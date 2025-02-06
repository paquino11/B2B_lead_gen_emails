# B2B Lead Generator and Email Automation with CrewAI

A streamlit-based application that collects business information using Google Places API and CrewAI. This tool helps gather detailed information about businesses in specific locations, including contact details, social media presence, and ratings.

## Features

- Search businesses by type (e.g., accounting, restaurants, retail)
- Filter by country and district
- Collect detailed business information including:
  - Name and address
  - Contact information (phone, email)
  - Website and social media links
  - Business ratings and reviews
  - Additional business details

## Prerequisites

- Python 3.8 or higher
- Required API Keys:
  - Google Places API key
  - Anthropic API key (for Claude)
  - Serper API key (for web searches)

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/get_info_business.git
cd get_info_business
```

2. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install 'crewai[tools]'
```


4. Create a `.env` file in the root directory and add your API keys:
```bash
GOOGLE_API_KEY=your_google_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
SERPER_API_KEY=your_serper_api_key_here
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. In the web interface:
   - Enter the target country
   - Enter the district(s) (one per line)
   - Select the business type from the dropdown menu
   - Click "Start Collection" to begin gathering data

3. The application will:
   - First collect basic business information from the specified location
   - Then gather detailed information for each business
   - Display results in a real-time updating table

## Data Output

The collected data includes:
- Business name
- Email address
- Phone number
- Website
- Social media links (Instagram, Facebook)
- Business description
- Physical address
- Rating and review count

## Project Structure

- `app.py`: Main Streamlit application
- `scrape_businesses/`: Module for collecting business data from Google Places API
- `src/get_info_business/`: Core business logic and CrewAI implementation
- `requirements.txt`: Project dependencies

## API Keys

This application requires three API keys:

1. **Google Places API Key**: Used for collecting business information from Google Maps
   - Get it from [Google Cloud Console](https://console.cloud.google.com/)
   - Enable Places API in your project

2. **Anthropic API Key**: Used for AI-powered data analysis with Claude
   - Get it from [Anthropic](https://www.anthropic.com/)

3. **Serper API Key**: Used for web searches
   - Get it from [Serper.dev](https://serper.dev/)

## Notes

- Ensure all API keys are properly set in the `.env` file
- Rate limits may apply based on your API quotas
- Results are saved in JSON format and can be viewed in real-time through the interface
