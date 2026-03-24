# SearXNG MCP Server

A Model Context Protocol (MCP) server that provides web search capabilities by integrating with a SearXNG instance.

## Features

- **Web Search**: Perform powerful aggregated searches across multiple engines.
- **Discovery**: Programmatically retrieve available categories and engines.
- **Stateless HTTP**: Compatible with any standard JSON-RPC client.
- **Flexible Configuration**: Supports environment variables and command-line arguments.

## Example of compose.yml to run SearXNG with MCP server 

```yaml
services:
  searxng:
    image: searxng/searxng:latest
    ports:
      - 8080:8080
    volumes:
      - ./searxng/etc/:/etc/searxng/
      - ./searxng/data/:/var/cache/searxng/
    restart: always

  searxng-mcp:
    image: ghcr.io/aicrafted/searxng-mcp:latest
    restart: unless-stopped
    depends_on:
      # Ensure SearXNG starts before the MCP server
      - searxng
    environment:
      SEARXNG_URL: http://searxng:8080
      MCP_HOST: 0.0.0.0
      MCP_PORT: 32123
      MCP_TRANSPORT: "http"
    ports:
      - "32123:32123"
```

## Prerequisites for run from sources

- Python 3.10+
- A running [SearXNG](https://github.com/searxng/searxng) instance.

## Installation

1. Clone the repository and navigate to the directory.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up your `.env` file (optional):
   ```env
   SEARXNG_URL=http://your-searxng-instance:8080
   MCP_PORT=32123
   MCP_HOST=127.0.0.1
   ```

## Usage

Run the server using `uv` or standard python:

```bash
python searxng_mcp.py --transport http --port 32123 --searxng http://searx.lan
```

### Run with Docker

1. **Build the image**:
   ```bash
   docker build -t searxng-mcp .
   ```

2. **Run the container**:
   ```bash
   docker run -d \
     -p 32123:32123 \
     -e SEARXNG_URL=http://your-searxng-instance:8080 \
     --name searxng-mcp \
     searxng-mcp
   ```

### Transport Options
- `stdio`: Standard input/output (default for some MCP clients).
- `http`: Stateless HTTP (streamable-http).
- `sse`: Server-Sent Events.

---

# Search Abilities Guide

SearXNG aggregates results from various sources. This guide outlines the capabilities available through the `searxng_search` tool.

## Search Categories
Categories help refine your search by content type. Use these in the `categories` parameter (comma-separated).

| Category | Description |
| :--- | :--- |
| `general` | Default web search (Google, Brave, DuckDuckGo, etc.) |
| `images` | Image search results |
| `videos` | Video content from YouTube, Vimeo, etc. |
| `news` | Recent news articles |
| `map` | Geographical and map information |
| `it` | IT-related searches (StackOverflow, GitHub, etc.) |
| `science` | Scientific papers and articles (ArXiv, Google Scholar) |
| `files` | Torrent and file searches |
| `social_media` | Posts and profiles from social platforms |

## Supported Engines
SearXNG can query over 130 engines. Configured engines typically include:
- **Web**: Google, Brave, DuckDuckGo, Qwant, Startpage
- **Knowledge**: Wikipedia, Wikidata
- **Development**: GitHub, StackOverflow, PyPI
- **Social**: Reddit, Twitter/X

## Advanced Search Parameters
- **`categories`**: Filter by specific types (e.g., `news,it`).
- **`engines`**: Force specific engines (e.g., `google,wikipedia`).
- **`language`**: Specify search language (e.g., `en`, `es`, `fr`).
- **`pageno`**: Navigate through multiple pages of results.
- **`time_range`**: Filter by date (`day`, `month`, `year`).
- **`safesearch`**: Control content filtering (0=None, 1=Moderate, 2=Strict).

## Programmatic Discovery
Use the `searxng_get_info` tool to dynamically retrieve the list of enabled categories and engines from your instance.
