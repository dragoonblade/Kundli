"""Geocoding: location string to (lat, lon) coordinates."""
import json
import logging
import os
import uuid

from geopy.geocoders import Nominatim, Photon
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable

_CITIES_PATH = os.path.join(os.path.dirname(__file__), "cities.json")
with open(_CITIES_PATH) as _f:
    _BUILTIN_COORDS = {k: tuple(v) for k, v in json.load(_f).items()}

_geo_cache: dict = {}


def get_coordinates(location: str) -> tuple:
    """Geocode a location string to (lat, lon). Checks builtin cities, then Photon, then Nominatim."""
    normalized = location.strip().lower()
    if normalized in _BUILTIN_COORDS:
        logging.info(f"Geocode builtin: {location}")
        return _BUILTIN_COORDS[normalized]
    if normalized in _geo_cache:
        logging.info(f"Geocode cache hit: {location}")
        return _geo_cache[normalized]

    # Try Photon first (higher rate limit, no key needed)
    try:
        geo = Photon(user_agent="kundli_app", timeout=10)
        loc = geo.geocode(location)
        if loc:
            result = (loc.latitude, loc.longitude)
            _geo_cache[normalized] = result
            logging.info(f"Geocoded (Photon): {location} -> ({result[0]:.4f}, {result[1]:.4f})")
            return result
        logging.warning(f"Photon returned no results for: {location}")
    except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable) as e:
        logging.warning(f"Photon failed for: {location} ({e})")

    # Fallback to Nominatim
    try:
        geo = Nominatim(user_agent=f"kundli_app_{uuid.uuid4().hex[:6]}", timeout=10)
        loc = geo.geocode(location)
        if loc:
            result = (loc.latitude, loc.longitude)
            _geo_cache[normalized] = result
            logging.info(f"Geocoded (Nominatim): {location} -> ({result[0]:.4f}, {result[1]:.4f})")
            return result
        logging.warning(f"Nominatim returned no results for: {location}")
    except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable) as e:
        logging.error(f"Nominatim failed for: {location} ({e})")
    except (ValueError, AttributeError) as e:
        logging.error(f"Geocode unexpected error for: {location} ({e})")

    return None, None
