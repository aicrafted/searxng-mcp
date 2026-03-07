---
name: searxng-mcp
description: "Repository-local integration skill for SearXNG MCP server. Enables privacy-respecting web search, engine discovery, and advanced query filtering."
category: tool
risk: safe
source: local
tags: "[search, privacy, searxng, mcp-server]"
date_added: "2026-03-07"
---

# searxng-mcp

## Purpose

To provide a powerful, privacy-focused search capability using a local SearXNG instance. This skill enables agents to perform web searches, explore available engines, and refine results using categories and time ranges.

## When to Use This Skill

- When a web search is needed to gather information.
- When you need to verify if a SearXNG instance is running correctly.
- When you want to discover which search engines or categories are available on the server.
- When you need to refine search results by time (e.g., day, month) or specific domains (e.g., news, science).

## Available Tools

### `searxng_search`
Perform a web search through the SearXNG backend.

**Arguments:**
- `query` (required): The search terms.
- `categories` (optional): Comma-separated list (e.g., `news,it`). Default: `general`.
- `engines` (optional): Comma-separated list of engines to use.
- `language` (optional): Search language (e.g., `en-US`).
- `pageno` (optional): Page number for results.
- `time_range` (optional): Filter results by `day`, `month`, or `year`.
- `response_format` (optional): Choose between `markdown` or `json`.

### `searxng_get_info`
Retrieve diagnostic information about the SearXNG instance.

**Returns:**
- A JSON object listing available categories, instance URL, and active engines (if stats are enabled).

## Best Practices

1. **Use Specific Categories**: If searching for news, use `categories="news"` to improve relevance.
2. **Context Efficiency**: The tool limits Markdown output to the top 10 results to save token space.
3. **Health Check**: If the search fails, use `searxng_get_info` to verify the server status and connection URL.
4. **Time Range Filtering**: Use `time_range="day"` for breaking news or recent software updates.

## Triggers
- "search for [topic] using searxng"
- "find recent news about [topic]"
- "check searxng server status"
- "what search engines are available?"
