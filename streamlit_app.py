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
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin: 20px 0 10px 0;
            padding-bottom: 5px;
            border-bottom: 1px solid #eee;
        }
        
        .clean-subheading {
            font-family: 'Times New Roman', serif;
            font-size: 15px;
            font-weight: 600;
            color: #34495e;
            margin: 15px 0 8px 0;
        }
        
        .clean-text {
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            line-height: 1.7;
            color: #2c3e50;
            margin: 8px 0;
        }
        
        .clean-day-section {
            background: #f8f9fa;
            border-left: 4px solid #007bff;
            padding: 1.5rem;
            margin: 1rem 0;
            border-radius: 5px;
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
            background: #f8f9fa;
            border-radius: 10px;
            margin-bottom: 2rem;
            border: 1px solid #dee2e6;
        }
        
        .simple-header h1 {
            font-family: 'Times New Roman', serif;
            font-size: 20px;
            color: #2c3e50;
            margin: 0;
            font-weight: 600;
        }
        
        /* Clean list styling */
        .clean-list-item {
            font-family: 'Times New Roman', serif;
            font-size: 14px;
            line-height: 1.6;
            color: #2c3e50;
            margin: 5px 0;
            padding-left: 20px;
            position: relative;
        }
        
        .clean-list-item::before {
            content: "•";
            position: absolute;
            left: 0;
            color: #007bff;
        }
        
        /* Price highlighting */
        .price-highlight {
            background: #fff3cd;
            padding: 2px 4px;
            border-radius: 3px;
            font-weight: 600;
        }

        /* Main container styling - simplified */
        .main-container {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 2rem;
            margin: 1rem 0;
            border: 1px solid #dee2e6;
        }
        
        /* Menu button styling - clean */
        .stButton > button {
            background-color: #6c757d;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 0.7rem 1.5rem;
            font-family: 'Times New Roman', serif;
            font-weight: normal;
            transition: background-color 0.3s ease;
            width: 100%;
        }
        
        .stButton > button:hover {
            background-color: #5a6268;
        }
        
        /* Currency converter - clean */
        .currency-converter {
            background: #e9ecef;
            border-radius: 10px;
            padding: 1.5rem;
            margin: 1rem 0;
            color: #2c3e50;
            text-align: center;
            border: 1px solid #dee2e6;
        }
        
        /* Loading spinner - clean */
        .loading-spinner {
            display: inline-block;
            width: 30px;
            height: 30px;
            border: 3px solid #dee2e6;
            border-radius: 50%;
            border-top-color: #007bff;
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
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

def display_welcome_screen():
    """Display welcome screen"""
    try:
        st.markdown("""
        <div class="main-container">
            <div style="text-align: center; color: #2c3e50; margin-bottom: 2rem;">
                <div style="font-size: 2.5rem; font-weight: 600; margin-bottom: 0.5rem; font-family: 'Times New Roman', serif;">AI Travel Companion</div>
                <div style="font-size: 1.1rem; color: #6c757d; font-family: 'Times New Roman', serif;">Your intelligent travel planning assistant</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Feature cards
        col1, col2, col3 = st.columns(3)
        
        features = [
            ("Interactive Menus", "Choose specific aspects of your trip to explore in detail"),
            ("Currency Conversion", "Automatic price conversion to your preferred currency"),
            ("Clean Presentation", "Professional, easy-to-read format for all travel information")
        ]
        
        for i, (title, description) in enumerate(features):
            with [col1, col2, col3][i]:
                st.markdown(f"""
                <div style="background: #f8f9fa; border-radius: 10px; padding: 1.5rem; margin: 1rem; text-align: center; color: #2c3e50; border: 1px solid #dee2e6;">
                    <h4 style="font-family: 'Times New Roman', serif; margin-bottom: 1rem;">{title}</h4>
                    <p style="font-family: 'Times New Roman', serif; font-size: 14px;">{description}</p>
                </div>
                """, unsafe_allow_html=True)
                
    except Exception as e:
        logger.error(f"Welcome screen error: {e}")
        st.title("AI Travel Companion")
        st.write("Your intelligent travel planning assistant")

def display_menu():
    """Display the interactive menu after getting travel data"""
    st.markdown(f"""
    <div class="simple-header">
        <h1>Choose What You'd Like to Explore</h1>
        <p style="font-size: 14px; margin-top: 1rem; font-family: 'Times New Roman', serif;">
            Your travel query: <strong>"{st.session_state.user_query}"</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create menu grid
    col1, col2 = st.columns(2)
    col3, col4 = st.columns(2)
    col5, col6 = st.columns(2)
    
    menu_options = [
        ("complete", "Complete Itinerary", "Full day-by-day travel plan with activities", col1),
        ("hotels", "Hotel Recommendations", "Detailed accommodation options and reviews", col2),
        ("cost", "Cost Breakdown", "Detailed budget analysis with price estimates", col3),
        ("weather", "Weather Information", "Climate details and best travel times", col4),
        ("alternatives", "Alternative Plans", "Different options and backup suggestions", col5)
    ]
    
    for option_id, title, description, column in menu_options:
        with column:
            if st.button(f"{title}", key=f"menu_{option_id}", use_container_width=True):
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
        <h4 style="font-family: 'Times New Roman', serif; margin-bottom: 1rem;">Currency</h4>
        <p style="font-family: 'Times New Roman', serif; font-size: 14px;">Prices shown in your preferred currency</p>
    </div>
    """, unsafe_allow_html=True)
    
    currencies = {
        "USD": "USD",
        "INR": "INR", 
        "EUR": "EUR",
        "GBP": "GBP",
        "AUD": "AUD",
        "CAD": "CAD",
        "JPY": "JPY"
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

def display_clean_itinerary(content: str):
    """Display itinerary in clean format"""
    lines = content.split('\n')
    current_section = []
    sections = []
    
    for line in lines:
        line = line.strip()
        if not line:
            if current_section:
                sections.append('\n'.join(current_section))
                current_section = []
            continue
        current_section.append(line)
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    for section in sections:
        if not section.strip():
            continue
            
        # Check if it's a day section
        if re.match(r'Day \d+', section, re.IGNORECASE):
            lines = section.split('\n')
            day_title = lines[0]
            day_content = '\n'.join(lines[1:]) if len(lines) > 1 else ""
            
            st.markdown(f"""
            <div class="clean-day-section">
                <div class="clean-heading">{day_title}</div>
                <div class="clean-text">{day_content.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # Regular content section
            st.markdown(f"""
            <div class="clean-content">
                <div class="clean-text">{section.replace(chr(10), '<br>')}</div>
            </div>
            """, unsafe_allow_html=True)

def display_clean_generic_content(content: str):
    """Display generic content in clean format"""
    st.markdown(f"""
    <div class="clean-content">
        <div class="clean-text">{content.replace(chr(10), '<br>')}</div>
    </div>
    """, unsafe_allow_html=True)

def display_clean_content_page(content_type: str, data: str):
    """Display content in clean Times New Roman format"""
    
    # Back button
    if st.button("← Back to Menu", key="back_button", use_container_width=False):
        st.session_state.current_view = "menu"
        st.rerun()
    
    # Content titles
    titles = {
        "complete": "Complete Travel Itinerary",
        "hotels": "Hotel Recommendations", 
        "cost": "Cost Breakdown",
        "weather": "Weather Information",
        "alternatives": "Alternative Plans"
    }
    
    title = titles.get(content_type, "Travel Information")
    
    # Simple header
    st.markdown(f"""
    <div class="simple-header">
        <h1>{title}</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Clean and process content
    clean_data = clean_content_from_markdown(data)
    processed_content = extract_price_ranges(clean_data)
    
    # Display content in clean format
    if content_type == "complete":
        display_clean_itinerary(processed_content)
    else:
        display_clean_generic_content(processed_content)

def display_content_page(content_type: str, data: str):
    """Display specific content page with back button - CLEAN VERSION"""
    display_clean_content_page(content_type, data)

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
            st.markdown("### Plan Your Perfect Trip")
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
                    send_button = st.button("Plan Trip", use_container_width=True)
            
            # Example prompts
            st.markdown("#### Try these examples:")
            example_col1, example_col2, example_col3 = st.columns(3)
            
            examples = [
                ("Beach vacation in Goa", "Plan a 7-day beach vacation in Goa for 2 people with water sports and local cuisine"),
                ("Adventure in Nepal", "Plan a 10-day adventure trip to Nepal including trekking and cultural sites for 3 people"),
                ("Cultural tour of Rajasthan", "Plan a 5-day cultural heritage tour of Rajasthan covering palaces and forts for a family of 4")
            ]
            
            for i, (button_text, query) in enumerate(examples):
                with [example_col1, example_col2, example_col3][i]:
                    if st.button(button_text, use_container_width=True):
                        st.session_state.user_query = query
                        st.session_state.current_view = "menu"
                        # Get initial travel data
                        with st.spinner("Preparing your travel options..."):
                            response_data = make_api_request(query, "complete")
                            if response_data:
                                st.session_state.travel_data = response_data.get("answer", "")
                        st.rerun()
            
            # Process user input
            if send_button and user_input and user_input.strip():
                st.session_state.user_query = user_input.strip()
                st.session_state.current_view = "menu"
                # Get initial travel data
                with st.spinner("Preparing your travel options..."):
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
                <div class="clean-content">
                    <div style="text-align: center; padding: 3rem;">
                        <div class="loading-spinner"></div>
                        <h3 style="margin-top: 1rem; font-family: 'Times New Roman', serif;">AI is preparing your detailed information...</h3>
                        <p style="font-family: 'Times New Roman', serif;">This may take a few moments</p>
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
                    st.error("Failed to generate the requested information. Please try again.")
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
            "<div style='text-align: center; color: #6c757d; font-size: 14px; padding: 1rem; font-family: Times New Roman, serif;'>"
            "Built with Streamlit & AI • Navigate through different sections to explore your travel plan"
            "</div>",
            unsafe_allow_html=True,
        )
        
    except Exception as e:
        logger.critical(f"Main app crash: {e}")
        st.error("Critical error: The application crashed.")
        
        # Reset button in case of crash
        if st.button("Reset Application"):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()


if __name__ == "__main__":
    main()

    