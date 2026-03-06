#!/usr/bin/env python3
"""
SearXNG MCP Server.

Provides a search tool that integrates with a local SearXNG instance.
"""

import os
import json
import logging
import httpx
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("searxng_mcp", stateless_http=True, json_response=True, streamable_http_path="/")

# Configuration
SEARXNG_URL = os.environ.get("SEARXNG_URL", "http://localhost:8080").rstrip("/")
DEFAULT_PORT = int(os.environ.get("MCP_PORT", "8000"))
DEFAULT_HOST = os.environ.get("MCP_HOST", "127.0.0.1")
DEFAULT_TRANSPORT = os.environ.get("MCP_TRANSPORT", "stdio").lower()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("searxng_mcp")

class ResponseFormat(str, Enum):
    """Output format for search results."""
    MARKDOWN = "markdown"
    JSON = "json"

class SearchInput(BaseModel):
    """Input parameters for SearXNG search."""
    model_config = ConfigDict(str_strip_whitespace=True)

    query: str = Field(..., description="Search query")
    categories: Optional[str] = Field(None, description="Comma-separated list of categories (e.g., 'general,news')")
    engines: Optional[str] = Field(None, description="Comma-separated list of engines to use")
    language: Optional[str] = Field("en", description="Search language (e.g., 'en', 'es')")
    pageno: int = Field(1, description="Page number", ge=1)
    time_range: Optional[str] = Field(None, description="Time range (e.g., 'day', 'month', 'year')")
    response_format: ResponseFormat = Field(ResponseFormat.MARKDOWN, description="Format of the tool output")

@mcp.tool(
    name="searxng_search",
    annotations={
        "title": "SearXNG Web Search",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def searxng_search(
    query: str,
    categories: Optional[str] = None,
    engines: Optional[str] = None,
    language: str = "en",
    pageno: int = 1,
    time_range: Optional[str] = None,
    response_format: ResponseFormat = ResponseFormat.MARKDOWN
) -> str:
    """
    Perform a web search using SearXNG.

    Args:
        query: Search query
        categories: Comma-separated list of categories (e.g., 'general,news')
        engines: Comma-separated list of engines to use
        language: Search language (e.g., 'en', 'es')
        pageno: Page number (starts at 1)
        time_range: Time range (e.g., 'day', 'month', 'year')
        response_format: Format of the tool output (markdown or json)

    Returns:
        Formatted search results or error message.
    """
    url = f"{SEARXNG_URL}/search"
    
    query_params = {
        "q": query,
        "format": "json",
        "pageno": pageno,
        "language": language
    }
    
    if categories:
        query_params["categories"] = categories
    if engines:
        query_params["engines"] = engines
    if time_range:
        query_params["time_range"] = time_range

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url, params=query_params)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if not results:
            return f"No results found for query: '{query}'"

        if response_format == ResponseFormat.JSON:
            return json.dumps(data, indent=2)

        # Markdown formatting
        lines = [f"# Search Results for: {query}", ""]
        for result in results[:10]: # Limit to top 10 for context efficiency
            title = result.get("title", "No Title")
            link = result.get("url", "#")
            snippet = result.get("content", "").replace("\n", " ")
            lines.append(f"### [{title}]({link})")
            if snippet:
                lines.append(snippet)
            lines.append("")
        
        return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        return f"Error: SearXNG API request failed with status {e.response.status_code}. Make sure SearXNG is running at {SEARXNG_URL}"
    except Exception as e:
        logger.error("Search error: %s", str(e))
        return f"Error: An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="SearXNG MCP Server")
    parser.add_argument("--searxng", default=SEARXNG_URL, help="SearXNG url")
    parser.add_argument("--transport", default=DEFAULT_TRANSPORT, choices=["stdio", "sse", "http"], help="Transport type (stdio, sse, http)")
    parser.add_argument("--host", default=DEFAULT_HOST, help="Host to bind to for mcp network transports")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port for mcp network transports")
    
    args = parser.parse_args()
    
    # Configure settings
    mcp.settings.host = args.host
    mcp.settings.port = args.port
    
    # Map 'http' to 'streamable-http' as required by FastMCP
    transport = args.transport
    if transport == "http":
        transport = "streamable-http"
    
    logger.info("Starting SearXNG MCP Server")
    logger.info("Transport: %s", transport)
    
    if transport != "stdio":
        logger.info("Bind address: %s:%s", args.host, args.port)

    logger.info("Running in %s mode", transport)
    try:
        mcp.run(transport=transport)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error("Server error: %s", str(e))
