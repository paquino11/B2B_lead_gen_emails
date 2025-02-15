#!/usr/bin/env python
import sys
import warnings
import json
import os
from datetime import datetime
from pathlib import Path

from get_info_business.crew import GetInfoBusiness

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

def get_project_root():
    """Get the path to the project root directory."""
    current_path = Path(__file__).resolve()
    
    # Go up until we find the root directory (where app.py is)
    while current_path.parent != current_path:
        if (current_path / "app.py").exists():
            return current_path
        current_path = current_path.parent
    
    # If we can't find the root, use the parent of get_info_business
    return Path(__file__).resolve().parent.parent.parent.parent.parent

def load_business_data(business_type):
    """Load business data from JSON files in scrape_businesses directory."""
    project_root = get_project_root()
    base_path = project_root / "scrape_businesses" / "businesses"
    
    if not base_path.exists():
        raise Exception(f"Directory not found: {base_path}")
    
    all_businesses = []
    
    for file_path in base_path.glob("*.json"):
        print(f"Reading file: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            try:
                businesses = json.load(f)
                if isinstance(businesses, list):
                    all_businesses.extend(businesses)
                else:
                    all_businesses.append(businesses)
            except json.JSONDecodeError as e:
                print(f"Error reading {file_path}: {e}")
    
    if not all_businesses:
        raise Exception(f"No businesses found in {base_path}")
    
    return all_businesses

def append_to_results(business_data):
    """Append business data to results.json file."""
    project_root = get_project_root()
    results_file = project_root / 'results.json'
    
    print(f"\nResults will be saved to: {results_file.absolute()}\n")
    
    # Create directory if it doesn't exist
    results_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing results or create empty list
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
            except json.JSONDecodeError:
                results = []
    else:
        results = []
    
    # Check if business already exists in results
    business_exists = any(b.get('title') == business_data.get('title') for b in results)
    
    if not business_exists:
        # Append new data
        results.append(business_data)
        
        # Write back to file
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=4, ensure_ascii=False)

def process_business(business, business_type):
    """Process a single business."""
    try:
        inputs = {
            'business_type': business_type,
            'business_name': business['title'],
            'business_address': business['address'],
            'business_website': business.get('website', 'Not available'),
            'business_about': business.get('about', ''),
            'current_year': str(datetime.now().year)
        }
        
        crew = GetInfoBusiness()
        result = crew.crew().kickoff(inputs=inputs)
        
        # Convert CrewOutput to string if necessary
        if hasattr(result, 'raw_output'):
            result_data = json.loads(result.raw_output)
        else:
            result_data = json.loads(str(result))
            
        # Combine all data
        complete_data = {**business, **result_data}
        
        # Append to results.json
        append_to_results(complete_data)
        return complete_data
        
    except Exception as e:
        print(f"Error processing business {business['title']}: {e}")
        return business

def run():
    """Run the crew for each business."""
    # Get business type from command line arguments
    if len(sys.argv) > 1:
        business_type = sys.argv[1]
    else:
        business_type = "bar"  # Default fallback value
        
    try: 
        businesses = load_business_data(business_type)
        for business in businesses:
            print(f"\nProcessing business: {business['title']}")
            process_business(business, business_type)
            
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

if __name__ == "__main__":
    run()

