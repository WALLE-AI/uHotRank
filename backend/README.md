# Backend API Service

FastAPI-based backend service for TopHub article management and analysis.

## Overview

This backend service provides RESTful API endpoints for:
- Article management (list, detail, search, export)
- Crawler control (start, stop, status, history)
- Statistics and analytics (keywords, categories, sentiments, trends)
- Health monitoring

## Architecture

```
backend/
├── api/              # API route handlers
├── service/          # Business logic layer
├── schemas/          # Pydantic data models
├── db/              # Database access layer
├── agent/           # Crawler and analysis agents
├── llm/             # LLM integration
├── utils/           # Utility functions
├── config/          # Application configuration
└── main.py          # FastAPI application entry point
```

## Quick Start

### 1. Install Dependencies

```bash
# Using uv (recommended)
uv sync

# Or using pip
pip install -r requirements.txt
```

### 2. Configure Environment

Create a `.env` file in the project root:

```env
# Elasticsearch Configuration
ELASTICSEARCH_HOST=localhost
ELASTICSEARCH_PORT=9200
ELASTICSEARCH_INDEX=tophub_articles

# API Configuration
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

### 3. Start the Server

```bash
# Development mode with auto-reload
python backend/main.py

# Or using uvicorn directly
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI Schema: http://localhost:8000/openapi.json

## API Endpoints

### Articles

- `GET /api/articles` - Get paginated article list
- `GET /api/articles/{id}` - Get article details
- `POST /api/articles/search` - Search articles with filters
- `GET /api/articles/export` - Export articles (JSON/CSV/Excel)

### Crawler

- `POST /api/crawler/start` - Start crawler task
- `GET /api/crawler/status` - Get current crawler status
- `POST /api/crawler/stop` - Stop running crawler
- `GET /api/crawler/history` - Get crawler history

### Statistics

- `GET /api/statistics` - Get overall statistics
- `GET /api/statistics/keywords` - Get keyword statistics
- `GET /api/statistics/categories` - Get category distribution
- `GET /api/statistics/sentiments` - Get sentiment analysis
- `GET /api/statistics/sources` - Get source distribution
- `GET /api/statistics/trends` - Get time-series trends

### Health

- `GET /health` - Health check with dependency status
- `GET /version` - API version information

## Configuration

Configuration is managed through `backend/config/settings.py` using pydantic-settings.

### Available Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `API_TITLE` | "TopHub Article API" | API title |
| `API_VERSION` | "1.0.0" | API version |
| `CORS_ORIGINS` | ["http://localhost:3000", ...] | Allowed CORS origins |
| `ELASTICSEARCH_HOST` | "localhost" | Elasticsearch host |
| `ELASTICSEARCH_PORT` | 9200 | Elasticsearch port |
| `ELASTICSEARCH_INDEX` | "tophub_articles" | Index name |
| `LOG_LEVEL` | "INFO" | Logging level |
| `REQUEST_TIMEOUT` | 30 | Request timeout (seconds) |
| `MAX_REQUEST_SIZE` | 10MB | Maximum request size |

## Middleware

### CORS Middleware
- Allows cross-origin requests from configured origins
- Supports credentials
- Allows all HTTP methods and headers

### Request Middleware
- Logs all requests with timing information
- Enforces request size limits
- Adds `X-Process-Time` header to responses

### Exception Handlers
- Validates request data with detailed error messages (422)
- Catches and logs all unhandled exceptions (500)
- Hides sensitive error details in production

## Testing

### Run Quick Verification

```bash
python test_fastapi_app.py
```

### Run Full Test Suite

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=backend --cov-report=html

# Run specific test file
pytest test_services.py
```

## Development

### Adding New Endpoints

1. Create router in `backend/api/`
2. Implement service logic in `backend/service/`
3. Define Pydantic models in `backend/schemas/`
4. Register router in `backend/main.py`

### Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Add docstrings for all public APIs
- Keep functions focused and testable

## Deployment

### Using Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Using systemd

Create `/etc/systemd/system/tophub-api.service`:

```ini
[Unit]
Description=TopHub API Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000

[Install]
WantedBy=multi-user.target
```

## Monitoring

### Health Check

```bash
curl http://localhost:8000/health
```

### Logs

Logs are written to stdout/stderr with configurable format and level.

```bash
# View logs in development
tail -f logs/app.log

# View logs in production (systemd)
journalctl -u tophub-api -f
```

## Troubleshooting

### Elasticsearch Connection Failed

- Check Elasticsearch is running: `curl http://localhost:9200`
- Verify connection settings in `.env`
- Check network connectivity and firewall rules

### CORS Errors

- Add frontend origin to `CORS_ORIGINS` in settings
- Ensure origin includes protocol (http/https)
- Check browser console for specific CORS error

### Import Errors

- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.11+)
- Verify virtual environment is activated

## License

[Your License Here]

## Support

For issues and questions, please open an issue on GitHub or contact the development team.
