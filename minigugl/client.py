"""Video stream client for Raspberry Pi-powered dash cam."""
import io
import signal
import sys
import time
from pathlib import Path
from threading import Thread

import arrow
import cv2
from loguru import logger
from vidgear.gears import VideoGear, WriteGear

from minigugl import config
from minigugl.log import setup_logging

if config.settings.enable_gps:
    import gps  # noqa: WPS433

setup_logging(
    log_level=config.settings.log_level,
    log_format=config.settings.log_format,
)

opencv_options = {
    'CAP_PROP_FRAME_WIDTH': config.settings.video_width,
    'CAP_PROP_FRAME_HEIGHT': config.settings.video_height,
    'CAP_PROP_FPS': config.settings.video_framerate,
}
stream = VideoGear(
    source=config.settings.video_source,
    stabilize=True,
    logging=True,
    # colorspace='COLOR_BGR2RGB',
    **opencv_options,
).start()

# https://trac.ffmpeg.org/wiki/Encode/H.264
# https://www.ffmpeg.org/ffmpeg-all.html#Codec-Options
ffmpeg_options = {
    '-c:v': config.settings.video_codec,
    '-crf': 22,  # constant rate factor, decides quality
    '-map': 0,  # map all streams from the first input to output
    '-segment_time': config.settings.video_segment_length_sec,
    '-g': config.settings.video_framerate,  # group of picture (GOP) size = fps
    '-sc_threshold': 0,  # disable scene detection
    '-force_key_frames': 'expr:gte(t,n_forced*{0})'.format(
        # force key frame every x seconds
        config.settings.video_segment_length_sec,
    ),
    '-clones': ['-f', 'segment'],  # enable segment muxer
    '-preset': 'fast',  # preset option (encoding speed to compression ratio)
    '-tune': 'zerolatency',  # fast encoding and low-latency streaming
    '-input_framerate': config.settings.video_framerate,
    '-r': config.settings.video_framerate,  # output framerate
    '-pix_fmt': 'yuv420p',  # for output to work in QuickTime
    '-reset_timestamps': 1,  # reset timestamps at beginning of each segment
    '-strftime': 1,  # expand the segment filename with localtime
}
Path(config.settings.output_dir).mkdir(parents=True, exist_ok=True)
writer = WriteGear(
    # Example: video_2021-04-14_20-15-30.mp4
    # April 14th, 2021, at 8:15:30pm
    output_filename=str(
        Path(
            config.settings.output_dir,
        ) / 'video_%Y-%m-%d_%H-%M-%S.mp4',  # noqa: WPS323
    ),
    logging=True,
    **ffmpeg_options,
)

# Font setup for OpenCV
ft = cv2.freetype.createFreeType2()
font_file = Path(__file__).parent / 'fonts' / 'SourceCodePro-Regular.ttf'
ft.loadFontData(
    fontFileName=str(font_file),
    id=0,
)


def _signal_handler(signalnum: int, frame):
    """Handle signal from user interruption (e.g. CTRL+C).
    Logs and error message and exits with non-zero exit code.
    Args are ignored.
    Args:
        signalnum: Recevied signal number.
        frame: Current stack frame.
    """
    logger.info('Received signal: {0}', signal.Signals(signalnum).name)
    # safely close video stream & writer
    stream.stop()
    writer.close()
    sys.exit(0)


# Register handler for (keyboard) interrupts
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def _update_gps(gpsd: 'gps.gps', geo_coordinates: io.StringIO):
    """Update geo coordinates with gps data from gpsd.

    https://gpsd.gitlab.io/gpsd/gpsd_json.html#_tpv

    Args:
        gpsd: An instance of the GPS daemon interface.
        geo_coordinates: A StringIO buffer object.
    """
    while True:  # noqa: WPS457
        gps_data = next(gpsd)
        if gps_data.get('class') == 'TPV':
            latitude = getattr(gps_data, 'lat', 'N/A')
            longitude = getattr(gps_data, 'lon', 'N/A')
            if latitude and longitude:
                geo_coordinates.seek(0)
                geo_coordinates.write(
                    '{0}° | {1}°'.format(latitude, longitude),
                )
        time.sleep(config.settings.gps_interval_sec)


def _add_timestamp(img):
    font_height = 20
    thickness = -1
    text = arrow.now().format(arrow.FORMAT_RFC2822)
    (text_width, text_height) = ft.getTextSize(
        text,
        font_height,
        thickness,
    )[0]
    margin = 5
    padding = 5
    text_offset_x = 0 + padding + margin
    text_offset_y = img.shape[0] - padding - margin
    box_coords = (
        (
            text_offset_x - padding,
            text_offset_y + padding,
        ),
        (
            text_offset_x + text_width + padding,
            text_offset_y - text_height - padding,
        ),
    )
    overlay = img.copy()  # to allow opacity

    # Add background
    cv2.rectangle(
        overlay,
        box_coords[0],
        box_coords[1],
        (255, 255, 255),  # white background
        cv2.FILLED,
    )

    ft.putText(
        img=overlay,
        text=text,
        org=(text_offset_x, text_offset_y),
        fontHeight=font_height,
        color=(0, 0, 0),  # black text
        thickness=-1,
        line_type=cv2.LINE_AA,
        bottomLeftOrigin=True,
    )

    alpha = 0.7

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)


if __name__ == '__main__':
    if config.settings.enable_gps:
        # WATCH_ENABLE   # enable streaming
        # WATCH_NEWSTYLE # force JSON streaming
        gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        geo_coordinates = io.StringIO('N/A')
        gps_thread = Thread(
            target=_update_gps,
            args=(gpsd, geo_coordinates),
            daemon=True,
        )
        gps_thread.start()

    while True:
        # if config.settings.enable_gps:

        # read frames from stream
        frame = stream.read()

        # check for frame if None-type
        if frame is None:
            break

        if config.settings.enable_gps:
            logger.info('GPS: {0}', geo_coordinates.getvalue())

        # explicit conversion because of
        # https://github.com/opencv/opencv/issues/18120
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = _add_timestamp(img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        writer.write(img)
