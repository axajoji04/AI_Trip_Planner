import os
from utils.currency_converter import CurrencyConverter
from typing import List
from langchain.tools import tool
from dotenv import load_dotenv

class CurrencyConverterTool:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        api_key = os.getenv("EXCHANGE_RATE_API_KEY")
        if not api_key:
            raise ValueError("EXCHANGE_RATE_API_KEY not found! Check your .env file.")
        
        # Pass api_key correctly
        self.currency_service = CurrencyConverter(api_key)
        self.currency_converter_tool_list = self._setup_tools()

    def _setup_tools(self) -> List:
        @tool
        def convert_currency(amount: float, from_currency: str, to_currency: str) -> float:
            """
            Convert an amount from one currency to another using current exchange rates.
            
            Args:
                amount: The amount to convert
                from_currency: Source currency code (e.g., 'USD', 'EUR')
                to_currency: Target currency code (e.g., 'INR', 'GBP')
            
            Returns:
                The converted amount in the target currency
            """
            return self.currency_service.convert(amount, from_currency, to_currency)
        
        return [convert_currency]
    