import pytest
from http import HTTPStatus


class TestUserCreation:
    """Test user creation functionality"""

    def test_create_user_returns_201_and_body(self, client):
        """Test creating a new user returns correct response"""
        payload = {
            "email": "test@example.com",
            "google_sub": "google123"
        }
        response = client.post("/api/v1/users", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        
        # Check required fields
        assert "id" in data
        assert data["email"] == "test@example.com"
        assert data["google_sub"] == "google123"

    def test_create_user_minimal_payload(self, client):
        """Test creating user with minimal required fields (email only)"""
        payload = {
            "email": "minimal@example.com"
        }
        response = client.post("/api/v1/users", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["email"] == "minimal@example.com"
        assert data["google_sub"] is None

    def test_create_user_validation_errors(self, client):
        """Test validation errors for invalid user data"""
        # Missing required email
        payload = {
            "google_sub": "google123"
        }
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Invalid email format
        payload = {
            "email": "not-an-email",
            "google_sub": "google123"
        }
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Email too long
        payload = {
            "email": "a" * 250 + "@example.com",  # Exceeds max_length=255
            "google_sub": "google123"
        }
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Google sub too long
        payload = {
            "email": "test@example.com",
            "google_sub": "a" * 129  # Exceeds max_length=128
        }
        response = client.post("/api/v1/users", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_create_user_duplicate_email(self, client):
        """Test creating user with duplicate email returns 400"""
        payload = {
            "email": "duplicate@example.com",
            "google_sub": "google123"
        }
        
        # Create first user
        response1 = client.post("/api/v1/users", json=payload)
        assert response1.status_code == HTTPStatus.CREATED
        
        # Try to create second user with same email
        response2 = client.post("/api/v1/users", json=payload)
        assert response2.status_code == HTTPStatus.BAD_REQUEST
        
        error_data = response2.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()


class TestUserRetrieval:
    """Test user retrieval functionality"""

    def test_get_user_by_id_returns_200(self, client):
        """Test retrieving user by ID"""
        # Create user first
        create_response = client.post("/api/v1/users", json={
            "email": "retrieve@example.com",
            "google_sub": "google456"
        })
        assert create_response.status_code == HTTPStatus.CREATED
        user_data = create_response.json()
        user_id = user_data["id"]

        # Retrieve by ID
        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert data["id"] == user_id
        assert data["email"] == "retrieve@example.com"
        assert data["google_sub"] == "google456"

    def test_get_user_not_found(self, client):
        """Test retrieving non-existent user returns 404"""
        response = client.get("/api/v1/users/99999")
        assert response.status_code == HTTPStatus.NOT_FOUND
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    def test_get_user_invalid_id(self, client):
        """Test retrieving user with invalid ID format"""
        response = client.get("/api/v1/users/not_a_number")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_list_users_empty_result(self, client):
        """Test listing users when no users exist"""
        response = client.get("/api/v1/users")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_users_with_data(self, client):
        """Test listing users returns all users"""
        # Create multiple users
        users_data = [
            {"email": "user1@example.com", "google_sub": "google1"},
            {"email": "user2@example.com", "google_sub": "google2"},
            {"email": "user3@example.com", "google_sub": "google3"}
        ]
        
        created_users = []
        for user_data in users_data:
            response = client.post("/api/v1/users", json=user_data)
            assert response.status_code == HTTPStatus.CREATED
            created_users.append(response.json())

        # List all users
        response = client.get("/api/v1/users")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        
        # Check that all created users are in the list
        user_ids = [user["id"] for user in data]
        for created_user in created_users:
            assert created_user["id"] in user_ids

    def test_list_users_with_email_filter(self, client):
        """Test listing users with email filter"""
        # Create users with different emails
        client.post("/api/v1/users", json={"email": "filter1@example.com"})
        client.post("/api/v1/users", json={"email": "filter2@example.com"})
        
        # Filter by specific email
        response = client.get("/api/v1/users?email=filter1@example.com")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["email"] == "filter1@example.com"

    def test_list_users_pagination(self, client):
        """Test pagination functionality"""
        # Create 5 users
        for i in range(5):
            client.post("/api/v1/users", json={
                "email": f"page{i}@example.com",
                "google_sub": f"google{i}"
            })

        # Test limit
        response = client.get("/api/v1/users?limit=3&offset=0")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 3

        # Test offset
        response = client.get("/api/v1/users?limit=3&offset=3")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2

    def test_list_users_pagination_validation(self, client):
        """Test pagination parameter validation"""
        # Invalid limit (too high)
        response = client.get("/api/v1/users?limit=300")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Invalid limit (too low)
        response = client.get("/api/v1/users?limit=0")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Invalid offset (negative)
        response = client.get("/api/v1/users?offset=-1")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUserUpdates:
    """Test user update functionality"""

    def test_update_user_partial(self, client):
        """Test partial update of user"""
        # Create user
        create_response = client.post("/api/v1/users", json={
            "email": "original@example.com",
            "google_sub": "original123"
        })
        user_id = create_response.json()["id"]

        # Partial update
        update_response = client.patch(f"/api/v1/users/{user_id}", json={
            "email": "updated@example.com"
        })
        
        assert update_response.status_code == HTTPStatus.OK
        data = update_response.json()
        
        assert data["email"] == "updated@example.com"
        assert data["google_sub"] == "original123"  # Should remain unchanged
        assert data["id"] == user_id

    def test_update_user_full(self, client):
        """Test full update of user"""
        # Create user
        create_response = client.post("/api/v1/users", json={
            "email": "old@example.com",
            "google_sub": "old123"
        })
        user_id = create_response.json()["id"]

        # Full update
        update_response = client.patch(f"/api/v1/users/{user_id}", json={
            "email": "new@example.com",
            "google_sub": "new456"
        })
        
        assert update_response.status_code == HTTPStatus.OK
        data = update_response.json()
        
        assert data["email"] == "new@example.com"
        assert data["google_sub"] == "new456"
        assert data["id"] == user_id

    def test_update_user_not_found(self, client):
        """Test updating non-existent user"""
        response = client.patch("/api/v1/users/99999", json={
            "email": "updated@example.com"
        })
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_user_invalid_data(self, client):
        """Test updating with invalid data"""
        # Create user
        create_response = client.post("/api/v1/users", json={
            "email": "test@example.com",
            "google_sub": "test123"
        })
        user_id = create_response.json()["id"]

        # Invalid email format
        response = client.patch(f"/api/v1/users/{user_id}", json={
            "email": "not-an-email"
        })
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Email too long
        response = client.patch(f"/api/v1/users/{user_id}", json={
            "email": "a" * 250 + "@example.com"
        })
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_update_user_duplicate_email(self, client):
        """Test updating user with email that already exists"""
        # Create two users
        user1_response = client.post("/api/v1/users", json={
            "email": "user1@example.com",
            "google_sub": "google1"
        })
        user2_response = client.post("/api/v1/users", json={
            "email": "user2@example.com",
            "google_sub": "google2"
        })
        
        user1_id = user1_response.json()["id"]
        user2_id = user2_response.json()["id"]

        # Try to update user1 with user2's email
        response = client.patch(f"/api/v1/users/{user1_id}", json={
            "email": "user2@example.com"
        })
        assert response.status_code == HTTPStatus.CONFLICT
        
        error_data = response.json()
        assert "detail" in error_data
        assert "already exists" in error_data["detail"].lower()

    def test_update_user_same_email(self, client):
        """Test updating user with the same email (should succeed)"""
        # Create user
        create_response = client.post("/api/v1/users", json={
            "email": "same@example.com",
            "google_sub": "same123"
        })
        user_id = create_response.json()["id"]

        # Update with same email
        update_response = client.patch(f"/api/v1/users/{user_id}", json={
            "email": "same@example.com",
            "google_sub": "updated123"
        })
        
        assert update_response.status_code == HTTPStatus.OK
        data = update_response.json()
        
        assert data["email"] == "same@example.com"
        assert data["google_sub"] == "updated123"


class TestUserDeletion:
    """Test user deletion functionality"""

    def test_delete_user(self, client):
        """Test deleting an existing user"""
        # Create user
        create_response = client.post("/api/v1/users", json={
            "email": "tobedeleted@example.com",
            "google_sub": "delete123"
        })
        user_id = create_response.json()["id"]

        # Delete user
        delete_response = client.delete(f"/api/v1/users/{user_id}")
        assert delete_response.status_code == HTTPStatus.NO_CONTENT
        
        # Verify deletion
        get_response = client.get(f"/api/v1/users/{user_id}")
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_not_found(self, client):
        """Test deleting non-existent user"""
        response = client.delete("/api/v1/users/99999")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_user_invalid_id(self, client):
        """Test deleting user with invalid ID format"""
        response = client.delete("/api/v1/users/not_a_number")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestUserEdgeCases:
    """Test edge cases and error scenarios"""

    def test_empty_request_body(self, client):
        """Test creating user with empty request body"""
        response = client.post("/api/v1/users", json={})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_malformed_json(self, client):
        """Test creating user with malformed JSON"""
        response = client.post("/api/v1/users", 
                             data="not json",
                             headers={"Content-Type": "application/json"})
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

    def test_extra_fields_ignored(self, client):
        """Test that extra fields in request are ignored"""
        payload = {
            "email": "extra@example.com",
            "google_sub": "extra123",
            "extra_field": "should_be_ignored"
        }
        response = client.post("/api/v1/users", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert "extra_field" not in data
        assert data["email"] == "extra@example.com"
        assert data["google_sub"] == "extra123"

    def test_case_sensitive_email(self, client):
        """Test that email addresses are case sensitive"""
        # Create user with lowercase email
        client.post("/api/v1/users", json={"email": "case@example.com"})
        
        # Try to create user with uppercase email (should succeed)
        response = client.post("/api/v1/users", json={"email": "CASE@example.com"})
        assert response.status_code == HTTPStatus.CREATED

    def test_unicode_in_email(self, client):
        """Test creating user with unicode characters in email"""
        payload = {
            "email": "tëst@ëxämplë.com",
            "google_sub": "unicode123"
        }
        response = client.post("/api/v1/users", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["email"] == "tëst@ëxämplë.com"
        assert data["google_sub"] == "unicode123"

    def test_unicode_in_google_sub(self, client):
        """Test creating user with unicode characters in google_sub"""
        payload = {
            "email": "unicode@example.com",
            "google_sub": "gööglë123"
        }
        response = client.post("/api/v1/users", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["email"] == "unicode@example.com"
        assert data["google_sub"] == "gööglë123"
