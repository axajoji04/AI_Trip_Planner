import streamlit as st
import requests
import datetime
import time
import json
import os
import re
from typing import Optional, Dict, Any
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration with fallbacks
try:
    BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    EXCHANGE_API_URL = os.getenv("EXCHANGE_API_URL", "https://api.exchangerate-api.com/v4/latest/USD")
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
except Exception as e:
    logger.error(f"Configuration error: {e}")
    BASE_URL = "http://localhost:8000"
    EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    TIMEOUT = 30

def initialize_page_config():
    """Initialize page config safely"""
    try:
        st.set_page_config(
            page_title="AI Travel Companion",
            page_icon="✈️",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception as e:
        logger.warning(f"Page config already set: {e}")
        pass

def load_stunning_custom_css():
    """Load beautiful CSS styling for amazing presentation"""
    css_content = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=Inter:wght@300;400;500;600&display=swap');
        
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Beautiful gradient background */
        .main {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        
        /* Stunning content containers */
        .stunning-content {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.8;
            color: #2d3748;
            background: linear-gradient(145deg, #ffffff 0%, #f7fafc 100%);
            padding: 2.5rem;
            border-radius: 20px;
            box-shadow: 
                0 20px 25px -5px rgba(0, 0, 0, 0.1),
                0 10px 10px -5px rgba(0, 0, 0, 0.04);
            margin: 1.5rem 0;
            border: 1px solid rgba(255, 255, 255, 0.18);
            backdrop-filter: blur(10px);
        }
        
        /* Elegant headings with spacing */
        .elegant-heading {
            font-family: 'Playfair Display', serif;
            font-size: 28px;
            font-weight: 700;
            color: #1a202c;
            margin: 30px 0 20px 0;
            padding-bottom: 15px;
            border-bottom: 3px solid #667eea;
            position: relative;
            text-align: center;
        }
        
        .elegant-heading::after {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        /* Beautiful subheadings */
        .beautiful-subheading {
            font-family: 'Playfair Display', serif;
            font-size: 22px;
            font-weight: 600;
            color: #2d3748;
            margin: 25px 0 15px 0;
            padding-left: 20px;
            border-left: 4px solid #667eea;
            background: linear-gradient(90deg, rgba(102, 126, 234, 0.1) 0%, transparent 100%);
            padding: 15px 20px;
            border-radius: 0 10px 10px 0;
        }
        
        /* Premium text styling */
        .premium-text {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.8;
            color: #4a5568;
            margin: 15px 0;
            text-align: justify;
            letter-spacing: 0.3px;
        }
        
        /* Gorgeous day sections */
        .gorgeous-day-section {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 2rem;
            margin: 2rem 0;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(240, 147, 251, 0.3);
            position: relative;
            overflow: hidden;
        }
        
        .gorgeous-day-section::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.5;
        }
        
        .gorgeous-day-section .day-title {
            font-family: 'Playfair Display', serif;
            font-size: 24px;
            font-weight: 700;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
            position: relative;
            z-index: 1;
        }
        
        .gorgeous-day-section .day-content {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.7;
            position: relative;
            z-index: 1;
        }
        
        /* Luxurious buttons */
        .luxury-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px 30px;
            font-family: 'Inter', sans-serif;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .luxury-button:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.4);
        }
        
        /* Spectacular header styling */
        .spectacular-header {
            text-align: center;
            padding: 3rem 2rem;
            background: linear-gradient(135deg, rgba(255,255,255,0.95) 0%, rgba(247,250,252,0.95) 100%);
            border-radius: 25px;
            margin-bottom: 3rem;
            box-shadow: 0 25px 50px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .spectacular-header h1 {
            font-family: 'Playfair Display', serif;
            font-size: 36px;
            color: #1a202c;
            margin: 0 0 15px 0;
            font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .spectacular-header p {
            font-family: 'Inter', sans-serif;
            font-size: 18px;
            color: #4a5568;
            margin: 0;
            font-weight: 400;
        }
        
        /* Amazing list styling */
        .amazing-list-item {
            font-family: 'Inter', sans-serif;
            font-size: 15px;
            line-height: 1.7;
            color: #4a5568;
            margin: 10px 0;
            padding: 12px 0 12px 30px;
            position: relative;
            border-bottom: 1px solid rgba(102, 126, 234, 0.1);
        }
        
        .amazing-list-item::before {
            content: "✨";
            position: absolute;
            left: 0;
            top: 12px;
            font-size: 16px;
        }
        
        /* Stunning price highlighting */
        .stunning-price-highlight {
            background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            display: inline-block;
            margin: 0 5px;
            box-shadow: 0 5px 15px rgba(255, 216, 155, 0.4);
        }

        /* Premium main container */
        .premium-main-container {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 25px;
            padding: 3rem;
            margin: 2rem 0;
            box-shadow: 0 25px 50px rgba(0,0,0,0.15);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        /* Elegant menu button styling */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            padding: 15px 25px;
            font-family: 'Inter', sans-serif;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
            font-size: 15px;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 15px 30px rgba(102, 126, 234, 0.3);
        }
        
        /* Beautiful currency converter */
        .beautiful-currency-converter {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            color: #2d3748;
            text-align: center;
            box-shadow: 0 15px 35px rgba(168, 237, 234, 0.3);
        }
        
        /* Magnificent loading spinner */
        .magnificent-loading-spinner {
            display: inline-block;
            width: 50px;
            height: 50px;
            border: 4px solid rgba(102, 126, 234, 0.3);
            border-radius: 50%;
            border-top-color: #667eea;
            animation: magnificent-spin 1s ease-in-out infinite;
        }
        
        @keyframes magnificent-spin {
            to { transform: rotate(360deg); }
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .stunning-content {
                padding: 1.5rem;
                margin: 1rem 0;
            }
            
            .elegant-heading {
                font-size: 24px;
            }
            
            .beautiful-subheading {
                font-size: 18px;
            }
            
            .spectacular-header h1 {
                font-size: 28px;
            }
        }
        
        /* Enhanced spacing classes */
        .space-large { margin: 2.5rem 0; }
        .space-medium { margin: 1.5rem 0; }
        .space-small { margin: 1rem 0; }
        .padding-large { padding: 2.5rem; }
        .padding-medium { padding: 1.5rem; }
        .padding-small { padding: 1rem; }
        
        /* Special sections styling */
        .hotel-section {
            background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            color: #1a202c;
            box-shadow: 0 15px 35px rgba(132, 250, 176, 0.3);
        }
        
        .cost-section {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            color: #1a202c;
            box-shadow: 0 15px 35px rgba(250, 112, 154, 0.3);
        }
        
        .weather-section {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            color: #1a202c;
            box-shadow: 0 15px 35px rgba(79, 172, 254, 0.3);
        }
        
        .activity-section {
            background: linear-gradient(135deg, #c471f5 0%, #fa71cd 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 2rem 0;
            color: white;
            box-shadow: 0 15px 35px rgba(196, 113, 245, 0.3);
        }
    </style>
    """
    
    try:
        st.markdown(css_content, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Beautiful CSS loading error: {e}")

def init_session_state():
    """Initialize session state variables safely"""
    try:
        if "current_view" not in st.session_state:
            st.session_state.current_view = "main"
        if "travel_data" not in st.session_state:
            st.session_state.travel_data = None
        if "user_query" not in st.session_state:
            st.session_state.user_query = ""
        if "currency" not in st.session_state:
            st.session_state.currency = "USD"
        if "exchange_rates" not in st.session_state:
            st.session_state.exchange_rates = {}
        if "loading" not in st.session_state:
            st.session_state.loading = False
    except Exception as e:
        logger.error(f"Session state initialization error: {e}")

def get_exchange_rates():
    """Fetch current exchange rates"""
    try:
        if not st.session_state.exchange_rates:
            response = requests.get(EXCHANGE_API_URL, timeout=10)
            if response.status_code == 200:
                data = response.json()
                st.session_state.exchange_rates = data.get("rates", {})
                st.session_state.exchange_rates["USD"] = 1.0  # Base currency
        return st.session_state.exchange_rates
    except Exception as e:
        logger.error(f"Exchange rate fetch error: {e}")
        # Fallback rates
        return {
            "USD": 1.0,
            "INR": 83.0,
            "EUR": 0.85,
            "GBP": 0.73,
            "AUD": 1.35,
            "CAD": 1.25,
            "JPY": 110.0
        }

def convert_price(amount_str, target_currency="INR"):
    """Convert price from USD to target currency"""
    try:
        # Extract numeric value from price string
        price_match = re.search(r'[\d,]+(?:\.\d+)?', str(amount_str))
        if not price_match:
            return amount_str
        
        amount = float(price_match.group().replace(',', ''))
        
        if target_currency == "USD":
            return f"${amount:,.2f}"
        
        rates = get_exchange_rates()
        if target_currency in rates:
            converted = amount * rates[target_currency]
            
            currency_symbols = {
                "INR": "₹",
                "EUR": "€", 
                "GBP": "£",
                "JPY": "¥",
                "AUD": "A$",
                "CAD": "C$"
            }
            
            symbol = currency_symbols.get(target_currency, target_currency)
            return f"{symbol}{converted:,.2f}"
        
        return amount_str
    except Exception as e:
        logger.error(f"Price conversion error: {e}")
        return amount_str

def extract_price_ranges(text):
    """Extract and convert price ranges from text with beautiful highlighting"""
    try:
        currency = st.session_state.currency
        if currency == "USD":
            # Still highlight prices even in USD
            price_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
            def highlight_price(match):
                return f'<span class="stunning-price-highlight">{match.group(0)}</span>'
            return re.sub(price_pattern, highlight_price, text)
        
        # Pattern to match prices like $250, $100-200, etc.
        price_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
        range_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[-–]\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        
        def replace_single_price(match):
            original = match.group(0)
            converted = convert_price(match.group(1), currency)
            return f'<span class="stunning-price-highlight">{original} ({converted})</span>'
        
        def replace_price_range(match):
            amount1 = match.group(1)
            amount2 = match.group(2)
            original = match.group(0)
            converted1 = convert_price(amount1, currency)
            converted2 = convert_price(amount2, currency)
            return f'<span class="stunning-price-highlight">{original} ({converted1} - {converted2})</span>'
        
        # First replace ranges, then single prices
        text = re.sub(range_pattern, replace_price_range, text)
        text = re.sub(price_pattern, replace_single_price, text)
        
        return text
    except Exception as e:
        logger.error(f"Price range extraction error: {e}")
        return text

def make_api_request(user_input: str, request_type: str = "complete") -> Optional[Dict[Any, Any]]:
    """Make API request with comprehensive error handling"""
    try:
        logger.info(f"Making request to {BASE_URL}/query")
        
        # Modify the query based on request type
        modified_query = user_input
        if request_type == "hotels":
            modified_query = f"Recommend detailed hotels and accommodations for: {user_input}"
        elif request_type == "cost":
            modified_query = f"Provide detailed cost breakdown and budget analysis for: {user_input}"
        elif request_type == "weather":
            modified_query = f"Provide weather information and climate details for: {user_input}"
        elif request_type == "alternatives":
            modified_query = f"Suggest alternative travel plans and options for: {user_input}"
        
        payload = {"question": modified_query}
        headers = {"Content-Type": "application/json"}
        
        response = requests.post(
            f"{BASE_URL}/query", 
            json=payload,
            timeout=TIMEOUT,
            headers=headers
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            return response.json()
        else:
            error_msg = f"Server returned status {response.status_code}"
            if response.text:
                error_msg += f": {response.text[:200]}"
            st.error(f"Server Error: {error_msg}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        st.error("Connection Error: Unable to connect to the travel planning service.")
        if "localhost" in BASE_URL:
            st.info("Tip: Make sure your backend server is running locally, or update the BACKEND_URL environment variable.")
        return None
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error: {e}")
        st.error(f"Timeout Error: Request took longer than {TIMEOUT} seconds. Please try again.")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        st.error(f"Network Error: {str(e)[:200]}")
        return None
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        st.error("Response Error: Invalid response format from server.")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.error(f"Unexpected Error: {str(e)[:200]}")
        return None

def clean_content_from_markdown(content: str) -> str:
    """Remove markdown formatting and clean up content"""
    # Remove markdown headers (# ## ### ####)
    content = re.sub(r'^#{1,6}\s*', '', content, flags=re.MULTILINE)
    
    # Remove markdown bold (**text** or __text__)
    content = re.sub(r'\*\*(.*?)\*\*', r'\1', content)
    content = re.sub(r'__(.*?)__', r'\1', content)
    
    # Remove markdown italic (*text* or _text_)
    content = re.sub(r'\*(.*?)\*', r'\1', content)
    content = re.sub(r'_(.*?)_', r'\1', content)
    
    # Remove markdown lists (- or * at start of line)
    content = re.sub(r'^[-\*]\s*', '', content, flags=re.MULTILINE)
    
    # Remove extra dashes/separators
    content = re.sub(r'^-+$', '', content, flags=re.MULTILINE)
    
    # Clean up multiple newlines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    return content.strip()

def display_spectacular_welcome_screen():
    """Display spectacular welcome screen"""
    try:
        st.markdown("""
        <div class="premium-main-container">
            <div class="spectacular-header">
                <h1>✈️ AI Travel Companion</h1>
                <p>Your intelligent travel planning assistant for extraordinary journeys</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards with amazing spacing
        st.markdown('<div class="space-large"></div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        
        features = [
            ("🎯 Interactive Menus", "Choose specific aspects of your trip to explore in detail"),
            ("💱 Currency Conversion", "Automatic price conversion to your preferred currency"), 
            ("✨ Premium Presentation", "Professional, beautifully formatted travel information")
        ]
        
        for i, (title, description) in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div class="stunning-content space-medium">
                    <div class="beautiful-subheading">{title}</div>
                    <div class="premium-text">{description}</div>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        logger.error(f"Welcome screen error: {e}")
        st.title("AI Travel Companion")
        st.write("Your intelligent travel planning assistant")

def display_elegant_menu():
    """Display the interactive menu after getting travel data"""
    st.markdown(f"""
    <div class="spectacular-header">
        <h1>Choose Your Travel Experience</h1>
        <p class="space-small">Your travel query: <strong>"{st.session_state.user_query}"</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create menu grid with beautiful spacing
    st.markdown('<div class="space-medium"></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    menu_options = [
        ("complete", "🗓️ Complete Itinerary", "Full comprehensive travel plan with everything", col1),
        ("hotels", "🏨 Hotel Recommendations", "Detailed accommodation options and reviews", col2),
        ("cost", "💰 Cost Breakdown", "Detailed budget analysis with price estimates", col3),
        ("weather", "🌤️ Weather Information", "Climate details and best travel times", col4),
        ("alternatives", "🔄 Alternative Plans", "Different options and backup suggestions", col5)
    ]
    
    for option_id, title, description, column in menu_options:
        with column:
            st.markdown(f"""
            <div class="stunning-content space-small">
                <div class="beautiful-subheading">{title}</div>
                <div class="premium-text">{description}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Explore {title.split()[-1]}", key=f"menu_{option_id}", use_container_width=True):
                st.session_state.current_view = option_id
                st.session_state.loading = True
                st.rerun()
    
    # Currency converter in the last column
    with col6:
        display_beautiful_currency_converter()

def display_beautiful_currency_converter():
    """Display beautiful currency converter"""
    st.markdown("""
    <div class="beautiful-currency-converter">
        <div class="beautiful-subheading">💱 Currency</div>
        <div class="premium-text">Prices in your preferred currency</div>
    </div>
    """, unsafe_allow_html=True)
    
    currencies = {
        "USD": "🇺🇸 USD",
        "INR": "🇮🇳 INR", 
        "EUR": "🇪🇺 EUR",
        "GBP": "🇬🇧 GBP",
        "AUD": "🇦🇺 AUD",
        "CAD": "🇨🇦 CAD",
        "JPY": "🇯🇵 JPY"
    }
    
    selected_currency = st.selectbox(
        "Select Currency:",
        options=list(currencies.keys()),
        format_func=lambda x: currencies[x],
        index=list(currencies.keys()).index(st.session_state.currency) if st.session_state.currency in currencies else 0,
        key="currency_selector"
    )
    
    if selected_currency != st.session_state.currency:
        st.session_state.currency = selected_currency
        st.rerun()

def identify_section_type(content_section):
    """Identify what type of section this is based on content"""
    content_lower = content_section.lower()
    
    if any(keyword in content_lower for keyword in ['hotel', 'accommodation', 'stay', 'lodge', 'resort']):
        return 'hotel'
    elif any(keyword in content_lower for keyword in ['cost', 'budget', 'price', 'expense', 'money', '$']):
        return 'cost'  
    elif any(keyword in content_lower for keyword in ['weather', 'climate', 'temperature', 'rain', 'sunny']):
        return 'weather'
    elif any(keyword in content_lower for keyword in ['activity', 'attraction', 'visit', 'tour', 'museum', 'park']):
        return 'activity'
    elif any(keyword in content_lower for keyword in ['day 1', 'day 2', 'day 3', 'morning', 'afternoon', 'evening']):
        return 'day'
    else:
        return 'general'

def display_gorgeous_itinerary(content: str):
    """Display itinerary in gorgeous format with proper spacing"""
    # Split content into sections
    sections = re.split(r'\n\s*\n', content)
    
    for section in sections:
        if not section.strip():
            continue
            
        # Add beautiful spacing between sections
        st.markdown('<div class="space-medium"></div>', unsafe_allow_html=True)
        
        section_type = identify_section_type(section)
        
        # Check if it's a day section
        if re.match(r'Day \d+', section, re.IGNORECASE) or section_type == 'day':
            lines = section.split('\n')
            day_title = lines[0].strip()
            day_content = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
            
            processed_content = extract_price_ranges(day_content)
            
            st.markdown(f"""
            <div class="gorgeous-day-section space-large">
                <div class="day-title">🗓️ {day_title}</div>
                <div class="space-small"></div>
                <div class="day-content">{processed_content.replace(chr(10), '<br><br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif section_type == 'hotel':
            processed_content = extract_price_ranges(section)
            st.markdown(f"""
            <div class="hotel-section space-large">
                <div class="beautiful-subheading">🏨 Accommodation Recommendations</div>
                <div class="space-small"></div>
                <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif section_type == 'cost':
            processed_content = extract_price_ranges(section)
            st.markdown(f"""
            <div class="cost-section space-large">
                <div class="beautiful-subheading">💰 Budget & Costs</div>
                <div class="space-small"></div>
                <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif section_type == 'weather':
            processed_content = extract_price_ranges(section)
            st.markdown(f"""
            <div class="weather-section space-large">
                <div class="beautiful-subheading">🌤️ Weather & Climate</div>
                <div class="space-small"></div>
                <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        elif section_type == 'activity':
            processed_content = extract_price_ranges(section)
            st.markdown(f"""
            <div class="activity-section space-large">
                <div class="beautiful-subheading">🎯 Activities & Attractions</div>
                <div class="space-small"></div>
                <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            # General content section
            processed_content = extract_price_ranges(section)
            
            # Check if section has a title
            lines = section.split('\n')
            if lines and len(lines[0]) < 100 and ':' not in lines[0]:
                title = lines[0].strip()
                content_text = '\n'.join(lines[1:]).strip() if len(lines) > 1 else ""
                
                st.markdown(f"""
                <div class="stunning-content space-large">
                    <div class="elegant-heading">{title}</div>
                    <div class="space-small"></div>
                    <div class="premium-text">{extract_price_ranges(content_text).replace(chr(10), '<br><br>')}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="stunning-content space-large">
                    <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
                </div>
                """, unsafe_allow_html=True)

def display_stunning_generic_content(content: str):
    """Display generic content in stunning format"""
    processed_content = extract_price_ranges(content)
    st.markdown(f"""
    <div class="stunning-content space-large">
        <div class="premium-text">{processed_content.replace(chr(10), '<br><br>')}</div>
    </div>
    """, unsafe_allow_html=True)

def display_magnificent_content_page(content_type: str, data: str):
    """Display content in magnificent format with beautiful spacing"""
    
    # Beautiful back button
    st.markdown('<div class="space-medium"></div>', unsafe_allow_html=True)
    if st.button("← ✨ Back to Menu", key="back_button", use_container_width=False):
        st.session_state.current_view = "menu"
        st.rerun()
    
    # Content titles with emojis
    titles = {
        "complete": "🗓️ Complete Travel Itinerary",
        "hotels": "🏨 Hotel Recommendations", 
        "cost": "💰 Cost Breakdown",
        "weather": "🌤️ Weather Information",
        "alternatives": "🔄 Alternative Plans"
    }
    
    title = titles.get(content_type, "✈️ Travel Information")
    
    # Spectacular header
    st.markdown(f"""
    <div class="spectacular-header space-large">
        <h1>{title}</h1>
        <p>Expertly curated travel information for your perfect journey</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean and process content
    clean_data = clean_content_from_markdown(data)
    
    # Display content in magnificent format
    if content_type == "complete":
        display_gorgeous_itinerary(clean_data)
    else:
        display_stunning_generic_content(clean_data)
    
    # Add beautiful spacing at the end
    st.markdown('<div class="space-large"></div>', unsafe_allow_html=True)

def display_content_page(content_type: str, data: str):
    """Display specific content page with back button - MAGNIFICENT VERSION"""
    display_magnificent_content_page(content_type, data)

def main():
    """Main application function"""
    try:
        # Initialize everything
        initialize_page_config()
        load_stunning_custom_css()
        init_session_state()
        
        # Handle different views
        if st.session_state.current_view == "main":
            # Display spectacular welcome screen
            display_spectacular_welcome_screen()
            
            # Chat section with beautiful spacing
            st.markdown('<div class="space-large"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="stunning-content">
                <div class="elegant-heading">🎯 Plan Your Perfect Trip</div>
                <div class="premium-text">Tell us about your dream destination and we'll create a comprehensive travel plan</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Input section with beautiful styling
            st.markdown('<div class="space-medium"></div>', unsafe_allow_html=True)
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    user_input = st.text_input(
                        "",
                        placeholder="✈️ Where would you like to travel? e.g., 'Plan a 5-day romantic trip to Paris for 2 people'",
                        key="travel_input",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    send_button = st.button("🚀 Plan Trip", use_container_width=True)
            
            # Example prompts with stunning presentation
            st.markdown('<div class="space-large"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div class="stunning-content">
                <div class="beautiful-subheading">✨ Try These Amazing Examples</div>
            </div>
            """, unsafe_allow_html=True)
            
            example_col1, example_col2, example_col3 = st.columns(3)
            
            examples = [
                ("🏖️ Beach Vacation in Goa", "Plan a 7-day beach vacation in Goa for 2 people with water sports and local cuisine"),
                ("🏔️ Adventure in Nepal", "Plan a 10-day adventure trip to Nepal including trekking and cultural sites for 3 people"),
                ("🏰 Cultural Rajasthan Tour", "Plan a 5-day cultural heritage tour of Rajasthan covering palaces and forts for a family of 4")
            ]
            
            for i, (button_text, query) in enumerate(examples):
                with [example_col1, example_col2, example_col3][i]:
                    st.markdown(f"""
                    <div class="stunning-content space-small">
                        <div class="premium-text">{button_text.split(' ', 1)[1]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button(button_text, use_container_width=True):
                        st.session_state.user_query = query
                        st.session_state.current_view = "menu"
                        # Get initial travel data
                        with st.spinner("🎨 Crafting your perfect travel experience..."):
                            response_data = make_api_request(query, "complete")
                            if response_data:
                                st.session_state.travel_data = response_data.get("answer", "")
                        st.rerun()
            
            # Process user input
            if send_button and user_input and user_input.strip():
                st.session_state.user_query = user_input.strip()
                st.session_state.current_view = "menu"
                # Get initial travel data
                with st.spinner("🎨 Crafting your perfect travel experience..."):
                    response_data = make_api_request(user_input.strip(), "complete")
                    if response_data:
                        st.session_state.travel_data = response_data.get("answer", "")
                st.rerun()
        
        elif st.session_state.current_view == "menu":
            # Display the elegant menu
            display_elegant_menu()
        
        elif st.session_state.current_view in ["complete", "hotels", "cost", "weather", "alternatives"]:
            # Handle loading state with magnificent styling
            if st.session_state.loading:
                st.markdown("""
                <div class="stunning-content space-large">
                    <div style="text-align: center; padding: 4rem;">
                        <div class="magnificent-loading-spinner"></div>
                        <div class="space-medium"></div>
                        <div class="elegant-heading">🎨 AI is crafting your detailed information...</div>
                        <div class="premium-text">Creating something beautiful just for you</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Make API request for specific content
                response_data = make_api_request(st.session_state.user_query, st.session_state.current_view)
                st.session_state.loading = False
                
                if response_data and response_data.get("answer"):
                    # Display the specific content
                    display_content_page(st.session_state.current_view, response_data.get("answer"))
                else:
                    st.markdown("""
                    <div class="stunning-content space-large">
                        <div class="elegant-heading">⚠️ Unable to Generate Information</div>
                        <div class="premium-text">We encountered an issue generating your travel information. This might be due to:</div>
                        <div class="space-small"></div>
                        <div class="amazing-list-item">API server is not running or unreachable</div>
                        <div class="amazing-list-item">API keys might be missing or invalid</div>
                        <div class="amazing-list-item">Rate limits may have been exceeded</div>
                        <div class="space-medium"></div>
                        <div class="premium-text">Please check your backend server and API configuration.</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if st.button("← ✨ Back to Menu"):
                        st.session_state.current_view = "menu"
                        st.rerun()
            else:
                # This shouldn't happen, but just in case
                st.session_state.current_view = "menu"
                st.rerun()
        
        # Beautiful footer
        st.markdown('<div class="space-large"></div>', unsafe_allow_html=True)
        st.markdown("""
        <div class="stunning-content">
            <div style="text-align: center; color: #4a5568; font-size: 14px; padding: 1rem;">
                ✨ Built with Streamlit & AI • Navigate through different sections to explore your travel plan ✨
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        logger.critical(f"Main app crash: {e}")
        st.error("Critical error: The application crashed.")
        
        # Reset button in case of crash
        if st.button("🔄 Reset Application"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
    