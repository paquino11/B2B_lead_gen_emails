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
    
    # Text input for city
    city = st.text_input("Enter city name:", placeholder="e.g., New York")
    
    # Text input for business type
    business_type = st.text_input("Enter business type:", placeholder="e.g., restaurant, accounting, retail")
    
    # Create two columns
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.button("Start Collection"):
            if not city or not business_type:
                st.error("Please enter both city and business type.")
                return
                
            with st.spinner("Step 1: Collecting businesses..."):
                try:
                    scrape_business(city, business_type)
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