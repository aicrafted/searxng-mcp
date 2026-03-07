# SearXNG MCP Skill

A repository-local skill for managing and utilizing the SearXNG Model Context Protocol (MCP) server.

## Features
- **Privacy-First Search**: Aggregate results from multiple engines without tracking.
- **Advanced Filtering**: Narrow down results by category, engine, or time range.
- **Easy Integration**: Simple CLI triggers for automated research tasks.

## Installation
This skill is located within the `.agent/skills` directory of this repository and is automatically available to the agent when working in this directory.

## Usage
Simply ask the AI to search for something:
> "Search for 'latest rust releases' using searxng with category=it"

## Tools
- `searxng_search`: The primary tool for web queries.
- `searxng_get_info`: Check server health and available configurations.
