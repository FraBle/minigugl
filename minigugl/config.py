"""Settings management using pydantic."""
from typing import Optional, Union

from pydantic import BaseSettings


class Settings(BaseSettings):
    """All settings for minigugl.

    Values can be overridden with environment variables or a .env file.
    See: https://pydantic-docs.helpmanual.io/usage/settings/
    """

    debug: bool = False
    log_level: str = 'info'
    log_format: str = (
        '<level>{level: <8}</level> ' +
        '<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> ' +
        '<cyan>{name}</cyan>:<cyan>{function}</cyan> - ' +
        '<level>{message}</level>' +
        '{exception}\n'
    )
    video_width: int = 640
    video_height: int = 480
    video_framerate: int = 24
    video_source: str
    video_codec: str = 'libx264'
    video_segment_length_sec: int = 60
    output_dir: str
    enable_gps: bool = False
    gps_interval_sec: Union[float, int] = 0.1
    annotation_padding: int = 5
    annotation_margin: int = 5
    annotation_font_height: int = 15
    annotation_override_text_height: Optional[int]

    class Config(object):  # noqa: WPS431
        """Enable support to load settings from .env files."""

        env_file = '.env'


settings = Settings()
