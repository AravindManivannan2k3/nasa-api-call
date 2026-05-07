from flask import Flask, jsonify, request
from nasa import get_apod, get_mars_photos, get_neo
import os

app = Flask(__name__)


# ─────────────────────────────────────────────
# Home
# ─────────────────────────────────────────────
@app.route("/")
def home():
    return jsonify({
        "message": "NASA Explorer API",
        "endpoints": {
            "GET /apod":               "Astronomy Picture of the Day",
            "GET /mars":               "Mars Rover Photos",
            "GET /neo":                "Near Earth Objects (Asteroids)",
        },
        "params": {
            "/apod":  "?date=YYYY-MM-DD (optional)",
            "/mars":  "?rover=curiosity&date=YYYY-MM-DD&camera=FHAZ (all optional)",
            "/neo":   "?start=YYYY-MM-DD&end=YYYY-MM-DD (optional, max 7-day range)",
        }
    })


# ─────────────────────────────────────────────
# APOD — Astronomy Picture of the Day
# ─────────────────────────────────────────────
@app.route("/apod")
def apod():
    date = request.args.get("date")          # e.g. 2024-01-15
    result, status = get_apod(date=date)
    return jsonify(result), status


# ─────────────────────────────────────────────
# Mars Rover Photos
# ─────────────────────────────────────────────
@app.route("/mars")
def mars():
    rover  = request.args.get("rover", "curiosity")   # curiosity | opportunity | spirit
    date   = request.args.get("date", "2023-01-01")   # earth date
    camera = request.args.get("camera")               # FHAZ, RHAZ, MAST, CHEMCAM, etc.
    result, status = get_mars_photos(rover=rover, date=date, camera=camera)
    return jsonify(result), status


# ─────────────────────────────────────────────
# Near Earth Objects
# ─────────────────────────────────────────────
@app.route("/neo")
def neo():
    from datetime import date
    today = date.today().isoformat()
    start = request.args.get("start", today)
    end   = request.args.get("end",   today)
    result, status = get_neo(start=start, end=end)
    return jsonify(result), status


if __name__ == "__main__":
    app.run(debug=True)
