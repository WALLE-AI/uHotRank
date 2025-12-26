#!/usr/bin/env python
"""
Convenience script to start the FastAPI application
"""
import sys
import uvicorn
from backend.config.settings import settings


def main():
    """Start the FastAPI application"""
    print("=" * 80)
    print(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    print("=" * 80)
    print()
    print("📚 API Documentation:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("  - OpenAPI:    http://localhost:8000/openapi.json")
    print()
    print("🔍 Health Check:")
    print("  - Health:     http://localhost:8000/health")
    print("  - Version:    http://localhost:8000/version")
    print()
    print("⚙️  Configuration:")
    print(f"  - Elasticsearch: {settings.ELASTICSEARCH_HOST}:{settings.ELASTICSEARCH_PORT}")
    print(f"  - Index:         {settings.ELASTICSEARCH_INDEX}")
    print(f"  - Log Level:     {settings.LOG_LEVEL}")
    print(f"  - CORS Origins:  {', '.join(settings.CORS_ORIGINS)}")
    print()
    print("=" * 80)
    print()
    
    # Determine if we're in development mode
    dev_mode = "--dev" in sys.argv or "--reload" in sys.argv
    
    try:
        uvicorn.run(
            "backend.main:app",
            host="0.0.0.0",
            port=8000,
            reload=dev_mode,
            log_level=settings.LOG_LEVEL.lower(),
        )
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down gracefully...")
    except Exception as e:
        print(f"\n\n❌ Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
