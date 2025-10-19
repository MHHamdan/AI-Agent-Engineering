"""
Financial Data MCP Server

MCP server that provides real-time financial data including
cryptocurrency prices and stock market information. This server demonstrates
how to build production-ready MCP tools.
"""

from typing import Any, Dict, Optional
import httpx
import asyncio
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("financial-data-server")

# API Configuration
COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
ALPHA_VANTAGE_API_BASE = "https://www.alphavantage.co/query"
USER_AGENT = "Financial-Data-Server/1.0"

# Rate limiting configuration
REQUEST_TIMEOUT = 30.0
MAX_RETRIES = 3


async def make_api_request(url: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
    """
    Make an HTTP request with proper error handling and rate limiting.
    
    Args:
        url: The API endpoint URL
        params: Optional query parameters
        
    Returns:
        JSON response data or None if request fails
    """
    headers = {
        "User-Agent": USER_AGENT,
        "Accept": "application/json"
    }
    
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        for attempt in range(MAX_RETRIES):
            try:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:  # Rate limited
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                return None
            except Exception:
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(1)
                    continue
                return None
    return None


@mcp.tool()
async def get_cryptocurrency_price(symbol: str, currency: str = "usd") -> str:
    """
    Get current cryptocurrency price and market data.
    
    This tool provides real-time cryptocurrency pricing information using
    the CoinGecko API, which is free and doesn't require authentication.
    
    Args:
        symbol: Cryptocurrency symbol (e.g., 'bitcoin', 'ethereum', 'cardano')
        currency: Target currency for price display (default: 'usd')
        
    Returns:
        Formatted string with current price and market data
    """
    try:
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            return "Error: Invalid cryptocurrency symbol provided."
        
        symbol = symbol.lower().strip()
        currency = currency.lower().strip()
        
        # Make API request to CoinGecko
        url = f"{COINGECKO_API_BASE}/simple/price"
        params = {
            "ids": symbol,
            "vs_currencies": currency,
            "include_market_cap": "true",
            "include_24hr_change": "true",
            "include_24hr_vol": "true"
        }
        
        data = await make_api_request(url, params)
        
        if not data or symbol not in data:
            return f"Error: Cryptocurrency '{symbol}' not found. Please check the symbol and try again."
        
        crypto_data = data[symbol]
        
        # Format the response
        price = crypto_data.get(currency, 0)
        market_cap = crypto_data.get(f"{currency}_market_cap", 0)
        change_24h = crypto_data.get(f"{currency}_24h_change", 0)
        volume_24h = crypto_data.get(f"{currency}_24h_vol", 0)
        
        # Format numbers for display
        def format_number(num: float) -> str:
            if num >= 1e12:
                return f"${num/1e12:.2f}T"
            elif num >= 1e9:
                return f"${num/1e9:.2f}B"
            elif num >= 1e6:
                return f"${num/1e6:.2f}M"
            elif num >= 1e3:
                return f"${num/1e3:.2f}K"
            else:
                return f"${num:.2f}"
        
        result = f"""
        {symbol.upper()} Price Information
        {'='*40}
        Current Price: ${price:,.2f} {currency.upper()}
        Market Cap: {format_number(market_cap)}
        24h Change: {change_24h:+.2f}%
        24h Volume: {format_number(volume_24h)}

        Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        Data Source: CoinGecko API
        """.strip()
        
        return result
        
    except Exception as e:
        return f"Error retrieving cryptocurrency data: {str(e)}"


@mcp.tool()
async def get_company_profile(symbol: str) -> str:
    """
    Get comprehensive company profile information.
    
    This tool provides detailed company information using the free Alpha Vantage API,
    including business description, industry, market cap, and key financial metrics.
    This tool only work with the IBM stock symbol since it is the only one that is free to use.

    Args:
        symbol: Stock symbol (e.g., 'IBM')
        
    Returns:
        Formatted string with company profile information
    """
    try:
        # Validate inputs
        if not symbol or not isinstance(symbol, str):
            return "Error: Invalid stock symbol provided."
        
        symbol = symbol.upper().strip()
        
        # Make API request to Alpha Vantage for company overview
        url = ALPHA_VANTAGE_API_BASE
        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": "demo"  # Free tier API key
        }
        
        data = await make_api_request(url, params)
        
        if not data or 'Name' not in data:
            return f"Error: Company profile for '{symbol}' not found. Please check the symbol and try again."
        
        # Format the response
        name = data.get('Name', 'Unknown')
        description = data.get('Description', 'No description available')
        sector = data.get('Sector', 'Unknown')
        industry = data.get('Industry', 'Unknown')
        exchange = data.get('Exchange', 'Unknown')
        market_cap = data.get('MarketCapitalization', '0')
        pe_ratio = data.get('PERatio', 'N/A')
        peg_ratio = data.get('PEGRatio', 'N/A')
        dividend_yield = data.get('DividendYield', 'N/A')
        eps = data.get('EPS', 'N/A')
        beta = data.get('Beta', 'N/A')
        analyst_target_price = data.get('AnalystTargetPrice', 'N/A')
        
        # Format market cap
        def format_market_cap(cap_str: str) -> str:
            try:
                cap = float(cap_str)
                if cap >= 1e12:
                    return f"${cap/1e12:.2f}T"
                elif cap >= 1e9:
                    return f"${cap/1e9:.2f}B"
                elif cap >= 1e6:
                    return f"${cap/1e6:.2f}M"
                else:
                    return f"${cap:,.0f}"
            except:
                return cap_str
        
        result = f"""
        Company Profile: {name} ({symbol})
        {'='*50}
        Sector: {sector}
        Industry: {industry}
        Exchange: {exchange}
        Market Cap: {format_market_cap(market_cap)}

        Key Metrics:
        - P/E Ratio: {pe_ratio}
        - PEG Ratio: {peg_ratio}
        - Dividend Yield: {dividend_yield}
        - EPS: {eps}
        - Beta: {beta}
        - Analyst Target Price: ${analyst_target_price}

        Description: {description[:200]}{'...' if len(description) > 200 else ''}

        Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
        Data Source: Alpha Vantage API (Free Tier)
        """.strip()
        
        return result
        
    except Exception as e:
        return f"Error retrieving company profile: {str(e)}"


@mcp.tool()
async def get_crypto_market_overview(limit: int = 10) -> str:
    """
    Get overview of top cryptocurrencies by market capitalization.
    
    This tool provides a market overview showing the top cryptocurrencies
    with their current prices and market data.
    
    Args:
        limit: Number of cryptocurrencies to return (default: 10, max: 50)
        
    Returns:
        Formatted string with market overview
    """
    try:
        # Validate inputs
        if not isinstance(limit, int) or limit < 1 or limit > 50:
            return "Error: Limit must be an integer between 1 and 50."
        
        # Make API request to CoinGecko for market data
        url = f"{COINGECKO_API_BASE}/coins/markets"
        params = {
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "24h"
        }
        
        data = await make_api_request(url, params)
        
        if not data:
            return "Error: Unable to retrieve market data. Please try again later."
        
        # Format the response
        result = f"Top {limit} Cryptocurrencies by Market Cap\n"
        result += "=" * 50 + "\n\n"
        
        for i, crypto in enumerate(data, 1):
            name = crypto.get("name", "Unknown")
            symbol = crypto.get("symbol", "").upper()
            price = crypto.get("current_price", 0)
            market_cap = crypto.get("market_cap", 0)
            change_24h = crypto.get("price_change_percentage_24h", 0)
            
            # Format market cap
            if market_cap >= 1e12:
                market_cap_str = f"${market_cap/1e12:.2f}T"
            elif market_cap >= 1e9:
                market_cap_str = f"${market_cap/1e9:.2f}B"
            elif market_cap >= 1e6:
                market_cap_str = f"${market_cap/1e6:.2f}M"
            else:
                market_cap_str = f"${market_cap:,.0f}"
            
            change_indicator = "+" if change_24h >= 0 else "-"
            
            result += f"{i:2d}. {name} ({symbol})\n"
            result += f"    Price: ${price:,.2f} | Market Cap: {market_cap_str}\n"
            result += f"    24h Change: {change_indicator} {change_24h:+.2f}%\n\n"
        
        result += f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        result += "Data Source: CoinGecko API"
        
        return result
        
    except Exception as e:
        return f"Error retrieving market overview: {str(e)}"


if __name__ == "__main__":
    print("Financial Data MCP Server is running...")
    # Start the server
    mcp.run(transport='stdio')
