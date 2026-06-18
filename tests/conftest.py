"""
Pytest configuration and fixtures for the Mergington Activities API tests.

Provides:
- app_instance: Fresh FastAPI app with clean activities dict per test
- client: TestClient connected to app_instance
- setup_activities: Factory fixture to populate test data
"""
import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def app_instance():
    """
    Provide a fresh FastAPI app instance for each test.
    
    This fixture ensures that each test gets a clean slate, with no
    cross-test state pollution from previous registrations or activities.
    """
    # The app instance is created fresh for each test
    return app


@pytest.fixture
def client(app_instance):
    """
    Provide a TestClient connected to the app instance.
    
    TestClient simulates HTTP requests without running a server,
    making tests fast and allowing assertion on responses.
    """
    return TestClient(app_instance)


@pytest.fixture
def setup_activities(app_instance):
    """
    Factory fixture to pre-populate activities with test data.
    
    Usage:
        def test_full_activity(setup_activities, client):
            setup_activities({"Test Activity": {"max_participants": 2, "participants": ["alice@example.com"]}})
            response = client.post("/activities/Test Activity/signup?email=bob@example.com")
            assert response.status_code == 200
    """
    def _setup(activity_overrides=None):
        """
        Populate activities dict with test data.
        
        Args:
            activity_overrides: Dict mapping activity names to partial activity dicts
                               Merges with defaults.
        """
        from src.app import activities
        
        # Keep existing activities from app initialization
        if activity_overrides:
            activities.update(activity_overrides)
        
        return activities
    
    return _setup
