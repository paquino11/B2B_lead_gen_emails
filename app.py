import streamlit as st
import subprocess
import json
import pandas as pd
from pathlib import Path
import time
from scrape_businesses.main import main as scrape_business
import webbrowser
from urllib.parse import quote

def load_results():
    """Load results from results.json file"""
    results_file = Path('results.json')
    if results_file.exists():
        with open(results_file, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
                # Convert to DataFrame
                df = pd.DataFrame(results)
                return df
            except json.JSONDecodeError:
                return pd.DataFrame()
    return pd.DataFrame()

def run_get_info_business(business_type):
    """Execute the get_info_business crew"""
    print("Running get_info_business...")
    
    # Combine all commands into a single shell script
    commands = [
        "python3 -m venv .venv",
        "source .venv/bin/activate",
        "pip install --upgrade pip",
        "pip install -r requirements.txt",
        "pip install 'crewai[tools]'",
        "pip install -e .",
        f"python3 -m get_info_business.main {business_type}"
    ]
    
    # Join commands with && to ensure they run sequentially and stop on any error
    full_command = " && ".join(commands)
    
    # Run all commands in a single shell session
    result = subprocess.run(
        full_command,
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode != 0:
        print(f"Error during execution: {result.stderr}")
    
    return result

def main():
    st.title("🎯 🤖 B2B Lead Generator and Email Automation with CrewAI")
    
    # Dictionary of country codes to emoji flags
    COUNTRY_EMOJIS = {
        'Afghanistan': '🇦🇫', 'Albania': '🇦🇱', 'Algeria': '🇩🇿', 'Andorra': '🇦🇩', 'Angola': '🇦🇴',
        'Argentina': '🇦🇷', 'Armenia': '🇦🇲', 'Australia': '🇦🇺', 'Austria': '🇦🇹', 'Azerbaijan': '🇦🇾',
        'Bahamas': '🇧🇸', 'Bahrain': '🇧🇭', 'Bangladesh': '🇧🇩', 'Barbados': '🇧🇧', 'Belarus': '🇧🇾',
        'Belgium': '🇧🇪', 'Belize': '🇧🇿', 'Benin': '🇧🇯', 'Bhutan': '🇧🇹', 'Bolivia': '🇧🇴',
        'Bosnia and Herzegovina': '🇧🇦', 'Botswana': '🇧🇼', 'Brazil': '🇧🇷', 'Brunei': '🇧🇳', 'Bulgaria': '🇧🇬',
        'Burkina Faso': '🇧🇫', 'Burundi': '🇧🇮', 'Cambodia': '🇰🇭', 'Cameroon': '🇨🇲', 'Canada': '🇨🇦',
        'Chad': '🇹🇩', 'Chile': '🇨🇱', 'China': '🇨🇳', 'Colombia': '🇨🇴', 'Congo': '🇨🇬',
        'Costa Rica': '🇨🇷', 'Croatia': '🇭🇷', 'Cuba': '🇨🇺', 'Cyprus': '🇨🇾', 'Czech Republic': '🇨��',
        'Denmark': '🇩🇰', 'Djibouti': '🇩🇯', 'Dominican Republic': '🇩🇴', 'Ecuador': '🇪🇨', 'Egypt': '🇪🇬',
        'El Salvador': '🇸🇻', 'Estonia': '🇪🇪', 'Ethiopia': '🇪🇹', 'Fiji': '🇫🇯', 'Finland': '🇫🇮',
        'France': '🇫🇷', 'Gabon': '🇬🇦', 'Georgia': '🇬🇪', 'Germany': '🇩🇪', 'Ghana': '🇬🇭',
        'Greece': '🇬🇷', 'Grenada': '🇬🇩', 'Guatemala': '🇬🇹', 'Guinea': '🇬🇳', 'Guyana': '🇬🇾',
        'Haiti': '🇭🇹', 'Honduras': '🇭🇳', 'Hungary': '🇭🇺', 'Iceland': '🇮🇸', 'India': '🇮🇳',
        'Indonesia': '🇮🇩', 'Iran': '🇮🇷', 'Iraq': '🇮🇶', 'Ireland': '🇮🇪', 'Israel': '🇮��',
        'Italy': '🇮🇹', 'Jamaica': '🇯🇲', 'Japan': '🇯🇵', 'Jordan': '🇯🇴', 'Kazakhstan': '🇰🇿',
        'Kenya': '🇰🇪', 'Kuwait': '🇰🇼', 'Kyrgyzstan': '🇰🇬', 'Laos': '🇱🇦', 'Latvia': '🇱��',
        'Lebanon': '🇱🇧', 'Lesotho': '🇱🇸', 'Liberia': '🇱🇷', 'Libya': '🇱🇾', 'Liechtenstein': '🇱🇮',
        'Lithuania': '🇱🇹', 'Luxembourg': '🇱🇺', 'Madagascar': '🇲🇬', 'Malawi': '🇲🇼', 'Malaysia': '🇲🇾',
        'Maldives': '🇲🇻', 'Mali': '🇲🇱', 'Malta': '🇲🇹', 'Mauritania': '🇲🇷', 'Mauritius': '🇲🇺',
        'Mexico': '🇲🇽', 'Moldova': '🇲🇩', 'Monaco': '🇲🇨', 'Mongolia': '🇲🇳', 'Montenegro': '🇲🇪',
        'Morocco': '🇲🇦', 'Mozambique': '🇲🇿', 'Myanmar': '🇲🇲', 'Namibia': '🇳🇦', 'Nepal': '🇳🇵',
        'Netherlands': '🇳🇱', 'New Zealand': '🇳🇿', 'Nicaragua': '🇳🇮', 'Niger': '🇳🇪', 'Nigeria': '🇳🇬',
        'North Korea': '🇰🇵', 'North Macedonia': '🇲🇰', 'Norway': '🇳🇴', 'Oman': '🇴🇲', 'Pakistan': '🇵🇰',
        'Panama': '🇵🇦', 'Papua New Guinea': '🇵🇬', 'Paraguay': '🇵🇾', 'Peru': '🇵🇪', 'Philippines': '🇵🇭',
        'Poland': '🇵🇱', 'Portugal': '🇵🇹', 'Qatar': '🇶🇦', 'Romania': '🇷🇴', 'Russia': '🇷🇺',
        'Rwanda': '🇷🇼', 'Saudi Arabia': '🇸🇦', 'Senegal': '🇸🇳', 'Serbia': '🇷🇸', 'Singapore': '🇸🇬',
        'Slovakia': '🇸🇰', 'Slovenia': '🇸🇮', 'Somalia': '🇸🇴', 'South Africa': '🇿🇦', 'South Korea': '🇰🇷',
        'Spain': '🇪🇸', 'Sri Lanka': '🇱🇰', 'Sudan': '🇸🇩', 'Sweden': '🇸🇪', 'Switzerland': '🇨🇭',
        'Syria': '🇸🇾', 'Taiwan': '🇹🇼', 'Tanzania': '🇹🇿', 'Thailand': '🇹🇭', 'Togo': '🇹🇬',
        'Tunisia': '🇹🇳', 'Turkey': '🇹🇷', 'Uganda': '🇺🇬', 'Ukraine': '🇺🇦', 'United Arab Emirates': '🇦🇪',
        'United Kingdom': '🇬🇧', 'United States': '🇺🇸', 'Uruguay': '🇺🇾', 'Uzbekistan': '🇺🇿',
        'Venezuela': '🇻🇪', 'Vietnam': '🇻🇳', 'Yemen': '🇾🇪', 'Zambia': '🇿🇲', 'Zimbabwe': '🇿🇼' 
    }

    # Create list of countries with emojis
    countries_with_emojis = [f"{emoji} {country}" for country, emoji in COUNTRY_EMOJIS.items()]

    # Find the index of Sweden in the list
    default_idx = next((i for i, country in enumerate(countries_with_emojis) if "Sweden" in country), 0)

    # Replace the text input with a selectbox, setting Sweden as default
    country = st.selectbox("Select country:", countries_with_emojis, index=default_idx)
    # Extract just the country name without the emoji
    selected_country = country.split(' ', 1)[1] if country else ''
    
    districts = st.text_area("Enter district").split('\n')
    
    # Updated business type selection with all Google Places types
    business_type = st.selectbox(
        "Select business type:",
        [
            "accounting",
            "airport",
            "amusement_park",
            "aquarium",
            "art_gallery",
            "atm",
            "bakery",
            "bank",
            "bar",
            "beauty_salon",
            "bicycle_store",
            "book_store",
            "bowling_alley",
            "bus_station",
            "cafe",
            "campground",
            "car_dealer",
            "car_rental",
            "car_repair",
            "car_wash",
            "casino",
            "cemetery",
            "church",
            "city_hall",
            "clothing_store",
            "convenience_store",
            "courthouse",
            "dentist",
            "department_store",
            "doctor",
            "drugstore",
            "electrician",
            "electronics_store",
            "embassy",
            "fire_station",
            "florist",
            "funeral_home",
            "furniture_store",
            "gas_station",
            "gym",
            "hair_care",
            "hardware_store",
            "hindu_temple",
            "home_goods_store",
            "hospital",
            "insurance_agency",
            "jewelry_store",
            "laundry",
            "lawyer",
            "library",
            "light_rail_station",
            "liquor_store",
            "local_government_office",
            "locksmith",
            "lodging",
            "meal_delivery",
            "meal_takeaway",
            "mosque",
            "movie_rental",
            "movie_theater",
            "moving_company",
            "museum",
            "night_club",
            "painter",
            "park",
            "parking",
            "pet_store",
            "pharmacy",
            "physiotherapist",
            "plumber",
            "police",
            "post_office",
            "primary_school",
            "real_estate_agency",
            "restaurant",
            "roofing_contractor",
            "rv_park",
            "school",
            "secondary_school",
            "shoe_store",
            "shopping_mall",
            "spa",
            "stadium",
            "storage",
            "store",
            "subway_station",
            "supermarket",
            "synagogue",
            "taxi_stand",
            "tourist_attraction",
            "train_station",
            "transit_station",
            "travel_agency",
            "university",
            "veterinary_care",
            "zoo"
        ]
    )
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Start Collection"):
            with st.spinner("Step 1: Collecting businesses..."):
                try:
                    scrape_business(districts, selected_country, business_type)
                    st.success("Step 1: Business collection completed!")
                except Exception as e:
                    st.error(f"Error in Step 1: {str(e)}")
                    return

            with st.spinner("Step 2: Getting detailed information..."):
                try:
                    result = run_get_info_business(business_type)
                    if result.stderr:
                        st.error(f"Error in Step 2: {result.stderr}")
                    else:
                        st.success("Step 2: Information gathering completed!")
                except Exception as e:
                    st.error(f"Error in Step 2: {str(e)}")
                    return

            st.success("All steps completed successfully!")

    # Create a placeholder for the results table
    table_placeholder = st.empty()
    
    # Use st.empty() to create a container that we can update
    results_container = st.empty()
    
    # Create a refresh button
    if st.button("Refresh Results"):
        st.rerun()
    
    # Load and display results
    df = load_results()
    if not df.empty:
        # Extract email_subject and email_body from the nested sales_email dictionary
        df['email_subject'] = df['sales_email'].apply(lambda x: x.get('email_subject') if isinstance(x, dict) else None)
        df['email_body'] = df['sales_email'].apply(lambda x: x.get('email_body') if isinstance(x, dict) else None)
        
        # Select specific columns to display
        display_columns = ['name', 'email', 'international_phone_number', 'website', 'instagram', 'facebook', 'about', 'formatted_address', 'rating', 'user_ratings_total']
        df_display = df[display_columns]
        
        # Add a button to export the data to CSV
        csv = df_display.to_csv(index=False)
        st.download_button(
            label="Export data as CSV",
            data=csv,
            file_name='business_data.csv',
            mime='text/csv',
        )
        
        # Clear previous content and update with new data
        with results_container.container():
            # Display each row with a send email button
            for index, row in df_display.iterrows():
                col1, col2 = st.columns([1, 11])
                with col1:
                    email = row['email'] if pd.notna(row['email']) else ''
                    subject = df.loc[index, 'email_subject'] if pd.notna(df.loc[index, 'email_subject']) else ''
                    body = df.loc[index, 'email_body'] if pd.notna(df.loc[index, 'email_body']) else ''
                    
                    mailto_link = f'mailto:{email}?subject={quote(subject)}&body={quote(body)}'
                    
                    if st.button("📧", key=f"email_{index}"):
                        subprocess.run(['open', '-a', 'Mail', mailto_link])
                
                with col2:
                    st.write(f"**{row['name']}**")
                    st.write(f"Email: {row['email']}")
                    st.write(f"Phone: {row['international_phone_number']}")
                    st.write(f"Website: {row['website']}")
                    st.write(f"Address: {row['formatted_address']}")
                    st.write("---")

    # Add auto-refresh using st.rerun()
    time.sleep(5)
    st.rerun()

if __name__ == "__main__":
    main() 