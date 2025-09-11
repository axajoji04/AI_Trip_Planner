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
    TIMEOUT = int(os.getenv("TIMEOUT", "60"))  # Increased timeout for API calls
except Exception as e:
    logger.error(f"Configuration error: {e}")
    BASE_URL = "http://localhost:8000"
    EXCHANGE_API_URL = "https://api.exchangerate-api.com/v4/latest/USD"
    TIMEOUT = 60

def initialize_page_config():
    """Initialize page config safely"""
    try:
        st.set_page_config(
            page_title="🌍 AI Travel Companion",
            page_icon="✈️",
            layout="wide",
            initial_sidebar_state="collapsed",
        )
    except Exception as e:
        logger.warning(f"Page config already set: {e}")
        pass

def load_clean_custom_css():
    """Load clean CSS styling for professional presentation"""
    css_content = """
    <style>
        /* Hide default Streamlit elements */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Clean professional styling */
        .clean-content {
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            line-height: 1.8;
            color: #333;
            background: white;
            padding: 2rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        .clean-heading {
            font-family: 'Times New Roman', serif;
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0 15px 0;
            padding-bottom: 8px;
            border-bottom: 2px solid #007bff;
        }
        
        .clean-subheading {
            font-family: 'Times New Roman', serif;
            font-size: 16px;
            font-weight: 600;
            color: #34495e;
            margin: 15px 0 10px 0;
        }
        
        .clean-text {
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            line-height: 1.7;
            color: #2c3e50;
            margin: 10px 0;
        }
        
        .clean-day-section {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 5px;
        }
        
        .weather-section {
            background: linear-gradient(135deg, #74b9ff, #0984e3);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .hotel-section {
            background: linear-gradient(135deg, #fd79a8, #e84393);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .cost-section {
            background: linear-gradient(135deg, #55a3ff, #003d82);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .alternative-section {
            background: linear-gradient(135deg, #00b894, #00a085);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        .error-section {
            background: linear-gradient(135deg, #e17055, #d63031);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
            text-align: center;
        }
        
        .clean-button {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.7rem 1.5rem;
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s ease;
        }
        
        .clean-button:hover {
            background-color: #5a6268;
        }
        
        /* Simple header styling */
        .simple-header {
            text-align: center;
            padding: 1.5rem;
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        
        .simple-header h1 {
            font-family: 'Times New Roman', serif;
            font-size: 22px;
            margin: 0;
            font-weight: 600;
        }
        
        /* Clean list styling */
        .clean-list-item {
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            line-height: 1.6;
            color: #2c3e50;
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .clean-list-item::before {
            content: "🔸";
            position: absolute;
            left: 0;
        }
        
        /* Price highlighting */
        .price-highlight {
            background: #fff3cd;
            padding: 3px 6px;
            border-radius: 4px;
            font-weight: 600;
        }

        /* Main container styling - simplified */
        .main-container {
            background: linear-gradient(135deg, #667eea, #764ba2);
            color: white;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
        }
        
        /* Menu button styling - clean */
        .stButton > button {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 1rem 1.5rem;
            font-family: 'Times New Roman', serif;
            font-weight: normal;
            transition: all 0.3s ease;
            width: 100%;
            font-size: 15px;
        }
        
        .stButton > button:hover {
            background-color: #5a6268;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        
        /* Currency converter - clean */
        .currency-converter {
            background: linear-gradient(135deg, #fdcb6e, #e17055);
            color: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            text-align: center;
        }
        
        /* Loading spinner - clean */
        .loading-spinner {
            display: inline-block;
            width: 40px;
            height: 40px;
            border: 4px solid #dee2e6;
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        /* Retry button styling */
        .retry-button {
            background-color: #e74c3c;
            color: white;
            border: none;
            border-radius: 8px;
            padding: 1rem 2rem;
            font-family: 'Times New Roman', serif;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        .retry-button:hover {
            background-color: #c0392b;
            transform: translateY(-2px);
        }
    </style>
    """
    
    try:
        st.markdown(css_content, unsafe_allow_html=True)
    except Exception as e:
        logger.error(f"Clean CSS loading error: {e}")

def init_session_state():
    """Initialize session state variables safely"""
    try:
        if "current_view" not in st.session_state:
            st.session_state.current_view = "main"
        if "travel_data" not in st.session_state:
            st.session_state.travel_data = {}
        if "user_query" not in st.session_state:
            st.session_state.user_query = ""
        if "currency" not in st.session_state:
            st.session_state.currency = "USD"
        if "exchange_rates" not in st.session_state:
            st.session_state.exchange_rates = {}
        if "loading" not in st.session_state:
            st.session_state.loading = False
        if "retry_count" not in st.session_state:
            st.session_state.retry_count = 0
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

def make_api_request(user_input: str, request_type: str = "complete", retries: int = 3) -> Optional[Dict[Any, Any]]:
    """Make API request with comprehensive error handling and retries"""
    for attempt in range(retries):
        try:
            logger.info(f"Making request to {BASE_URL}/query (attempt {attempt + 1}/{retries})")
            
            # Modify the query based on request type
            modified_query = user_input
            if request_type == "hotels":
                modified_query = f"🏨 Provide detailed hotel and accommodation recommendations for: {user_input}. Include names, ratings, amenities, and pricing."
            elif request_type == "cost":
                modified_query = f"💰 Provide comprehensive cost breakdown and budget analysis for: {user_input}. Include all expenses with detailed pricing."
            elif request_type == "weather":
                modified_query = f"🌤️ Provide detailed weather information, climate details, and best travel times for: {user_input}. Include seasonal variations and weather recommendations."
            elif request_type == "alternatives":
                modified_query = f"🔄 Suggest comprehensive alternative travel plans, options, and backup suggestions for: {user_input}. Include different destinations, activities, and trip variations."
            
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
            elif response.status_code == 429:
                # Rate limit error - wait before retry
                wait_time = (attempt + 1) * 10  # Exponential backoff
                logger.warning(f"Rate limit hit, waiting {wait_time} seconds...")
                if attempt < retries - 1:  # Don't wait on last attempt
                    time.sleep(wait_time)
                    continue
                else:
                    return {"error": "rate_limit", "message": "Rate limit exceeded. Please try again in a few minutes."}
            elif response.status_code == 500:
                # Server error - try again after a short wait
                if attempt < retries - 1:
                    time.sleep(5)
                    continue
                else:
                    return {"error": "server_error", "message": "Server is experiencing issues. Please try again later."}
            else:
                error_msg = f"Server returned status {response.status_code}"
                if response.text:
                    error_msg += f": {response.text[:200]}"
                return {"error": "http_error", "message": error_msg}
                
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Connection error: {e}")
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return {"error": "connection", "message": "Unable to connect to the travel planning service."}
            
        except requests.exceptions.Timeout as e:
            logger.error(f"Timeout error: {e}")
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return {"error": "timeout", "message": f"Request took longer than {TIMEOUT} seconds."}
            
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            if attempt < retries - 1:
                time.sleep(5)
                continue
            return {"error": "unexpected", "message": str(e)[:200]}
    
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

def display_welcome_screen():
    """Display welcome screen"""
    try:
        st.markdown("""
        <div class="main-container">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 3rem; margin-bottom: 0.5rem;">🌍✈️</div>
                <div style="font-size: 2.5rem; font-weight: 600; margin-bottom: 0.5rem; font-family: 'Times New Roman', serif;">AI Travel Companion</div>
                <div style="font-size: 1.2rem; font-family: 'Times New Roman', serif;">Your intelligent travel planning assistant 🤖</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        features = [
            ("🎯 Interactive Menus", "Choose specific aspects of your trip to explore in detail"),
            ("💱 Currency Conversion", "Automatic price conversion to your preferred currency"),
            ("📋 Clean Presentation", "Professional, easy-to-read format for all travel information")
        ]
        
        for i, (title, description) in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="background: white; color: #2c3e50; border-radius: 10px; padding: 1.5rem; margin: 1rem; text-align: center; border: 1px solid #dee2e6; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                    <h4 style="font-family: 'Times New Roman', serif; margin-bottom: 1rem;">{title}</h4>
                    <p style="font-family: 'Times New Roman', serif; font-size: 14px;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        logger.error(f"Welcome screen error: {e}")
        st.title("🌍 AI Travel Companion")
        st.write("Your intelligent travel planning assistant 🤖")

def display_menu():
    """Display the interactive menu after getting travel data"""
    st.markdown(f"""
    <div class="simple-header">
        <h1>🎯 Choose What You'd Like to Explore</h1>
        <p style="font-size: 15px; margin-top: 1rem; font-family: 'Times New Roman', serif;">
            Your travel query: <strong>"{st.session_state.user_query}"</strong> ✨
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create menu grid
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    menu_options = [
        ("complete", "📅 Complete Itinerary", "Full day-by-day travel plan with activities", col1),
        ("hotels", "🏨 Hotel Recommendations", "Detailed accommodation options and reviews", col2),
        ("cost", "💰 Cost Breakdown", "Detailed budget analysis with price estimates", col3),
        ("weather", "🌤️ Weather Information", "Climate details and best travel times", col4),
        ("alternatives", "🔄 Alternative Plans", "Different options and backup suggestions", col5)
    ]
    
    for option_id, title, description, column in menu_options:
        with column:
            if st.button(f"{title}", key=f"menu_{option_id}", use_container_width=True):
                st.session_state.current_view = option_id
                st.session_state.loading = True
                st.session_state.retry_count = 0
                st.rerun()
    
    # Currency converter in the last column
    with col6:
        display_currency_converter_compact()

def display_currency_converter_compact():
    """Display compact currency converter"""
    st.markdown("""
    <div class="currency-converter">
        <h4 style="font-family: 'Times New Roman', serif; margin-bottom: 1rem;">💱 Currency</h4>
        <p style="font-family: 'Times New Roman', serif; font-size: 14px;">Prices shown in your preferred currency</p>
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

def display_error_with_retry(error_type: str, error_message: str, content_type: str):
    """Display error message with retry option"""
    error_emojis = {
        "rate_limit": "⏳",
        "server_error": "🔧",
        "connection": "🌐",
        "timeout": "⏰",
        "unexpected": "❌"
    }
    
    emoji = error_emojis.get(error_type, "❌")
    
    st.markdown(f"""
    <div class="error-section">
        <h2>{emoji} Oops! Something went wrong</h2>
        <p style="font-size: 16px; margin: 1rem 0;">{error_message}</p>
        <p style="font-size: 14px;">Don't worry, you can try again! 🔄</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("🔄 Try Again", key=f"retry_{content_type}", use_container_width=True):
            st.session_state.loading = True
            st.session_state.retry_count += 1
            st.rerun()
    
    # Back button
    if st.button("← Back to Menu", key=f"back_error_{content_type}"):
        st.session_state.current_view = "menu"
        st.session_state.retry_count = 0
        st.rerun()

def display_content_only(content_type: str, content: str):
    """Display ONLY the requested content without any extra elements"""
    
    # Content type styling and emojis
    section_styles = {
        "weather": ("weather-section", "🌤️"),
        "hotels": ("hotel-section", "🏨"),
        "cost": ("cost-section", "💰"),
        "alternatives": ("alternative-section", "🔄"),
        "complete": ("clean-content", "📅")
    }
    
    section_class, emoji = section_styles.get(content_type, ("clean-content", "📋"))
    
    # Clean and process content
    clean_data = clean_content_from_markdown(content)
    processed_content = extract_price_ranges(clean_data)
    
    # Display ONLY the content
    st.markdown(f"""
    <div class="{section_class}">
        <div class="clean-text">{processed_content.replace(chr(10), '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Menu", key=f"back_{content_type}", use_container_width=False):
        st.session_state.current_view = "menu"
        st.rerun()

def main():
    """Main application function"""
    try:
        # Initialize everything
        initialize_page_config()
        load_clean_custom_css()
        init_session_state()
        
        # Handle different views
        if st.session_state.current_view == "main":
            # Display welcome screen
            display_welcome_screen()
            
            # Chat section
            st.markdown("### 🗺️ Plan Your Perfect Trip")
            st.markdown("---")
            
            # Input section
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    user_input = st.text_input(
                        "",
                        placeholder="Where would you like to travel? e.g., 'Plan a 5-day romantic trip to Paris for 2 people' 💕",
                        key="travel_input",
                        label_visibility="collapsed"
                    )
                
                with col2:
                    send_button = st.button("🚀 Plan Trip", use_container_width=True)
            
            # Example prompts
            st.markdown("#### ✨ Try these examples:")
            example_col1, example_col2, example_col3 = st.columns(3)
            
            examples = [
                ("🏖️ Beach vacation in Goa", "Plan a 7-day beach vacation in Goa for 2 people with water sports and local cuisine"),
                ("🏔️ Adventure in Nepal", "Plan a 10-day adventure trip to Nepal including trekking and cultural sites for 3 people"),
                ("🏰 Cultural tour of Rajasthan", "Plan a 5-day cultural heritage tour of Rajasthan covering palaces and forts for a family of 4")
            ]
            
            for i, (button_text, query) in enumerate(examples):
                with [example_col1, example_col2, example_col3][i]:
                    if st.button(button_text, use_container_width=True):
                        st.session_state.user_query = query
                        st.session_state.current_view = "menu"
                        # Get initial travel data
                        with st.spinner("🔄 Preparing your travel options..."):
                            response_data = make_api_request(query, "complete")
                            if response_data and not response_data.get("error"):
                                st.session_state.travel_data["complete"] = response_data.get("answer", "")
                        st.rerun()
            
            # Process user input
            if send_button and user_input and user_input.strip():
                st.session_state.user_query = user_input.strip()
                st.session_state.current_view = "menu"
                # Get initial travel data
                with st.spinner("🔄 Preparing your travel options..."):
                    response_data = make_api_request(user_input.strip(), "complete")
                    if response_data and not response_data.get("error"):
                        st.session_state.travel_data["complete"] = response_data.get("answer", "")
                st.rerun()
        
        elif st.session_state.current_view == "menu":
            # Display the menu
            display_menu()
        
        elif st.session_state.current_view in ["complete", "hotels", "cost", "weather", "alternatives"]:
            # Handle loading state
            if st.session_state.loading:
                loading_messages = {
                    "weather": "🌤️ Gathering weather information...",
                    "hotels": "🏨 Finding the best accommodations...",
                    "cost": "💰 Calculating detailed costs...",
                    "alternatives": "🔄 Exploring alternative options...",
                    "complete": "📅 Creating your complete itinerary..."
                }
                
                st.markdown(f"""
                <div class="clean-content">
                    <div style="text-align: center; padding: 3rem;">
                        <div class="loading-spinner"></div>
                        <h3 style="margin-top: 1rem; font-family: 'Times New Roman', serif;">{loading_messages.get(st.session_state.current_view, "🤖 AI is working on your request...")}</h3>
                        <p style="font-family: 'Times New Roman', serif;">This may take a few moments ⏳</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Make API request for specific content
                response_data = make_api_request(st.session_state.user_query, st.session_state.current_view)
                st.session_state.loading = False
                
                if response_data and not response_data.get("error"):
                    # Store the data and display only the content
                    st.session_state.travel_data[st.session_state.current_view] = response_data.get("answer", "")
                    display_content_only(st.session_state.current_view, response_data.get("answer", ""))
                elif response_data and response_data.get("error"):
                    # Display error with retry option
                    display_error_with_retry(
                        response_data.get("error", "unknown"),
                        response_data.get("message", "An unknown error occurred"),
                        st.session_state.current_view
                    )
                else:
                    # Generic error
                    display_error_with_retry(
                        "unexpected",
                        "Failed to generate the requested information",
                        st.session_state.current_view
                    )
            else:
                # Display cached data if available
                if st.session_state.current_view in st.session_state.travel_data:
                    display_content_only(
                        st.session_state.current_view, 
                        st.session_state.travel_data[st.session_state.current_view]
                    )
                else:
                    # This shouldn't happen, but redirect to menu
                    st.session_state.current_view = "menu"
                    st.rerun()
        
        # Footer
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #6c757d; font-size: 14px; padding: 1rem; font-family: Times New Roman, serif;'>"
            "🚀 Built with Streamlit & AI • ✨ Navigate through different sections to explore your travel plan • 🌍 Happy Traveling!"
            "</div>",
            unsafe_allow_html=True,
        )
        
    except Exception as e:
        logger.critical(f"Main app crash: {e}")
        st.markdown("""
        <div class="error-section">
            <h2>💥 Critical Error</h2>
            <p>The application encountered an unexpected error and needs to restart.</p>
            <p>Don't worry, your data is safe! 🔒</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Reset button in case of crash
        if st.button("🔄 Reset Application"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()

    