import os
from langchain_tavily import TavilySearch

class TavilyPlaceSearchTool:
    """Searches for place information using TavilySearch API."""

    def __init__(self):
        pass

    def search_attractions(self, place: str) -> dict:
        """Search attractions in a place."""
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"Top attractive places in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def search_restaurants(self, place: str) -> dict:
        """Search restaurants in a place."""
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"Top 10 restaurants and eateries in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def search_activity(self, place: str) -> dict:
        """Search activities in a place."""
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"Activities in and around {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    def search_transportation(self, place: str) -> dict:
        """Search transportation modes in a place."""
        tavily_tool = TavilySearch(topic="general", include_answer="advanced")
        result = tavily_tool.invoke({"query": f"Different modes of transportation available in {place}"})
        if isinstance(result, dict) and result.get("answer"):
            return result["answer"]
        return result

    