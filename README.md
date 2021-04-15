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

```
poetry run python -m minigugl.client
```

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
