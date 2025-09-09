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
        def convert_currency(amount: float, from_currency: str, to_currency: str):
            return self.currency_service.convert(amount, from_currency, to_currency)
        
        return [convert_currency]
