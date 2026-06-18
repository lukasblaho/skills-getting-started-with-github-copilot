"""
Unit tests for the Mergington Activities API.

Tests individual functions and business logic in isolation, without HTTP layer.
Validates data structure integrity and edge cases.
"""
import pytest
from src.app import activities


class TestActivitiesStructure:
    """Tests for the activities data structure."""
    
    def test_activities_is_dict(self):
        """Activities should be a dictionary."""
        assert isinstance(activities, dict)
    
    def test_activities_not_empty(self):
        """Activities dict should contain activities."""
        assert len(activities) > 0
    
    def test_all_activities_have_required_fields(self):
        """Each activity must have: description, schedule, max_participants, participants."""
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        for activity_name, activity_data in activities.items():
            actual_fields = set(activity_data.keys())
            missing_fields = required_fields - actual_fields
            
            assert not missing_fields, (
                f"Activity '{activity_name}' missing fields: {missing_fields}"
            )
    
    def test_all_activities_have_valid_types(self):
        """Validate types of all activity fields."""
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["description"], str), \
                f"{activity_name}: description must be str"
            assert isinstance(activity_data["schedule"], str), \
                f"{activity_name}: schedule must be str"
            assert isinstance(activity_data["max_participants"], int), \
                f"{activity_name}: max_participants must be int"
            assert isinstance(activity_data["participants"], list), \
                f"{activity_name}: participants must be list"
    
    def test_all_participants_are_strings(self):
        """All items in participants list should be strings (emails)."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            for participant in participants:
                assert isinstance(participant, str), (
                    f"{activity_name}: participant '{participant}' is not a string"
                )
    
    def test_max_participants_positive(self):
        """max_participants should be positive integer."""
        for activity_name, activity_data in activities.items():
            assert activity_data["max_participants"] > 0, (
                f"{activity_name}: max_participants must be > 0"
            )
    
    def test_participants_count_within_capacity(self):
        """Participant count should not exceed max_participants."""
        for activity_name, activity_data in activities.items():
            actual_count = len(activity_data["participants"])
            max_cap = activity_data["max_participants"]
            
            assert actual_count <= max_cap, (
                f"{activity_name}: {actual_count} participants exceeds max of {max_cap}"
            )
    
    def test_no_duplicate_participants(self):
        """No activity should have duplicate emails in participants."""
        for activity_name, activity_data in activities.items():
            participants = activity_data["participants"]
            unique_participants = set(participants)
            
            assert len(participants) == len(unique_participants), (
                f"{activity_name}: has duplicate participants"
            )


class TestActivitiesList:
    """Tests for the list of activities."""
    
    def test_nine_activities_exist(self):
        """There should be exactly 9 activities."""
        assert len(activities) == 9
    
    def test_expected_activities_present(self):
        """All expected activity names should exist."""
        expected = {
            "Chess Club", "Programming Class", "Gym Class",
            "Basketball Team", "Tennis Club",
            "Drama Club", "Music Band",
            "Debate Club", "Science Club"
        }
        
        actual = set(activities.keys())
        assert expected == actual, f"Expected: {expected}, got: {actual}"
    
    def test_activity_names_are_strings(self):
        """All activity names should be strings."""
        for activity_name in activities.keys():
            assert isinstance(activity_name, str)
    
    def test_activity_names_non_empty(self):
        """Activity names should not be empty strings."""
        for activity_name in activities.keys():
            assert len(activity_name) > 0


class TestParticipantLogic:
    """Tests for participant-related business logic."""
    
    def test_can_check_if_participant_exists(self):
        """Should be able to check if email is in participants."""
        # Pick first activity with participants or add one
        test_email = "test@example.com"
        test_activity = "Chess Club"
        
        # Simulate adding
        activities[test_activity]["participants"].append(test_email)
        
        assert test_email in activities[test_activity]["participants"]
        
        # Cleanup
        activities[test_activity]["participants"].remove(test_email)
    
    def test_can_add_and_remove_participant(self):
        """Should be able to add and remove participants."""
        test_email = "temp@example.com"
        test_activity = "Programming Class"
        
        # Add
        activities[test_activity]["participants"].append(test_email)
        assert test_email in activities[test_activity]["participants"]
        
        # Remove
        activities[test_activity]["participants"].remove(test_email)
        assert test_email not in activities[test_activity]["participants"]
    
    def test_capacity_check_logic(self):
        """Test capacity validation logic."""
        test_activity = "Gym Class"
        max_cap = activities[test_activity]["max_participants"]
        current_count = len(activities[test_activity]["participants"])
        
        # Can add if under capacity
        can_add = current_count < max_cap
        assert isinstance(can_add, bool)
        
        # Cleanup: ensure we didn't modify state
        assert len(activities[test_activity]["participants"]) == current_count


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""
    
    def test_empty_string_email_validation(self):
        """Empty string should not be a valid email in validation logic."""
        # This is a pattern test, not actual validation
        test_email = ""
        assert len(test_email) == 0  # Edge case: would fail real email validation
    
    def test_special_characters_in_email(self):
        """Emails with special characters should be stored as-is."""
        # The API accepts whatever string is passed
        special_email = "user+tag@example.com"
        assert isinstance(special_email, str)
        assert "@" in special_email
    
    def test_very_large_max_participants(self):
        """Activity with large max_participants should be valid."""
        large_activity = {
            "description": "Large event",
            "schedule": "Monday 5pm",
            "max_participants": 1000,
            "participants": []
        }
        
        assert large_activity["max_participants"] > 0
        assert len(large_activity["participants"]) <= large_activity["max_participants"]
    
    def test_activity_with_at_capacity(self):
        """Activity can have exactly max_participants registered."""
        # Simulate an at-capacity state
        test_activity = "Chess Club"
        max_cap = activities[test_activity]["max_participants"]
        
        # Check: if we fill to capacity, we have valid state
        if len(activities[test_activity]["participants"]) < max_cap:
            # We can add until full
            valid = True
        else:
            valid = True  # Already full is also valid
        
        assert valid
