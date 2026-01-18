# RankBias

Interactive web-based heatmap for visualizing football recruit rankings, now with live data from 247Sports.

## Overview

RankBias fetches the latest 2026 football recruit data from 247Sports and displays 4-star and 5-star recruits on an interactive map with heatmap visualization. No API keys required - uses free OpenStreetMap geocoding.

## Features

- 🏈 Live data scraping from 247Sports
- 🗺️ Interactive dark-themed map
- 🔥 Heatmap showing recruit concentration
- ⭐ 5-star recruits in gold, 4-star in purple
- 📍 Click markers to see recruit details
- 🌍 Automatic geocoding of recruit locations

## Installation

1. Install dependencies using `uv`:
```bash
cd RankBias
uv pip install flask requests beautifulsoup4
```

## Running the Application

Start the Flask development server:
```bash
uv run python app.py
```

Then open your browser to:
```
http://127.0.0.1:5000
```

The first load may take 1-2 minutes as it scrapes recruit data and geocodes locations. The app caches geocoding results for faster subsequent loads.

## How It Works

1. Scrapes 247Sports composite rankings page
2. Extracts recruit name, location, and star rating
3. Geocodes locations using Nominatim (OpenStreetMap)
4. Displays recruits on an interactive Leaflet.js map
5. Generates heatmap layer showing recruit concentration

## Files

- `app.py` - Flask server with scraping and geocoding logic
- `templates/index.html` - Interactive map frontend
- `requirements.txt` - Python dependencies

## Notes

- Only displays 4-star and 5-star recruits
- Geocoding is rate-limited to be respectful to free services
- Results are cached to improve performance
