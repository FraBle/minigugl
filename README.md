<p align="center">
  <img src="docs/minigugl.jpg" alt="minigugl" width="50%"/></br>
  Photo by <a href="https://pixabay.com/users/einladung_zum_essen-3625323/" target="_blank">Bernadette Wurzinger</a>
</p>

<h1 align="center">minigugl</h1>

<div align="center">

[![Travis CI][travis-badge]][travis-url]
[![Codacy][codacy-badge]][codacy-url]
[![Code Climate][code-climate-badge]][code-climate-url]
[![CodeFactor][codefactor-badge]][codefactor-url]
[![lgtm][lgtm-badge]][lgtm-url]
[![SonarQube][sonarqube-badge]][sonarqube-url]

</div>

`minigugl` is a little video streaming client to read an MJPEG video stream and store it in chunks (segments) locally as H.264-encoded video files. It's highly configurable and the perfect little helper to continuously record videos to file (e.g., for dashcams or security cameras).

## Prerequisites

This project uses [`poetry`](https://python-poetry.org/docs/) for Python dependency management and requires Python `3.6.1+`, but no newer than Python `3.7.x` due to its dependencies. [`pyenv`](https://github.com/pyenv/pyenv) is a great tool to manage different Python versions.  
It furthermore requires [`FFmpeg` for video encoding/decoding](https://abhitronix.github.io/vidgear/latest/gears/writegear/compression/advanced/ffmpeg_install/).

## Components

`minigugl` uses the fantastic Python video processing framework called [`vidgear`](https://abhitronix.github.io/vidgear) to read an MJPEG stream with [`VideoGear`](https://abhitronix.github.io/vidgear/latest/gears/videogear/overview/) and process it through FFmpeg with [`WriteGear`](https://abhitronix.github.io/vidgear/latest/gears/writegear/introduction/).
Video frames are augmented with text using [OpenCV](https://opencv.org/). This includes timestamps using [`arrow`](https://arrow.readthedocs.io/en/latest/) and optionally GPS coordinates using [`gpsd`](https://gitlab.com/gpsd/gpsd), e.g., using a Globalsat BU-353S4 GPS USB Receiver.

## Installation

1. Clone the GitHub repo: `git clone git@github.com:FraBle/minigugl.git`
2. Inside `minigugl` directory, run `poetry install --no-root` to install dependencies.  
   - Use `poetry install --no-root --extras gps` to install it with GPS tooling.

## Configuration

`minigugl` uses [`pydantic's settings management`](https://pydantic-docs.helpmanual.io/usage/settings/) and provides defaults for all parameters except `OUTPUT_DIR` and `VIDEO_SOURCE`.  
The following parameters can be passed in as environment variables. Alternatively, you can [use a `.env` file](https://pydantic-docs.helpmanual.io/usage/settings/#dotenv-env-support) as well.

| Environment Variable       | Type             | Required | Default     |
|----------------------------|------------------|----------|-------------|
| `OUTPUT_DIR`               | `str`            | Yes      |             |
| `VIDEO_SOURCE`             | `str`            | Yes      |             |
| `DEBUG`                    | `bool`           | No       | `False`     |
| `LOG_FORMAT`               | `str`            | No       | _provided_  |
| `LOG_LEVEL`                | `str`            | No       | `"info"`    |
| `ENABLE_GPS`               | `bool`           | No       | `False`     |
| `GPS_INTERVAL_SEC`         | `float` or `int` | No       | `0.1`       |
| `ANNOTATION_FONT_HEIGHT`   | `int`            | No       | `15`        |
| `ANNOTATION_MARGIN`        | `int`            | No       | `5`         |
| `ANNOTATION_PADDING`       | `int`            | No       | `5`         |
| `VIDEO_CODEC`              | `str`            | No       | `"libx264"` |
| `VIDEO_FRAMERATE`          | `int`            | No       | `24`        |
| `VIDEO_HEIGHT`             | `int`            | No       | `480`       |
| `VIDEO_SEGMENT_LENGTH_SEC` | `int`            | No       | `60`        |
| `VIDEO_WIDTH`              | `int`            | No       | `640`       |

## Running `minigugl`

With all required environment variables set, execute the following code inside the repo directory to start the video streaming client:

```bash
poetry run python -m minigugl.client
```

## Additional Resources

### Setting up Real Time Streaming Protocol (RTSP) server on a Raspberry Pi as video source

> Based on
>
> - [https://github.com/mpromonet/v4l2rtspserver/wiki/Setup-on-Pi](https://github.com/mpromonet/v4l2rtspserver/wiki/Setup-on-Pi)
> - [https://gist.github.com/brutella/a71e8d7aa90af2c53ab500c4125bc178](https://gist.github.com/brutella/a71e8d7aa90af2c53ab500c4125bc178)

1. Install `v4l2rtspserver`

    ```bash
    sudo apt install -y cmake liblog4cpp5-dev libv4l-dev
    cd /tmp
    git clone https://github.com/mpromonet/v4l2rtspserver.git
    cd v4l2rtspserver/
    cmake .
    make
    sudo make install
    ```

2. Install `v4l-utils` for debugging & control commands

    ```bash
    sudo apt install v4l-utils
    ```

    Example "rotatation of camera":

    ```bash
    v4l2-ctl --set-ctrl=rotate=90
    ```

3. (For full automation) Add `v4l2-ctl` command to system by boot via `udev` subsystem

    `sudo nano /etc/udev/rules.d/99-local-webcam.rules`:

    ```plain
    SUBSYSTEM=="video4linux", PROGRAM="/usr/bin/v4l2-ctl --set-ctrl=rotate=90"
    ```

4. Load open source V4L2 driver `bcm2835-v4l2`

    ```bash
    sudo modprobe -v bcm2835-v4l2 max_video_width=640 max_video_height=480
    ```

5. Add `bcm2835-v4l2` to `/etc/modules` (kernel modules to load at boot time)

    ```bash
    sudo nano /etc/modules
    # Add "bcm2835-v4l2 max_video_width=640 max_video_height=480" to the end of the file
    ```

6. Test the setup by starting `v4l2rtspserver` with open source V4L2 driver `bcm2835-v4l2`

    > [Parameters for `bcm2835-v4l2`](https://github.com/torvalds/linux/blob/master/drivers/staging/vc04_services/bcm2835-camera/bcm2835-camera.c)

    ```bash
    v4l2rtspserver -W640 -H480 -F30 -P8555 /dev/video0
    ```

7. Testing H264 RTSP video stream, e.g. with VLC from a MacBook

    ```bash
    vlc rtsp://<rpi-ip>:8555/unicast
    ```

8. (For full automation) Add `v4l2rtspserver` start-up script

    Create start-up script: `sudo nano /usr/local/bin/start-rtsp-server`

    ```bash
    #!/bin/bash
    v4l2rtspserver -W640 -H480 -F30 -P8555 /dev/video0
    ```

    Add execution rights with `sudo chmod +x /usr/local/bin/start-rtsp-server`.

9. (For full automation) Add `v4l2rtspserver` to systemd

    Create systemd entry: `sudo nano /lib/systemd/system/v4l2rtspserver.service`

    ```ini
    [Unit]
    Description=V4L2 RTSP server
    After=network.target

    [Service]
    Type=simple
    ExecStart=/usr/local/bin/start-rtsp-server
    Restart=always
    RestartSec=1
    StartLimitIntervalSec=0

    [Install]
    WantedBy=multi-user.target
    ```

    Enable `v4l2rtspserver.service`

    ```bash
    sudo systemctl daemon-reload
    sudo systemctl enable v4l2rtspserver.service
    sudo systemctl start v4l2rtspserver.service
    ```

10. (For full automation) Reboot Raspberry Pi and confirm everything starts automatically

    ```bash
    sudo reboot
    ```

    Open H264 RTSP video stream, e.g. with VLC from a MacBook:

    ```bash
    vlc rtsp://<rpi-ip>:8555/unicast
    ```

### Starting `gpsd` on Raspberry Pi for Globalsat BU-353S4

1. Install `gpsd` packages

    ```bash
    apt install gpsd gpsd-clients
    ```

2. Edit gpsd config (setting `DEVICES`, `GPSD_OPTIONS`, and `GPSD_SOCKET`)

    ```bash
    nano /etc/default/gpsd
    ```

    `/etc/default/gpsd` for reference:

    ```plain
    # Default settings for the gpsd init script and the hotplug wrapper.

    # Start the gpsd daemon automatically at boot time
    START_DAEMON="true"

    # Use USB hotplugging to add new USB devices automatically to the daemon
    USBAUTO="true"

    # Devices gpsd should collect to at boot time.
    # They need to be read/writeable, either by user gpsd or the group dialout.
    DEVICES="/dev/ttyUSB0"

    # Other options you want to pass to gpsd
    # "-n: Don't wait for a client to connect before polling whatever GPS is associated with it."
    GPSD_OPTIONS="-n"
    GPSD_SOCKET="/var/run/gpsd.sock"
    ```

3. Enable the gpsd service

    ```bash
    systemctl enable gpsd.socket
    systemctl start gpsd.socket
    ```

4. Verify GPS connection by running `gpsmon` and/or `cgps`

<!--
Badges
-->
[travis-badge]:https://img.shields.io/travis/com/FraBle/minigugl?label=Travis%20CI%20Build&style=flat-square
[codacy-badge]:https://img.shields.io/codacy/grade/1e536b353e83451a968db54f7f230bf3?label=Codacy%20Grade&style=flat-square
[code-climate-badge]:https://img.shields.io/codeclimate/maintainability/FraBle/minigugl?label=Code%20Climate%20Grade&style=flat-square
[codefactor-badge]:https://img.shields.io/codefactor/grade/github/FraBle/minigugl/main?label=CodeFactor%20Grade&style=flat-square
[lgtm-badge]:https://img.shields.io/lgtm/grade/python/github/FraBle/minigugl?label=lgtm%20Grade&style=flat-square
[sonarqube-badge]:https://img.shields.io/sonar/tech_debt/minigugl?label=Sonar%20Tech%20Debt&server=https%3A%2F%2Fsonarcloud.io&style=flat-square

<!--
Badge URLs
-->
[travis-url]:https://travis-ci.com/FraBle/minigugl
[codacy-url]:https://app.codacy.com/gh/FraBle/minigugl
[code-climate-url]:https://codeclimate.com/github/FraBle/minigugl
[codefactor-url]:https://www.codefactor.io/repository/github/frable/minigugl
[lgtm-url]:https://lgtm.com/projects/g/FraBle/minigugl/
[sonarqube-url]:https://sonarcloud.io/dashboard?id=minigugl
