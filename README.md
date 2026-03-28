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

## MCP client config
```JSON
{
  "mcpServers": {
    "searxng": {
      "type": "http",
      "url": "http://localhost:32123/mcp"
    }
  }
}
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

# Windows Troubleshooting

## localhost not reachable while Docker container is running

**Symptom:** `http://localhost:<port>/` returns connection refused or hits the wrong service,
but `curl` from inside the container works fine.

**Root cause: WSL2 port relay ghost**

WSL2 automatically forwards ports from the Linux VM to the Windows host using `wslrelay.exe`.
When a process inside WSL listens on a port, WSL creates a relay bound to `[::1]:<port>`
(IPv6 loopback) on the Windows side.

When that WSL process stops, `wslrelay.exe` often **does not release the port**. The relay
entry stays alive as a zombie listener on `[::1]:<port>`.

Later, when Docker maps a container to the same host port, it binds correctly to
`0.0.0.0:<port>` — but `[::1]:<port>` is already taken by the stale relay.

On Windows, `localhost` resolves to `::1` (IPv6) first. So browser and curl requests to
`localhost:<port>` hit the dead `wslrelay.exe` entry instead of the Docker container,
resulting in a connection error or unexpected response.

Connecting via the explicit IPv4 address `127.0.0.1:<port>` bypasses the relay and reaches
Docker correctly.

**How to diagnose:**

```powershell
# Check what is listening on the port
netstat -ano | findstr :<port>

# Identify the processes
Get-Process -Id <pid1>,<pid2> | Select-Object Id,Name
```

If you see two entries for the same port — one owned by `com.docker.backend` and another
by `wslrelay` — this is the problem.

**Workarounds:**

| Option | Command | Notes |
|--------|---------|-------|
| Use IPv4 directly | `http://127.0.0.1:<port>/` | Immediate, no restart needed |
| Restart WSL | `wsl --shutdown` | Kills all stale relays; WSL restarts on next use |
| Remap Docker port | Change host port in `docker run -p` or `docker-compose.yml` | Avoids the conflict entirely |

**Permanent fix:**

After `wsl --shutdown`, restart the Docker container. The relay will no longer exist and
`localhost:<port>` will work normally until the same port is reused inside WSL again.

**Prevention:**

If you regularly run services on the same port both in WSL and in Docker, prefer one of:

- Always use Docker for that service, never WSL directly
- Use different ports for WSL dev and Docker prod instances
- Add `127.0.0.1:<port>:<port>` explicit binding in `docker-compose.yml` to force IPv4

---

## Related

- [WSL2 networking documentation](https://learn.microsoft.com/en-us/windows/wsl/networking)
- WSL GitHub issue tracker: search `wslrelay port leak`
