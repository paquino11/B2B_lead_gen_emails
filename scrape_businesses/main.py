import os
import json
import http.client
from dataclasses import dataclass
from typing import List, Dict, Any
import time

@dataclass
class SerperConfig:
    """Configuration for Serper API."""
    api_key: str
    host: str = "google.serper.dev"
    endpoint: str = "/places"

class BusinessCollector:
    """Main class for collecting business data."""
    def __init__(self, config: SerperConfig, business_type: str, city: str):
        self.config = config
        self.business_type = business_type
        self.city = city

    def fetch_businesses(self) -> List[Dict[str, Any]]:
        """Fetch businesses using Serper API."""
        conn = http.client.HTTPSConnection(self.config.host)
        
        # Construct search query
        search_query = f"{self.business_type} in {self.city}"
        
        payload = json.dumps({
            "q": search_query
        })
        
        headers = {
            'X-API-KEY': self.config.api_key,
            'Content-Type': 'application/json'
        }
        
        businesses = []
        try:
            conn.request("POST", self.config.endpoint, payload, headers)
            response = conn.getresponse()
            data = json.loads(response.read().decode("utf-8"))
            
            # Extract business data from response
            if "places" in data:
                businesses = data["places"]
            
        except Exception as e:
            print(f"Error fetching businesses: {str(e)}")
        finally:
            conn.close()
            
        return businesses

    def save_data(self, businesses: List[Dict[str, Any]]):
        """Save collected data to JSON."""
        # Create base directory inside scrape_businesses
        base_dir = os.path.join("scrape_businesses", "businesses")
        os.makedirs(base_dir, exist_ok=True)
        
        # Create the file path
        filename = os.path.join(base_dir, f"{self.city.replace(' ', '_')}_{self.business_type.replace(' ', '_')}.json")
        
        # Save the data
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(businesses, f, ensure_ascii=False, indent=4)
        print(f"Saved data to {filename}")

    def collect_and_save_data(self):
        """Collect and save business data."""
        print(f"Searching for {self.business_type} in {self.city}")
        businesses = self.fetch_businesses()
        print(f"Found {len(businesses)} businesses")
        self.save_data(businesses)

def main(city: str, business_type: str):
    api_key = os.getenv("SERPER_API_KEY", "51883a683a7ff0c0a8b3c7b1a0bccf1db2212573")  # Using provided API key as default
    
    config = SerperConfig(api_key=api_key)
    collector = BusinessCollector(config, business_type, city)
    collector.collect_and_save_data()

