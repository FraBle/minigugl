"""Video stream client for Raspberry Pi-powered dash cam."""
import signal
import sys
from pathlib import Path
from typing import Any, Optional

import arrow
import cv2
from loguru import logger
from vidgear.gears import VideoGear, WriteGear

from minigugl import annotation, config
from minigugl.log import setup_logging

if config.settings.enable_gps:
    from minigugl import location  # noqa: WPS433

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
    # use `-clones` for `-f` parameter since WriteGear internally applies
    # critical '-f rawvideo' parameter to every FFmpeg pipeline
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


def _signal_handler(signalnum: int, _: Any) -> None:
    """Handle signal from user interruption (e.g. CTRL+C).

    Logs an error message and exits with non-zero exit code. Args are ignored.

    Args:
        signalnum: Recevied signal number.
    """
    logger.info('Received signal: {0}', signal.Signals(signalnum).name)
    # safely close video stream & writer
    stream.stop()
    writer.close()
    sys.exit(0)


# Register handler for (keyboard) interrupts
signal.signal(signal.SIGINT, _signal_handler)
signal.signal(signal.SIGTERM, _signal_handler)


def _add_text_annotations(
    img: Any,
    top_left: Optional[str] = None,
    top_right: Optional[str] = None,
    bottom_left: Optional[str] = None,
    bottom_right: Optional[str] = None,
) -> Any:
    if not any([top_left, top_right, bottom_left, bottom_right]):
        return img

    alpha = 0.7  # opacity level
    overlay = img.copy()  # to allow opacity
    override_text_height = config.settings.annotation_override_text_height

    if top_left:
        annotation.add_annotation_top_left(
            frame=overlay,
            text=top_left,
            override_text_height=override_text_height,
        )
    if top_right:
        annotation.add_annotation_top_right(
            overlay,
            top_right,
            override_text_height=override_text_height,
        )
    if bottom_left:
        annotation.add_annotation_bottom_left(
            overlay,
            bottom_left,
            override_text_height=override_text_height,
        )
    if bottom_right:
        annotation.add_annotation_bottom_right(
            overlay,
            bottom_right,
            override_text_height=override_text_height,
        )

    return cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)


if __name__ == '__main__':
    if config.settings.enable_gps:
        gps_coordinates = location.start_gps_thread()

    while True:
        frame = stream.read()  # read frames from stream

        # check for frame if None-type
        if frame is None:
            break

        # explicit conversion of color space because of
        # https://github.com/opencv/opencv/issues/18120
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # add text annotations: timestamp and optionally GPS coordinates
        img = _add_text_annotations(
            img,
            bottom_left=arrow.now().format(arrow.FORMAT_RFC2822),
            bottom_right=(
                str(gps_coordinates)
                if config.settings.enable_gps
                else None
            ),
        )

        # conversion back to original color space
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

        writer.write(img)
