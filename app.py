from flask import Flask, render_template, jsonify
import requests
from bs4 import BeautifulSoup
import re
import json
import time

app = Flask(__name__)

# Simple geocoding cache to avoid repeated lookups
geocode_cache = {}

def geocode_location(location):
    """Geocode a location string to lat/lng using Nominatim (OpenStreetMap)"""
    if location in geocode_cache:
        return geocode_cache[location]
    
    try:
        # Use Nominatim geocoding service (free, no API key needed)
        url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
        headers = {'User-Agent': 'RankBias/1.0'}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                result = {'lat': float(data[0]['lat']), 'lng': float(data[0]['lon'])}
                geocode_cache[location] = result
                time.sleep(1)  # Rate limiting - be nice to the free service
                return result
    except Exception as e:
        print(f"Geocoding error for {location}: {e}")
    
    return None

def scrape_247sports():
    """Scrape recruit data from 247sports"""
    url = "https://247sports.com/season/2026-football/CompositeRecruitRankings/?InstitutionGroup=HighSchool"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        print(f"Fetching from: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Failed to fetch: HTTP {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, 'html.parser')
        recruits = []
        
        # Find recruit divs
        recruit_items = soup.find_all('div', class_='recruit')
        print(f"Found {len(recruit_items)} recruit divs")
        
        for idx, item in enumerate(recruit_items[:50]):
            try:
                print(f"\nProcessing recruit {idx}")
                
                # Extract name from the name link
                name = "Unknown"
                name_elem = item.find('a', class_='rankings-page__name-link')
                if name_elem:
                    name = name_elem.get_text(strip=True)
                    print(f"  Name: {name}")
                
                # Extract location from meta span
                location = ""
                meta_elem = item.find('span', class_='meta')
                if meta_elem:
                    meta_text = meta_elem.get_text(strip=True)
                    
                    # Extract city, state from parentheses like "(Spring, TX)"
                    match = re.search(r'\(([^)]+)\)', meta_text)
                    if match:
                        location = match.group(1).strip()
                        print(f"  Location: {location}")
                
                # Extract stars - count icon-starsolid yellow spans
                stars = 0
                # Look in parent or sibling elements for the rating div
                parent_li = item.find_parent('li')
                if parent_li:
                    rating_div = parent_li.find('div', class_='rating')
                    if rating_div:
                        star_spans = rating_div.find_all('span', class_='icon-starsolid yellow')
                        stars = len(star_spans)
                        print(f"  Stars: {stars}")
                
                # Only process 4-star and 5-star recruits
                if stars < 4:
                    print(f"  Skipping - only {stars} stars")
                    continue
                
                if location and name != "Unknown":
                    coords = geocode_location(location)
                    if coords:
                        recruits.append({
                            'name': name,
                            'location': location,
                            'lat': coords['lat'],
                            'lng': coords['lng'],
                            'stars': stars
                        })
                        print(f"  ✓ Added: {name} - {location} ({stars}⭐)")
                else:
                    print(f"  Skipping - missing data")
                
                if location:
                    coords = geocode_location(location)
                    if coords:
                        recruits.append({
                            'name': name,
                            'location': location,
                            'lat': coords['lat'],
                            'lng': coords['lng'],
                            'stars': stars
                        })
                        print(f"Added: {name} - {location} ({stars}★)")
                
            except Exception as e:
                print(f"Error processing recruit item: {e}")
                continue
        
        return recruits
        
    except Exception as e:
        print(f"Scraping error: {e}")
        return []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/data')
def get_data():
    """Fetch recruit data from 247sports"""
    print("Fetching recruit data from 247sports...")
    locations = scrape_247sports()
    
    if not locations:
        # Return sample data if scraping fails
        print("Using sample data")
        return jsonify({
            'locations': [
                {'name': 'Sample Recruit 1', 'location': 'Los Angeles, CA', 'lat': 34.0522, 'lng': -118.2437, 'stars': 5},
                {'name': 'Sample Recruit 2', 'location': 'Miami, FL', 'lat': 25.7617, 'lng': -80.1918, 'stars': 5},
                {'name': 'Sample Recruit 3', 'location': 'Dallas, TX', 'lat': 32.7767, 'lng': -96.7970, 'stars': 5},
            ]
        })
    
    print(f"Returning {len(locations)} recruits")
    return jsonify({'locations': locations})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
