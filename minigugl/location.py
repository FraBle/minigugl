"""Integration with gpsd through separate thread."""
from threading import Lock, Thread
from time import sleep

import gps
from LatLon3.LatLon import LatLon

from minigugl import config


class GpsCoordinates(object):
    """Thread-safe wrapper for GPS coordinates (latitude/longitude).

    Attributes:
        lat: GPS latitude.
        lon: GPS longitude.
    """

    def __init__(self):
        """Initialize latitude, longitude, and internal lock."""
        self._lock = Lock()
        self.lat: float = 0
        self.lon: float = 0

    def update(self, lat, lon):
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
        latlon = LatLon(self.lat, self.lon)
        self._lock.release()
        lat_deg, lon_deg = latlon.to_string(
            'd%°%m%\'%S%"%H',
            n_digits_seconds=1,
        )
        # Fill up string to 13 characters for lat/lon to maintain same length
        return '{0:>13} {1:>13}'.format(lat_deg, lon_deg)


def _update_gps(gpsd: 'gps.gps', gps_coordinates: GpsCoordinates):
    """Update geo coordinates with gps data from gpsd.

    https://gpsd.gitlab.io/gpsd/gpsd_json.html#_tpv

    Args:
        gpsd: An instance of the GPS daemon interface.
        gps_coordinates: A GpsCoordinates instance.
    """
    while True:  # noqa: WPS457
        gps_data = next(gpsd)
        if gps_data.get('class') == 'TPV':
            gps_coordinates.update(gps_data.lat, gps_data.lon)
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
