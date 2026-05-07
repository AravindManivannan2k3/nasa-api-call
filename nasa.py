import requests
import os

NASA_API_KEY = os.getenv("NASA_API_KEY", "DEMO_KEY")
BASE_URL = "https://api.nasa.gov"


def _get(url, params=None):
    """Shared GET helper — attaches API key and handles errors."""
    if params is None:
        params = {}
    params["api_key"] = NASA_API_KEY
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json(), resp.status_code
    except requests.exceptions.HTTPError as e:
        return {"error": str(e), "details": resp.text}, resp.status_code
    except requests.exceptions.RequestException as e:
        return {"error": "Failed to reach NASA API", "details": str(e)}, 503


# ─────────────────────────────────────────────
# APOD
# ─────────────────────────────────────────────
def get_apod(date=None):
    """
    Fetch Astronomy Picture of the Day.
    date: YYYY-MM-DD (optional, defaults to today)
    """
    params = {}
    if date:
        params["date"] = date

    data, status = _get(f"{BASE_URL}/planetary/apod", params)
    if status != 200:
        return data, status

    return {
        "title":       data.get("title"),
        "date":        data.get("date"),
        "explanation": data.get("explanation"),
        "media_type":  data.get("media_type"),
        "url":         data.get("url"),
        "hdurl":       data.get("hdurl"),
        "copyright":   data.get("copyright", "NASA"),
    }, 200


# ─────────────────────────────────────────────
# Mars Rover Photos
# ─────────────────────────────────────────────
VALID_ROVERS  = {"curiosity", "opportunity", "spirit"}
VALID_CAMERAS = {
    "curiosity":    ["FHAZ", "RHAZ", "MAST", "CHEMCAM", "MAHLI", "MARDI", "NAVCAM"],
    "opportunity":  ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"],
    "spirit":       ["FHAZ", "RHAZ", "NAVCAM", "PANCAM", "MINITES"],
}

def get_mars_photos(rover="curiosity", date="2023-01-01", camera=None):
    """
    Fetch Mars rover photos.
    rover:  curiosity | opportunity | spirit
    date:   earth date YYYY-MM-DD
    camera: optional camera filter
    """
    rover = rover.lower()
    if rover not in VALID_ROVERS:
        return {"error": f"Invalid rover. Choose from: {', '.join(VALID_ROVERS)}"}, 400

    params = {"earth_date": date}
    if camera:
        camera = camera.upper()
        allowed = VALID_CAMERAS.get(rover, [])
        if camera not in allowed:
            return {
                "error": f"Invalid camera '{camera}' for {rover}.",
                "valid_cameras": allowed
            }, 400
        params["camera"] = camera

    data, status = _get(f"{BASE_URL}/mars-photos/api/v1/rovers/{rover}/photos", params)
    if status != 200:
        return data, status

    photos = data.get("photos", [])
    if not photos:
        return {
            "message": "No photos found for this date/camera combination. Try a different date.",
            "rover":  rover,
            "date":   date,
            "photos": []
        }, 200

    return {
        "rover":       rover,
        "date":        date,
        "total":       len(photos),
        "photos": [
            {
                "id":       p["id"],
                "camera":   p["camera"]["full_name"],
                "img_url":  p["img_src"],
                "sol":      p["sol"],
            }
            for p in photos[:20]   # cap at 20 to keep response manageable
        ]
    }, 200


# ─────────────────────────────────────────────
# Near Earth Objects
# ─────────────────────────────────────────────
def get_neo(start=None, end=None):
    """
    Fetch Near Earth Objects (asteroids) for a date range.
    start/end: YYYY-MM-DD (max 7-day window)
    """
    from datetime import date, timedelta, datetime

    today = date.today().isoformat()
    if not start:
        start = today
    if not end:
        end = today

    # Validate date range (NASA enforces max 7 days)
    try:
        d1 = datetime.strptime(start, "%Y-%m-%d").date()
        d2 = datetime.strptime(end,   "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400

    if (d2 - d1).days > 7:
        return {"error": "Date range cannot exceed 7 days."}, 400

    data, status = _get(f"{BASE_URL}/neo/rest/v1/feed", {
        "start_date": start,
        "end_date":   end,
    })
    if status != 200:
        return data, status

    all_neos = []
    for date_key, neos in data.get("near_earth_objects", {}).items():
        for neo in neos:
            close_approach = neo.get("close_approach_data", [{}])[0]
            all_neos.append({
                "name":                neo.get("name"),
                "date":                date_key,
                "diameter_km": {
                    "min": round(neo["estimated_diameter"]["kilometers"]["estimated_diameter_min"], 4),
                    "max": round(neo["estimated_diameter"]["kilometers"]["estimated_diameter_max"], 4),
                },
                "is_potentially_hazardous": neo.get("is_potentially_hazardous_asteroid"),
                "miss_distance_km":    round(float(close_approach.get("miss_distance", {}).get("kilometers", 0))),
                "relative_velocity_kmh": round(float(close_approach.get("relative_velocity", {}).get("kilometers_per_hour", 0))),
                "nasa_url":            neo.get("nasa_jpl_url"),
            })

    all_neos.sort(key=lambda x: x["miss_distance_km"])

    return {
        "start":       start,
        "end":         end,
        "total":       data.get("element_count", len(all_neos)),
        "asteroids":   all_neos,
    }, 200
