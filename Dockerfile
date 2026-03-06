# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed (none currently required for this app)
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     curl \
#     && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose the default MCP port
EXPOSE 32123

# Set default environment variables
ENV SEARXNG_URL=http://localhost:8080
ENV MCP_PORT=32123
ENV MCP_HOST=0.0.0.0
ENV MCP_TRANSPORT=http

# Run the server
CMD ["python", "searxng_mcp.py"]
