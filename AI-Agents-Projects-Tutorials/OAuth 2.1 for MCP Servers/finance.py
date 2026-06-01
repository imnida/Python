from mcp.server.fastmcp import FastMCP
from typing import Any
import os
import httpx
from typing import Dict, List
from config import settings

# Create an MCP server
mcp = FastMCP("finance-news")

BASE_URL = "https://www.alphavantage.co/query"

async def call_alpha_vantage(endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
    """Generic async caller to Alpha Vantage."""
    params["apikey"] = settings.ALPHA_VANTAGE_API_KEY
    params["function"] = endpoint
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(BASE_URL, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception:
            return None

@mcp.tool()
async def get_news_sentiment(ticker: str) -> str:
    """Get news sentiment data for a stock ticker.

    Args:
        ticker: Stock ticker symbol (e.g., MSFT, AAPL)
    """
    data = await call_alpha_vantage("NEWS_SENTIMENT", {"tickers": ticker.upper()})
    if not data or "feed" not in data:
        return "Couldn't retrieve news sentiment."

    articles = data["feed"][:3]
    result = []
    for item in articles:
        result.append(f"""
    📰 {item['title']}
    Summary: {item['summary']}
    Source: {item['source']} | Published: {item['time_published']}
    """)
    return "\n---\n".join(result)