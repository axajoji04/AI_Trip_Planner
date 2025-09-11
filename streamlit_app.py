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
            page_title="✈️ AI Travel Companion",
            page_icon="✈️",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception as e:
        logger.warning(f"Page config already set: {e}")
        pass

def load_custom_css():
    """Load enhanced custom CSS styling"""
    css_content = """
    <style>
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Main container styling */
        .main-container {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            padding: 2rem;
            margin: 1rem 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        
        /* Menu button grid */
        .menu-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 1.5rem;
            margin: 2rem 0;
        }
        
        /* Menu option cards */
        .menu-option {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 15px;
            padding: 2rem;
            text-align: center;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            border: none;
            text-decoration: none;
        }
        
        .menu-option:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.3);
            background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        }
        
        .menu-icon {
            font-size: 3rem;
            margin-bottom: 1rem;
            display: block;
        }
        
        .menu-title {
            font-size: 1.3rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .menu-description {
            font-size: 0.9rem;
            opacity: 0.9;
            line-height: 1.4;
        }
        
        /* Content display cards */
        .content-card {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            border-radius: 20px;
            padding: 2.5rem;
            margin: 2rem 0;
            color: white;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            animation: slideInUp 0.5s ease-out;
        }
        
        .content-header {
            text-align: center;
            border-bottom: 2px solid rgba(255,255,255,0.3);
            padding-bottom: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .content-header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        /* Specific content type cards */
        .itinerary-card {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .hotel-card {
            background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .cost-card {
            background: linear-gradient(135deg, #96c93d 0%, #00b09b 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .weather-card {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: white;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        .alternative-card {
            background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
            border-radius: 15px;
            padding: 2rem;
            margin: 1.5rem 0;
            color: #333;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }
        
        /* Back button */
        .back-button {
            background: linear-gradient(135deg, #fd79a8 0%, #fdcb6e 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.8rem 2rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-bottom: 2rem;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        
        .back-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.3);
        }
        
        /* Currency converter */
        .currency-converter {
            background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
            border-radius: 15px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: white;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            text-align: center;
        }
        
        /* Animations */
        @keyframes slideInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        /* Button improvements */
        .stButton > button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.7rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(0,0,0,0.3);
        }
        
        /* Responsive design */
        @media (max-width: 768px) {
            .menu-grid {
                grid-template-columns: 1fr;
            }
            
            .content-card {
                margin: 1rem 0;
                padding: 1.5rem;
            }
            
            .content-header h1 {
                font-size: 2rem;
            }
        }
        
        /* Loading spinner */
        .loading-spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid rgba(255,255,255,0.3);
            border-radius: 50%;
            border-top-color: white;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Day cards in itinerary */
        .day-section {
            background: rgba(255,255,255,0.15);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .day-header {
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 1rem;
            color: white;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
        }
        
        /* Cost breakdown styling */
        .cost-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.8rem;
            background: rgba(255,255,255,0.1);
            border-radius: 8px;
            margin: 0.5rem 0;
            backdrop-filter: blur(5px);
        }
        
        .cost-total {
            background: rgba(255,255,255,0.2);
            border-radius: 10px;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 1.2rem;
            font-weight: 700;
            text-align: center;
        }
    </style>
    """
    
    try:
        st.markdown(css_content, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"CSS loading error: {e}")

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
    """Extract and convert price ranges from text"""
    try:
        currency = st.session_state.currency
        if currency == "USD":
            return text
        
        # Pattern to match prices like $250, $100-200, etc.
        price_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)'
        range_pattern = r'\$(\d+(?:,\d{3})*(?:\.\d{2})?)\s*[-–]\s*\$?(\d+(?:,\d{3})*(?:\.\d{2})?)'
        
        def replace_single_price(match):
            original = match.group(0)
            converted = convert_price(match.group(1), currency)
            return f"{original} ({converted})"
        
        def replace_price_range(match):
            amount1 = match.group(1)
            amount2 = match.group(2)
            original = match.group(0)
            converted1 = convert_price(amount1, currency)
            converted2 = convert_price(amount2, currency)
            return f"{original} ({converted1} - {converted2})"
        
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
            st.error(f"🚫 **Server Error**: {error_msg}")
            return None
            
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error: {e}")
        st.error("🔌 **Connection Error**: Unable to connect to the travel planning service.")
        if "localhost" in BASE_URL:
            st.info("💡 **Tip**: Make sure your backend server is running locally, or update the BACKEND_URL environment variable.")
        return None
        
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout error: {e}")
        st.error(f"⏰ **Timeout Error**: Request took longer than {TIMEOUT} seconds. Please try again.")
        return None
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request error: {e}")
        st.error(f"🌐 **Network Error**: {str(e)[:200]}")
        return None
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        st.error("📄 **Response Error**: Invalid response format from server.")
        return None
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        st.error(f"❌ **Unexpected Error**: {str(e)[:200]}")
        return None

def display_welcome_screen():
    """Display welcome screen"""
    try:
        st.markdown("""
        <div class="main-container">
            <div style="text-align: center; color: white; margin-bottom: 2rem;">
                <div style="font-size: 3rem; font-weight: 700; margin-bottom: 0.5rem; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);">✈️ AI Travel Companion</div>
                <div style="font-size: 1.2rem; opacity: 0.9; font-weight: 300;">Your intelligent travel planning assistant with interactive menu-driven experience</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        features = [
            ("🎯", "Interactive Menus", "Choose specific aspects of your trip to explore in detail"),
            ("💱", "Smart Currency Conversion", "Automatic price conversion to your preferred currency"),
            ("🎨", "Beautiful Displays", "Organized, emoji-rich presentations for easy reading")
        ]
        
        for i, (icon, title, description) in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.1); border-radius: 15px; padding: 1.5rem; margin: 1rem; text-align: center; color: white; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                    <div style="font-size: 2.5rem; margin-bottom: 1rem;">{icon}</div>
                    <h3>{title}</h3>
                    <p>{description}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        logger.error(f"Welcome screen error: {e}")
        st.title("✈️ AI Travel Companion")
        st.write("Your intelligent travel planning assistant")

def display_menu():
    """Display the interactive menu after getting travel data"""
    st.markdown("""
    <div class="content-card">
        <div class="content-header">
            <h1>🎯 Choose What You'd Like to Explore</h1>
            <p style="font-size: 1.1rem; margin-top: 1rem;">
                Your travel query: <strong>"{}"</strong>
            </p>
        </div>
    </div>
    """.format(st.session_state.user_query), unsafe_allow_html=True)
    
    # Create menu grid
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    menu_options = [
        ("complete", "📋", "Complete Itinerary", "Full day-by-day travel plan with activities", col1),
        ("hotels", "🏨", "Hotel Recommendations", "Detailed accommodation options and reviews", col2),
        ("cost", "💰", "Cost Breakdown", "Detailed budget analysis with price estimates", col3),
        ("weather", "🌤️", "Weather Information", "Climate details and best travel times", col4),
        ("alternatives", "🔄", "Alternative Plans", "Different options and backup suggestions", col5)
    ]
    
    for option_id, icon, title, description, column in menu_options:
        with column:
            if st.button(f"{icon} {title}", key=f"menu_{option_id}", use_container_width=True):
                st.session_state.current_view = option_id
                st.session_state.loading = True
                st.rerun()
    
    # Currency converter in the last column
    with col6:
        display_currency_converter_compact()

def display_currency_converter_compact():
    """Display compact currency converter"""
    st.markdown("""
    <div class="currency-converter">
        <h4>💱 Currency</h4>
        <p>Prices shown in your preferred currency</p>
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
        "Currency:",
        options=list(currencies.keys()),
        format_func=lambda x: currencies[x],
        index=list(currencies.keys()).index(st.session_state.currency) if st.session_state.currency in currencies else 0,
        key="currency_selector"
    )
    
    if selected_currency != st.session_state.currency:
        st.session_state.currency = selected_currency
        st.rerun()

def display_content_page(content_type: str, data: str):
    """Display specific content page with back button"""
    
    # Back button
    if st.button("← Back to Menu", key="back_button", use_container_width=False):
        st.session_state.current_view = "menu"
        st.rerun()
    
    # Content mapping
    content_config = {
        "complete": {
            "title": "📋 Complete Travel Itinerary",
            "icon": "📋",
            "card_class": "itinerary-card",
            "description": "Your comprehensive day-by-day travel plan"
        },
        "hotels": {
            "title": "🏨 Hotel Recommendations",
            "icon": "🏨",
            "card_class": "hotel-card",
            "description": "Carefully selected accommodations for your trip"
        },
        "cost": {
            "title": "💰 Detailed Cost Breakdown",
            "icon": "💰",
            "card_class": "cost-card",
            "description": "Complete budget analysis and expense planning"
        },
        "weather": {
            "title": "🌤️ Weather & Climate Information",
            "icon": "🌤️",
            "card_class": "weather-card",
            "description": "Weather patterns and travel climate guidance"
        },
        "alternatives": {
            "title": "🔄 Alternative Travel Plans",
            "icon": "🔄",
            "card_class": "alternative-card",
            "description": "Different options and backup travel suggestions"
        }
    }
    
    config = content_config.get(content_type, content_config["complete"])
    
    # Header
    st.markdown(f"""
    <div class="content-card">
        <div class="content-header">
            <h1>{config['icon']} {config['title']}</h1>
            <p style="font-size: 1.1rem; opacity: 0.9; margin-top: 1rem;">
                {config['description']}
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Process and display content
    processed_content = extract_price_ranges(data)
    
    if content_type == "complete":
        display_formatted_itinerary(processed_content)
    elif content_type == "cost":
        display_formatted_cost_breakdown(processed_content)
    else:
        # Generic content display
        st.markdown(f"""
        <div class="{config['card_class']}">
            <div style="line-height: 1.8; font-size: 1.1rem;">
                {processed_content.replace(chr(10), '<br><br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_formatted_itinerary(content: str):
    """Display formatted itinerary with day sections"""
    lines = content.split('\n')
    current_day = None
    current_content = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a day header
        if re.match(r'Day \d+', line, re.IGNORECASE):
            # Save previous day if exists
            if current_day and current_content:
                st.markdown(f"""
                <div class="itinerary-card">
                    <div class="day-header">{current_day}</div>
                    <div class="day-content">
                        {'<br>'.join(current_content)}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            current_day = line
            current_content = []
        else:
            if line:
                current_content.append(line)
    
    # Add the last day
    if current_day and current_content:
        st.markdown(f"""
        <div class="itinerary-card">
            <div class="day-header">{current_day}</div>
            <div class="day-content">
                {'<br>'.join(current_content)}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # If no day structure found, display as is
    if not current_day:
        st.markdown(f"""
        <div class="itinerary-card">
            <div style="line-height: 1.8; font-size: 1.1rem;">
                {content.replace(chr(10), '<br><br>')}
            </div>
        </div>
        """, unsafe_allow_html=True)

def display_formatted_cost_breakdown(content: str):
    """Display formatted cost breakdown"""
    st.markdown(f"""
    <div class="cost-card">
        <div style="line-height: 1.8; font-size: 1.1rem;">
            {content.replace(chr(10), '<br><br>')}
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    """Main application function"""
    try:
        # Initialize everything
        initialize_page_config()
        load_custom_css()
        init_session_state()
        
        # Handle different views
        if st.session_state.current_view == "main":
            # Display welcome screen
            display_welcome_screen()
            
            # Chat section
            st.markdown("### 💬 Plan Your Perfect Trip")
            st.markdown("---")
            
            # Input section
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    user_input = st.text_input(
                        "",
                        placeholder="Where would you like to travel? e.g., 'Plan a 5-day romantic trip to Paris for 2 people'",
                        key="travel_input",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    send_button = st.button("🚀 Plan Trip", use_container_width=True)
            
            # Example prompts
            st.markdown("#### 💡 Try these examples:")
            example_col1, example_col2, example_col3 = st.columns(3)
            
            examples = [
                ("🏖️ Beach vacation in Goa", "Plan a 7-day beach vacation in Goa for 2 people with water sports and local cuisine"),
                ("🏔️ Adventure in Nepal", "Plan a 10-day adventure trip to Nepal including trekking and cultural sites for 3 people"),
                ("🏛️ Cultural tour of Rajasthan", "Plan a 5-day cultural heritage tour of Rajasthan covering palaces and forts for a family of 4")
            ]
            
            for i, (button_text, query) in enumerate(examples):
                with [example_col1, example_col2, example_col3][i]:
                    if st.button(button_text, use_container_width=True):
                        st.session_state.user_query = query
                        st.session_state.current_view = "menu"
                        # Get initial travel data
                        with st.spinner("🧠 Preparing your travel options..."):
                            response_data = make_api_request(query, "complete")
                            if response_data:
                                st.session_state.travel_data = response_data.get("answer", "")
                        st.rerun()
            
            # Process user input
            if send_button and user_input and user_input.strip():
                st.session_state.user_query = user_input.strip()
                st.session_state.current_view = "menu"
                # Get initial travel data
                with st.spinner("🧠 Preparing your travel options..."):
                    response_data = make_api_request(user_input.strip(), "complete")
                    if response_data:
                        st.session_state.travel_data = response_data.get("answer", "")
                st.rerun()
        
        elif st.session_state.current_view == "menu":
            # Display the menu
            display_menu()
        
        elif st.session_state.current_view in ["complete", "hotels", "cost", "weather", "alternatives"]:
            # Handle loading state
            if st.session_state.loading:
                st.markdown("""
                <div class="content-card">
                    <div style="text-align: center; padding: 3rem;">
                        <div class="loading-spinner"></div>
                        <h3 style="margin-top: 1rem;">🧠 AI is preparing your detailed information...</h3>
                        <p>This may take a few moments</p>
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
                    st.error("❌ Failed to generate the requested information. Please try again.")
                    if st.button("← Back to Menu"):
                        st.session_state.current_view = "menu"
                        st.rerun()
            else:
                # This shouldn't happen, but just in case
                st.session_state.current_view = "menu"
                st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; opacity: 0.7; font-size: 0.9rem; padding: 1rem;'>"
            "Built with ❤️ using Streamlit & AI • "
            "<span style='opacity: 0.5;'>Navigate through different sections to explore your travel plan</span>"
            "</div>",
            unsafe_allow_html=True,
        )
        
    except Exception as e:
        logger.critical(f"Main app crash: {e}")
        st.error("🚨 Critical error: The application crashed.")
        
        # Reset button in case of crash
        if st.button("🔄 Reset Application"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()
    