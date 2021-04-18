"""Integration with gpsd through separate thread."""
import math
from threading import Lock, Thread
from time import sleep

import gps

from minigugl import config


class GpsCoordinates(object):
    """Thread-safe wrapper for GPS coordinates (latitude/longitude).

    Attributes:
        lat: GPS latitude.
        lon: GPS longitude.
    """

    def __init__(self) -> None:
        """Initialize latitude, longitude, and internal lock."""
        self._lock = Lock()
        self.lat: float = 0
        self.lon: float = 0

    def update(self, lat: float, lon: float) -> None:
        """Thread-safe update of latitude & longitude.

        Args:
            lat: GPS latitude.
            lon: GPS longitude.
        """
        self._lock.acquire()
        self.lat = lat
        self.lon = lon
        self._lock.release()

    def __str__(self) -> str:
        """Thread-safe string representation in DMS.

        DMS = degrees, minutes, and seconds

        Returns:
            DMS-converted GPS coordinates.
        """
        self._lock.acquire()
        dms = '{0} {1}'.format(
            deg_to_dms(self.lat, unit='lat'),
            deg_to_dms(self.lon, unit='lon'),
        )
        self._lock.release()
        return dms


def deg_to_dms(deg: float, unit: str) -> str:  # noqa: WPS210
    """Convert decimal degrees to DMS.

    Based on https://stackoverflow.com/a/52371976
    DMS = degrees, minutes, and seconds

    Args:
        deg: Degree in decimal
        unit: Coordinates unit ('lat' or 'lon')

    Returns:
        DMS-converted GPS coordinates as string.
    """
    decimals, number = math.modf(deg)
    degrees = int(number)
    minutes = int(decimals * 60)
    seconds = (deg - degrees - minutes / 60) * 60 * 60
    compass = {
        'lat': ('N', 'S'),
        'lon': ('E', 'W'),
    }
    return '{0}°{1:02}\'{2:04.1f}"{3}'.format(
        abs(degrees),
        abs(minutes),
        abs(seconds),
        compass[unit][0 if degrees >= 0 else 1],
    )


def _update_gps(gpsd: 'gps.gps', gps_coordinates: GpsCoordinates) -> None:
    """Update geo coordinates with gps data from gpsd.

    https://gpsd.gitlab.io/gpsd/gpsd_json.html#_tpv

    Args:
        gpsd: An instance of the GPS daemon interface.
        gps_coordinates: A GpsCoordinates instance.
    """
    while True:  # noqa: WPS457
        gps_data = next(gpsd)
        if gps_data.get('class') == 'TPV':
            gps_coordinates.update(
                gps_data.get('lat'),
                gps_data.get('lon'),
            )
        sleep(config.settings.gps_interval_sec)


def start_gps_thread() -> GpsCoordinates:
    """Start separate thread to process gpsd data.

    Returns:
        An instance of GpsCoordinates which gets continously updated.
    """
    # WATCH_ENABLE   # enable streaming
    # WATCH_NEWSTYLE # force JSON streaming
    gpsd = gps.gps(mode=gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
    gps_coordinates = GpsCoordinates()
    gps_thread = Thread(
        target=_update_gps,
        args=(gpsd, gps_coordinates),
        daemon=True,
    )
    gps_thread.start()
    return gps_coordinates
