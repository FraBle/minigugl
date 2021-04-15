"""Annotations for video frames."""
from pathlib import Path
from typing import Any, NamedTuple, Tuple

import cv2

from minigugl import config

Point = Tuple[int, int]
TextOrg = Point
BoxCoords = Tuple[Point, Point]


class AnnotationCoords(NamedTuple):
    """Wrapper class for annation coordinates."""

    text_org: TextOrg
    box_coords: BoxCoords


# Font setup for OpenCV
ft = cv2.freetype.createFreeType2()
font_file = Path(__file__).parent / 'fonts' / 'SourceCodePro-Regular.ttf'
ft.loadFontData(
    fontFileName=str(font_file),
    id=0,
)


def get_text_size(text: str) -> Tuple[int, int]:
    """Calculate text width and height based on font height.

    Args:
        text: Input text as string.

    Returns:
        Tuple representing text width and text height as integers.
    """
    return ft.getTextSize(
        text,
        config.settings.annotation_font_height,
        thickness=-1,
    )[0]


def get_bottom_left_coords(
    text_width: int,
    text_height: int,
    text_x: int,
    text_y: int,
) -> Tuple[TextOrg, BoxCoords]:
    """Get coordinates for text and background in bottom left corner.

    Args:
        text_width: Width of the text to be drawn.
        text_height: Height of the text to be drawn.
        text_x: X coordinate of the bottom-left corner of the text.
        text_y: Y coordinate of the bottom-left corner of the text.

    Returns:
        A tuple consisting of tuples for text point and text box coordinates.
    """
    text_offset_x = (
        text_x +
        config.settings.annotation_padding +
        config.settings.annotation_margin
    )
    text_offset_y = (
        text_y -
        config.settings.annotation_padding -
        config.settings.annotation_margin
    )
    box_coords = (
        (
            text_offset_x - config.settings.annotation_padding,
            text_offset_y + config.settings.annotation_padding,
        ),
        (
            text_offset_x + text_width + config.settings.annotation_padding,
            text_offset_y - text_height - config.settings.annotation_padding,
        ),
    )
    text_org = (text_offset_x, text_offset_y)
    return AnnotationCoords(text_org, box_coords)


def get_bottom_right_coords(
    text_width: int,
    text_height: int,
    text_x: int,
    text_y: int,
) -> Tuple[TextOrg, BoxCoords]:
    """Get coordinates for text and background in bottom right corner.

    Args:
        text_width: Width of the text to be drawn.
        text_height: Height of the text to be drawn.
        text_x: X coordinate of the bottom-right corner of the text.
        text_y: Y coordinate of the bottom-right corner of the text.

    Returns:
        A tuple consisting of tuples for text point and text box coordinates.
    """
    text_offset_x = (
        text_x -
        config.settings.annotation_padding -
        config.settings.annotation_margin
    )
    text_offset_y = (
        text_y -
        config.settings.annotation_padding -
        config.settings.annotation_margin
    )
    box_coords = (
        (
            text_offset_x - config.settings.annotation_padding,
            text_offset_y + config.settings.annotation_padding,
        ),
        (
            text_offset_x + text_width + config.settings.annotation_padding,
            text_offset_y - text_height - config.settings.annotation_padding,
        ),
    )
    text_org = (text_offset_x, text_offset_y)
    return AnnotationCoords(text_org, box_coords)


def get_top_left_coords(
    text_width: int,
    text_height: int,
    text_x: int,
    text_y: int,
) -> Tuple[TextOrg, BoxCoords]:
    """Get coordinates for text and background in top left corner.

    Args:
        text_width: Width of the text to be drawn.
        text_height: Height of the text to be drawn.
        text_x: X coordinate of the top-left corner of the text.
        text_y: Y coordinate of the top-left corner of the text.

    Returns:
        A tuple consisting of tuples for text point and text box coordinates.
    """
    text_offset_x = (
        text_x +
        config.settings.annotation_padding +
        config.settings.annotation_margin
    )
    text_offset_y = (
        text_y +
        config.settings.annotation_padding +
        config.settings.annotation_margin
    )
    box_coords = (
        (
            text_offset_x - config.settings.annotation_padding,
            text_offset_y + config.settings.annotation_padding,
        ),
        (
            text_offset_x + text_width + config.settings.annotation_padding,
            text_offset_y - text_height - config.settings.annotation_padding,
        ),
    )
    text_org = (text_offset_x, text_offset_y)
    return AnnotationCoords(text_org, box_coords)


def get_top_right_coords(
    text_width: int,
    text_height: int,
    text_x: int,
    text_y: int,
) -> Tuple[TextOrg, BoxCoords]:
    """Get coordinates for text and background in top right corner.

    Args:
        text_width: Width of the text to be drawn.
        text_height: Height of the text to be drawn.
        text_x: X coordinate of the top-right corner of the text.
        text_y: Y coordinate of the top-right corner of the text.

    Returns:
        A tuple consisting of tuples for text point and text box coordinates.
    """
    text_offset_x = (
        text_x -
        config.settings.annotation_padding -
        config.settings.annotation_margin
    )
    text_offset_y = (
        text_y +
        config.settings.annotation_padding +
        config.settings.annotation_margin
    )
    box_coords = (
        (
            text_offset_x - config.settings.annotation_padding,
            text_offset_y + config.settings.annotation_padding,
        ),
        (
            text_offset_x + text_width + config.settings.annotation_padding,
            text_offset_y - text_height - config.settings.annotation_padding,
        ),
    )
    text_org = (text_offset_x, text_offset_y)
    return AnnotationCoords(text_org, box_coords)


def add_text(
    frame: Any,
    text: str,
    text_org: TextOrg,
    box_coords: BoxCoords,
) -> None:
    """Draw text with background on an frame.

    Args:
        frame: Input frame as OpenCV image.
        text: Text to be drawn as string.
        text_org: Bottom-left corner of the text in the image as tuple of ints.
        box_coords: Box coordinates as tuple of points.
    """
    # Add background
    cv2.rectangle(
        img=frame,
        pt1=box_coords[0],
        pt2=box_coords[1],
        color=(255, 255, 255),  # white background
        thickness=cv2.FILLED,
    )
    ft.putText(
        img=frame,
        text=text,
        org=text_org,
        fontHeight=config.settings.annotation_font_height,
        color=(0, 0, 0),  # black text
        thickness=-1,
        line_type=cv2.LINE_AA,
        bottomLeftOrigin=True,
    )


def add_annotation_bottom_left(
    frame: Any,
    text: str,
) -> None:
    """Add text annotation to frame on bottom left.

    Args:
        frame: Input frame as OpenCV image.
        text: Text to be drawn as string.
    """
    (text_width, text_height) = get_text_size(text=text)
    text_org, box_coords = get_bottom_left_coords(
        text_width=text_width,
        text_height=text_height,
        text_x=0,
        text_y=frame.shape[0],
    )
    add_text(
        frame=frame,
        text=text,
        text_org=text_org,
        box_coords=box_coords,
    )


def add_annotation_bottom_right(
    frame: Any,
    text: str,
) -> None:
    """Add text annotation to frame on bottom right.

    Args:
        frame: Input frame as OpenCV image.
        text: Text to be drawn as string.
    """
    (text_width, text_height) = get_text_size(text=text)
    text_org, box_coords = get_bottom_right_coords(
        text_width=text_width,
        text_height=text_height,
        text_x=frame.shape[1] - text_width,
        text_y=frame.shape[0],
    )
    add_text(
        frame=frame,
        text=text,
        text_org=text_org,
        box_coords=box_coords,
    )


def add_annotation_top_left(
    frame: Any,
    text: str,
) -> None:
    """Add text annotation to frame on top left.

    Args:
        frame: Input frame as OpenCV image.
        text: Text to be drawn as string.
    """
    (text_width, text_height) = get_text_size(text=text)
    text_org, box_coords = get_top_left_coords(
        text_width=text_width,
        text_height=text_height,
        text_x=0,
        text_y=text_height,
    )
    add_text(
        frame=frame,
        text=text,
        text_org=text_org,
        box_coords=box_coords,
    )


def add_annotation_top_right(
    frame: Any,
    text: str,
) -> None:
    """Add text annotation to frame on top right.

    Args:
        frame: Input frame as OpenCV image.
        text: Text to be drawn as string.
    """
    (text_width, text_height) = get_text_size(text=text)
    text_org, box_coords = get_top_right_coords(
        text_width=text_width,
        text_height=text_height,
        text_x=frame.shape[1] - text_width,
        text_y=text_height,
    )
    add_text(
        frame=frame,
        text=text,
        text_org=text_org,
        box_coords=box_coords,
    )
