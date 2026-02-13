"""API configuration and helper utilities for external APIs."""

import os

import requests
from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """Configuration for external APIs."""

    # Serper API (Google Search + Places)
    SERPER_API_KEY: str | None = os.getenv("SERPER_API_KEY")
    SERPER_BASE_URL = "https://google.serper.dev/search"
    SERPER_PLACES_URL = "https://google.serper.dev/places"

    # OpenStreetMap Nominatim (no key needed)
    NOMINATIM_BASE_URL = "https://nominatim.openstreetmap.org"
    NOMINATIM_USER_AGENT = "BizLaunch-AI/1.0 (Educational POC)"

    # Overpass API (no key needed)
    OVERPASS_BASE_URL = "https://overpass-api.de/api/interpreter"

    # Data Commons (no key needed for basic queries)
    DATA_COMMONS_BASE_URL = "https://datacommons.org/api"

    # Request timeout
    REQUEST_TIMEOUT = 10


def make_request(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = APIConfig.REQUEST_TIMEOUT,
) -> dict | None:
    """Make HTTP GET request with error handling.

    Args:
        url: Request URL
        params: Query parameters
        headers: Request headers
        timeout: Request timeout in seconds

    Returns:
        JSON response or None if request failed
    """
    try:
        response = requests.get(url, params=params, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None


def geocode_location(location: str) -> tuple[float, float] | None:
    """Geocode a location string to coordinates using Nominatim.

    Args:
        location: Location string (e.g., "Nueva Córdoba, Córdoba, Argentina")

    Returns:
        Tuple of (latitude, longitude) or None if geocoding failed
    """
    url = f"{APIConfig.NOMINATIM_BASE_URL}/search"
    params = {
        "q": f"{location}, Córdoba, Argentina",
        "format": "json",
        "limit": 1,
    }
    headers = {"User-Agent": APIConfig.NOMINATIM_USER_AGENT}

    data = make_request(url, params=params, headers=headers)

    if data and len(data) > 0:
        return float(data[0]["lat"]), float(data[0]["lon"])
    return None


def reverse_geocode(lat: float, lon: float) -> dict | None:
    """Reverse geocode coordinates to address using Nominatim.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Address data or None if reverse geocoding failed
    """
    url = f"{APIConfig.NOMINATIM_BASE_URL}/reverse"
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
    }
    headers = {"User-Agent": APIConfig.NOMINATIM_USER_AGENT}

    return make_request(url, params=params, headers=headers)
