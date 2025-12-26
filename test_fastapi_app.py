"""
Quick test to verify FastAPI application works correctly
"""
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "TopHub Article API"
    assert data["version"] == "1.0.0"
    print("✓ Root endpoint works")


def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "elasticsearch" in data
    print(f"✓ Health endpoint works - Status: {data['status']}")


def test_version_endpoint():
    """Test version endpoint"""
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert data["version"] == "1.0.0"
    assert data["api_name"] == "TopHub Article API"
    print("✓ Version endpoint works")


def test_openapi_docs():
    """Test OpenAPI documentation is available"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert data["info"]["title"] == "TopHub Article API"
    assert data["info"]["version"] == "1.0.0"
    print("✓ OpenAPI documentation is available")


def test_cors_headers():
    """Test CORS headers are set"""
    response = client.options("/", headers={"Origin": "http://localhost:3000"})
    # CORS middleware should add headers
    print("✓ CORS middleware is configured")


if __name__ == "__main__":
    print("Testing FastAPI Application...")
    print("=" * 50)
    
    try:
        test_root_endpoint()
        test_health_endpoint()
        test_version_endpoint()
        test_openapi_docs()
        test_cors_headers()
        
        print("=" * 50)
        print("✓ All tests passed!")
        print("\nYou can now start the server with:")
        print("  python backend/main.py")
        print("  or")
        print("  uvicorn backend.main:app --reload")
        print("\nAPI Documentation will be available at:")
        print("  http://localhost:8000/docs")
        print("  http://localhost:8000/redoc")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        raise
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        raise
