# NASA Explorer API

A Flask API that wraps three NASA public APIs:
- 🌌 Astronomy Picture of the Day (APOD)
- 🔴 Mars Rover Photos
- ☄️ Near Earth Objects (Asteroids)

## Setup

```bash
pip install -r requirements.txt
```

Optionally set your own NASA API key (free at https://api.nasa.gov):
```bash
# Windows
set NASA_API_KEY=e9452143-127c-4c40-972c-8a8cb48cd332

# Mac/Linux
export NASA_API_KEY=your_key_here
```

If not set, the `DEMO_KEY` is used (30 requests/hour limit).

```bash
python app.py
```

Server runs at `http://127.0.0.1:5000`

---

## Endpoints

### 🏠 Home
**GET** `/`
Returns all available endpoints and their parameters.

---

### 🌌 Astronomy Picture of the Day
**GET** `/apod`

| Param | Type   | Required | Description              |
|-------|--------|----------|--------------------------|
| date  | string | No       | YYYY-MM-DD (default: today) |

```bash
# Today's picture
curl http://localhost:5000/apod

# Specific date
curl http://localhost:5000/apod?date=2024-01-15
```

**Response:**
```json
{
  "title": "The Andromeda Galaxy",
  "date": "2024-01-15",
  "explanation": "...",
  "media_type": "image",
  "url": "https://apod.nasa.gov/...",
  "hdurl": "https://apod.nasa.gov/...",
  "copyright": "NASA"
}
```

---

### 🔴 Mars Rover Photos
**GET** `/mars`

| Param  | Type   | Required | Description                                      |
|--------|--------|----------|--------------------------------------------------|
| rover  | string | No       | curiosity / opportunity / spirit (default: curiosity) |
| date   | string | No       | YYYY-MM-DD (default: 2023-01-01)                 |
| camera | string | No       | FHAZ, RHAZ, MAST, NAVCAM, etc.                   |

```bash
# Default (Curiosity, recent date)
curl http://localhost:5000/mars

# Specific rover and date
curl "http://localhost:5000/mars?rover=curiosity&date=2023-06-10"

# With camera filter
curl "http://localhost:5000/mars?rover=curiosity&date=2023-06-10&camera=NAVCAM"
```

**Cameras by rover:**
- **Curiosity**: FHAZ, RHAZ, MAST, CHEMCAM, MAHLI, MARDI, NAVCAM
- **Opportunity / Spirit**: FHAZ, RHAZ, NAVCAM, PANCAM, MINITES

---

### ☄️ Near Earth Objects
**GET** `/neo`

| Param | Type   | Required | Description                        |
|-------|--------|----------|------------------------------------|
| start | string | No       | YYYY-MM-DD (default: today)        |
| end   | string | No       | YYYY-MM-DD (default: today, max 7-day range) |

```bash
# Today's asteroids
curl http://localhost:5000/neo

# Date range
curl "http://localhost:5000/neo?start=2024-01-01&end=2024-01-05"
```

**Response:**
```json
{
  "start": "2024-01-01",
  "end": "2024-01-05",
  "total": 23,
  "asteroids": [
    {
      "name": "(2024 AB1)",
      "date": "2024-01-01",
      "diameter_km": { "min": 0.012, "max": 0.027 },
      "is_potentially_hazardous": false,
      "miss_distance_km": 1234567,
      "relative_velocity_kmh": 45000,
      "nasa_url": "https://ssd.jpl.nasa.gov/..."
    }
  ]
}
```


output:
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/60ae1391-8ffe-4df2-bd41-21e79b87d79d" />
