import os
import json
import time
from dataclasses import dataclass
from typing import Tuple, List, Optional, Dict, Any
import requests
from math import radians, cos, sin, sqrt, atan2
from dotenv import load_dotenv

@dataclass
class GoogleAPIConfig:
    """Configuration for Google API endpoints and key."""
    api_key: str
    geocoding_url: str = "https://maps.googleapis.com/maps/api/geocode/json"
    places_url: str = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    details_url: str = "https://maps.googleapis.com/maps/api/place/details/json"

class GeoUtils:
    """Utility class for geographical calculations."""
    @staticmethod
    def calculate_midpoint(ne_lat: float, ne_lng: float, sw_lat: float, sw_lng: float) -> Tuple[float, float]:
        return (ne_lat + sw_lat) / 2, (ne_lng + sw_lng) / 2

    @staticmethod
    def haversine_distance(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        lat1, lng1, lat2, lng2 = map(radians, [lat1, lng1, lat2, lng2])
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlng / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        return 6371 * c * 1000  # Convert to meters

class BusinessCollector:
    """Main class for collecting business data."""
    def __init__(self, config: GoogleAPIConfig, type: str, districts: List[str], country: str):
        self.config = config
        self.type = type
        self.districts = districts
        self.country = country
        
    def get_district_info(self, district_name: str) -> Tuple[Optional[Tuple[float, float]], Optional[float]]:
        """Fetch district coordinates and radius."""
        params = {"address": f"{district_name}, {self.country}", "key": self.config.api_key}
        response = requests.get(self.config.geocoding_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching data for {district_name}: {response.status_code}")
            return None, None

        results = response.json().get("results", [])
        if not results:
            return None, None

        viewport = results[0]["geometry"]["viewport"]
        ne_lat, ne_lng = viewport["northeast"]["lat"], viewport["northeast"]["lng"]
        sw_lat, sw_lng = viewport["southwest"]["lat"], viewport["southwest"]["lng"]

        mid_lat, mid_lng = GeoUtils.calculate_midpoint(ne_lat, ne_lng, sw_lat, sw_lng)
        radius = GeoUtils.haversine_distance(mid_lat, mid_lng, ne_lat, ne_lng)
        return (mid_lat, mid_lng), radius
    
    def fetch_agency_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information for a specific agency."""
        params = {
            "place_id": place_id,
            "key": self.config.api_key
        }
        
        response = requests.get(self.config.details_url, params=params)
        if response.status_code != 200:
            print(f"Error fetching details for place_id {place_id}: {response.status_code}")
            return None

        details = response.json().get("result", {})
        if not details:
            return None

        # extract specific fields
        return {
            "name": details.get("name"),
            "formatted_address": details.get("formatted_address"),
            "international_phone_number": details.get("international_phone_number"),
            "url": details.get("url"),
            "website": details.get("website"),
            "rating": details.get("rating"),
            "user_ratings_total": details.get("user_ratings_total")
        }

    def fetch_agencies(self, lat: float, lng: float, radius: float) -> List[Dict[str, Any]]:
        """Fetch all agencies with detailed data."""
        agencies = []
        next_page_token = None

        while True:
            params = {
                "location": f"{lat},{lng}",
                "radius": radius,
                "type": self.type,
                "key": self.config.api_key
            }
            if next_page_token:
                params["pagetoken"] = next_page_token
                time.sleep(2)  # Avoid quota issues

            response = requests.get(self.config.places_url, params=params)
            if response.status_code != 200:
                print(f"Error fetching agencies: {response.status_code}")
                break

            data = response.json()
            for agency in data.get('results', []):
                place_id = agency.get("place_id")
                if place_id:
                    details = self.fetch_agency_details(place_id)
                    if details:
                        agencies.append(details)

            next_page_token = data.get("next_page_token")
            if not next_page_token:
                break

        return agencies


    def save_data(self, district: str, agencies: List[Dict[str, Any]]):
        """Save collected data to JSON."""
        # Create base directory inside scrape_businesses
        base_dir = os.path.join("scrape_businesses", self.type)
        os.makedirs(base_dir, exist_ok=True)
        
        # Create the file path
        filename = os.path.join(base_dir, f"{district.replace(' ', '_')}.json")
        
        # Save the data
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(agencies, f, ensure_ascii=False, indent=4)
        print(f"Saved data to {filename}")

    def collect_and_save_data(self):
        """Collect and save data for all districts."""
        for district in self.districts:
            coordinates, radius = self.get_district_info(district)
            if not coordinates or not radius:
                print(f"Skipping {district}: Failed to fetch coordinates")
                continue

            print(f"Processing {district}: {coordinates} (radius: {radius}m)")
            agencies = self.fetch_agencies(*coordinates, radius)
            print(f"Found {len(agencies)} agencies in {district}")
            self.save_data(district, agencies)

def main(districts, country, business_type):
    load_dotenv()
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
    config = GoogleAPIConfig(api_key=api_key)
    collector = BusinessCollector(config, business_type, districts, country)
    collector.collect_and_save_data()

