"""
Integration tests for the Mergington Activities API.

Tests full HTTP request/response cycles via TestClient, validating:
- Endpoint status codes and response format
- Error handling (404, 400, 422)
- Data integrity (participants list, capacity)
- State changes after operations

Tests follow the AAA (Arrange-Act-Assert) pattern:
- Arrange: Set up test data and initial state
- Act: Execute the HTTP request
- Assert: Verify the response and side effects
"""
import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint."""
    
    def test_get_activities_returns_200(self, client):
        """GET /activities should return 200 OK."""
        # Arrange: No setup needed for read-only operation
        
        # Act
        response = client.get("/activities")
        
        # Assert
        assert response.status_code == 200
    
    def test_get_activities_returns_dict(self, client):
        """GET /activities should return a JSON dict (not array)."""
        # Arrange: No setup needed
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
    
    def test_get_activities_contains_all_activities(self, client):
        """GET /activities should contain all 9 default activities."""
        # Arrange
        expected_activities = [
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club",
            "Drama Club", "Music Band",
            "Debate Club", "Science Club"
        ]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name in expected_activities:
            assert activity_name in data, f"Missing activity: {activity_name}"
    
    def test_get_activities_has_activity_details(self, client):
        """Each activity should have description, schedule, max_participants, participants."""
        # Arrange: Define required fields
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert: Check structure and types
        for activity_name, details in data.items():
            for field in required_fields:
                assert field in details, f"{activity_name} missing '{field}'"
            
            assert isinstance(details["participants"], list), \
                f"{activity_name} participants not a list"


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint."""
    
    def test_signup_success_returns_200(self, client):
        """Successful signup should return 200 OK."""
        response = client.post("/activities/Chess Club/signup?email=alice@example.com")
        assert response.status_code == 200
    
    def test_signup_success_returns_message(self, client):
        """Successful signup should return message in response."""
        response = client.post("/activities/Chess Club/signup?email=alice@example.com")
        data = response.json()
        
        assert "message" in data
        assert "alice@example.com" in data["message"]
        assert "Chess Club" in data["message"]
    
    def test_signup_adds_email_to_participants(self, client):
        """After successful signup, email should appear in participants list."""
        email = "bob@example.com"
        activity = "Programming Class"
        
        # Sign up
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Verify in participants list
        response = client.get("/activities")
        data = response.json()
        assert email in data[activity]["participants"]
    
    def test_signup_nonexistent_activity_returns_404(self, client):
        """Signup to nonexistent activity should return 404."""
        response = client.post("/activities/Nonexistent Activity/signup?email=alice@example.com")
        assert response.status_code == 404
    
    def test_signup_nonexistent_activity_error_detail(self, client):
        """404 error should contain 'Activity not found' message."""
        response = client.post("/activities/Nonexistent Activity/signup?email=alice@example.com")
        data = response.json()
        
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    def test_signup_duplicate_email_returns_400(self, client):
        """Signing up same email twice should return 400."""
        email = "alice@example.com"
        activity = "Chess Club"
        
        # First signup
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 200
        
        # Duplicate signup
        response = client.post(f"/activities/{activity}/signup?email={email}")
        assert response.status_code == 400
    
    def test_signup_duplicate_email_error_detail(self, client):
        """400 error for duplicate should mention already registered."""
        email = "alice@example.com"
        activity = "Chess Club"
        
        # First signup
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Duplicate signup
        response = client.post(f"/activities/{activity}/signup?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "already" in data["detail"].lower() or "registered" in data["detail"].lower()
    
    def test_signup_full_activity_returns_400(self, client, setup_activities):
        """Signup to full activity (at max capacity) should return 400."""
        # Fill an activity to capacity
        activity = "Tennis Club"  # max_participants = 10
        
        # Get current max
        response = client.get("/activities")
        max_cap = response.json()[activity]["max_participants"]
        
        # Fill to capacity
        for i in range(max_cap):
            client.post(f"/activities/{activity}/signup?email=user{i}@example.com")
        
        # Try to overfill
        response = client.post(f"/activities/{activity}/signup?email=overfull@example.com")
        assert response.status_code == 400
    
    def test_signup_full_activity_error_detail(self, client):
        """400 error for full activity should mention 'full'."""
        activity = "Tennis Club"
        
        response = client.get("/activities")
        max_cap = response.json()[activity]["max_participants"]
        
        # Fill to capacity
        for i in range(max_cap):
            client.post(f"/activities/{activity}/signup?email=user{i}@example.com")
        
        response = client.post(f"/activities/{activity}/signup?email=overfull@example.com")
        data = response.json()
        
        assert "detail" in data
        assert "full" in data["detail"].lower()
    
    def test_signup_multiple_different_emails_success(self, client):
        """Multiple different emails should sign up successfully."""
        activity = "Gym Class"
        emails = ["alice@example.com", "bob@example.com", "charlie@example.com"]
        
        for email in emails:
            response = client.post(f"/activities/{activity}/signup?email={email}")
            assert response.status_code == 200
        
        # Verify all in participants
        response = client.get("/activities")
        data = response.json()
        for email in emails:
            assert email in data[activity]["participants"]


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint.
    
    Note: These tests are designed for when the backend endpoint is implemented.
    They follow the expected API contract based on frontend expectations.
    """
    
    def test_unregister_success_returns_200(self, client):
        """Successful unregister should return 200 OK."""
        # First sign up
        email = "alice@example.com"
        activity = "Chess Club"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Then unregister
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 200
    
    def test_unregister_success_returns_message(self, client):
        """Successful unregister should return success message."""
        email = "bob@example.com"
        activity = "Programming Class"
        client.post(f"/activities/{activity}/signup?email={email}")
        
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        data = response.json()
        
        assert "message" in data
        assert email in data["message"]
    
    def test_unregister_removes_from_participants(self, client):
        """After unregister, email should be removed from participants."""
        email = "charlie@example.com"
        activity = "Gym Class"
        
        # Sign up
        client.post(f"/activities/{activity}/signup?email={email}")
        
        # Verify present
        response = client.get("/activities")
        assert email in response.json()[activity]["participants"]
        
        # Unregister
        client.post(f"/activities/{activity}/unregister?email={email}")
        
        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()[activity]["participants"]
    
    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Unregister from nonexistent activity should return 404."""
        response = client.post("/activities/Fake Activity/unregister?email=alice@example.com")
        assert response.status_code == 404
    
    def test_unregister_email_not_registered_returns_400(self, client):
        """Unregister for email not in participants should return 400."""
        activity = "Chess Club"
        email = "notregistered@example.com"
        
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response.status_code == 400
    
    def test_unregister_email_not_registered_error_detail(self, client):
        """400 error should indicate email not registered."""
        activity = "Chess Club"
        email = "notregistered@example.com"
        
        response = client.post(f"/activities/{activity}/unregister?email={email}")
        data = response.json()
        
        assert "detail" in data
        assert "not registered" in data["detail"].lower() or "not found" in data["detail"].lower()
    
    def test_unregister_frees_up_capacity(self, client):
        """After unregister, freed capacity should allow new signup."""
        activity = "Tennis Club"
        response = client.get("/activities")
        max_cap = response.json()[activity]["max_participants"]
        
        # Fill to capacity
        emails = [f"user{i}@example.com" for i in range(max_cap)]
        for email in emails:
            client.post(f"/activities/{activity}/signup?email={email}")
        
        # Try to add one more (should fail)
        response = client.post(f"/activities/{activity}/signup?email=extra@example.com")
        assert response.status_code == 400
        
        # Unregister first email
        client.post(f"/activities/{activity}/unregister?email={emails[0]}")
        
        # Now signup should succeed
        response = client.post(f"/activities/{activity}/signup?email=extra@example.com")
        assert response.status_code == 200
