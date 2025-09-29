import pytest
from http import HTTPStatus
from datetime import datetime, timezone


class TestInterviewCreation:
    """Test interview creation functionality"""

    def test_create_interview_returns_201_and_body(self, client):
        """Test creating a new interview returns correct response"""
        payload = {
            "user_id": 1,
            "company": "Acme Corp",
            "role": "Backend Engineer",
            "type": "coding",
            "starts_at": datetime.now(timezone.utc).isoformat(),
            "details": {"notes": "Technical coding interview"}
        }
        response = client.post("/api/v1/interviews", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        
        # Check required fields
        assert "id" in data
        assert data["user_id"] == 1
        assert data["company"] == "Acme Corp"
        assert data["role"] == "Backend Engineer"
        assert data["type"] == "coding"
        assert data["starts_at"] is not None
        assert data["details"] == {"notes": "Technical coding interview"}
        assert "created_at" in data

    def test_create_interview_minimal_payload(self, client):
        """Test creating interview with minimal required fields"""
        payload = {
            "user_id": 1,
        }
        response = client.post("/api/v1/interviews", json=payload)
        
        assert response.status_code == HTTPStatus.CREATED
        data = response.json()
        assert data["user_id"] == 1
        assert data["company"] is None
        assert data["role"] is None
        assert data["type"] is None

    def test_create_interview_validation_errors(self, client):
        """Test validation errors for invalid interview data"""
        # Missing required user_id
        payload = {
            "company": "Acme Corp",
            "role": "Backend Engineer",
            "type": "coding",
        }
        response = client.post("/api/v1/interviews", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Invalid type enum value
        payload = {
            "user_id": 1,
            "type": "invalid_type",
        }
        response = client.post("/api/v1/interviews", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY

        # Field too long
        payload = {
            "user_id": 1,
            "company": "A" * 101,  # Exceeds max_length=100
        }
        response = client.post("/api/v1/interviews", json=payload)
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestInterviewRetrieval:
    """Test interview retrieval functionality"""

    def test_get_interview_by_id_returns_200(self, client):
        """Test retrieving interview by ID"""
        # Create interview first
        create_response = client.post("/api/v1/interviews", json={
            "user_id": 2,
            "company": "Globex Corp",
            "role": "Platform Engineer",
            "type": "design",
            "starts_at": datetime.now(timezone.utc).isoformat()
        })
        assert create_response.status_code == HTTPStatus.CREATED
        interview_data = create_response.json()
        interview_id = interview_data["id"]

        # Retrieve by ID
        response = client.get(f"/api/v1/interviews/{interview_id}")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert data["id"] == interview_id
        assert data["user_id"] == 2
        assert data["company"] == "Globex Corp"
        assert data["role"] == "Platform Engineer"
        assert data["type"] == "design"

    def test_get_interview_not_found(self, client):
        """Test retrieving non-existent interview returns 404"""
        response = client.get("/api/v1/interviews/99999")
        assert response.status_code == HTTPStatus.NOT_FOUND
        
        error_data = response.json()
        assert "detail" in error_data
        assert "not found" in error_data["detail"].lower()

    def test_get_interview_invalid_id(self, client):
        """Test retrieving interview with invalid ID format"""
        response = client.get("/api/v1/interviews/not_a_number")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestInterviewListing:
    """Test interview listing functionality"""

    def test_list_interviews_by_user_id(self, client):
        """Test listing interviews for a specific user"""
        # Create interviews for different users
        client.post("/api/v1/interviews", json={
            "user_id": 1, "company": "Company A", "role": "Role X", "type": "coding"
        })
        client.post("/api/v1/interviews", json={
            "user_id": 2, "company": "Company B", "role": "Role Y", "type": "design"
        })
        client.post("/api/v1/interviews", json={
            "user_id": 1, "company": "Company C", "role": "Role Z", "type": "phone"
        })

        # List interviews for user 1
        response = client.get("/api/v1/interviews?user_id=1&limit=10&offset=0")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 2
        
        # All returned interviews should belong to user 1
        for interview in data:
            assert interview["user_id"] == 1
            assert "id" in interview
            assert "created_at" in interview

    def test_list_interviews_empty_result(self, client):
        """Test listing interviews for user with no interviews"""
        response = client.get("/api/v1/interviews?user_id=999&limit=10&offset=0")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_interviews_pagination(self, client):
        """Test pagination functionality"""
        # Create 5 interviews for user 1
        for i in range(5):
            client.post("/api/v1/interviews", json={
                "user_id": 1, 
                "company": f"Company {i}", 
                "role": f"Role {i}", 
                "type": "coding"
            })

        # Test limit
        response = client.get("/api/v1/interviews?user_id=1&limit=3&offset=0")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 3

        # Test offset
        response = client.get("/api/v1/interviews?user_id=1&limit=3&offset=3")
        assert response.status_code == HTTPStatus.OK
        data = response.json()
        assert len(data) == 2

    def test_list_interviews_missing_user_id(self, client):
        """Test that user_id is required for listing interviews"""
        response = client.get("/api/v1/interviews?limit=10&offset=0")
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestInterviewUpdates:
    """Test interview update functionality"""

    def test_update_interview_partial(self, client):
        """Test partial update of interview"""
        # Create interview
        create_response = client.post("/api/v1/interviews", json={
            "user_id": 1, 
            "company": "Original Corp", 
            "role": "Original Role", 
            "type": "coding"
        })
        interview_id = create_response.json()["id"]

        # Partial update
        update_response = client.patch(f"/api/v1/interviews/{interview_id}", json={
            "company": "Updated Corp"
        })
        
        assert update_response.status_code == HTTPStatus.OK
        data = update_response.json()
        
        assert data["company"] == "Updated Corp"
        assert data["role"] == "Original Role"  # Should remain unchanged
        assert data["type"] == "coding"  # Should remain unchanged
        assert data["id"] == interview_id

    def test_update_interview_full(self, client):
        """Test full update of interview"""
        # Create interview
        create_response = client.post("/api/v1/interviews", json={
            "user_id": 1, 
            "company": "Old Corp", 
            "role": "Old Role", 
            "type": "coding"
        })
        interview_id = create_response.json()["id"]

        # Full update
        update_response = client.patch(f"/api/v1/interviews/{interview_id}", json={
            "company": "New Corp",
            "role": "New Role",
            "type": "design",
            "details": {"new": "details"}
        })
        
        assert update_response.status_code == HTTPStatus.OK
        data = update_response.json()
        
        assert data["company"] == "New Corp"
        assert data["role"] == "New Role"
        assert data["type"] == "design"
        assert data["details"] == {"new": "details"}

    def test_update_interview_not_found(self, client):
        """Test updating non-existent interview"""
        response = client.patch("/api/v1/interviews/99999", json={
            "company": "Updated Corp"
        })
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_update_interview_invalid_data(self, client):
        """Test updating with invalid data"""
        # Create interview
        create_response = client.post("/api/v1/interviews", json={
            "user_id": 1, 
            "company": "Test Corp", 
            "role": "Test Role"
        })
        interview_id = create_response.json()["id"]

        # Invalid type
        response = client.patch(f"/api/v1/interviews/{interview_id}", json={
            "type": "invalid_type"
        })
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY


class TestInterviewDeletion:
    """Test interview deletion functionality"""

    def test_delete_interview(self, client):
        """Test deleting an existing interview"""
        # Create interview
        create_response = client.post("/api/v1/interviews", json={
            "user_id": 1, 
            "company": "To Be Deleted", 
            "role": "Test Role"
        })
        interview_id = create_response.json()["id"]

        # Delete interview
        delete_response = client.delete(f"/api/v1/interviews/{interview_id}")
        assert delete_response.status_code == HTTPStatus.NO_CONTENT
        
        # Verify deletion
        get_response = client.get(f"/api/v1/interviews/{interview_id}")
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_interview_not_found(self, client):
        """Test deleting non-existent interview"""
        response = client.delete("/api/v1/interviews/99999")
        assert response.status_code == HTTPStatus.NOT_FOUND


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_endpoint(self, client):
        """Test the health check endpoint"""
        response = client.get("/health")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert data["status"] == "ok"


class TestLegacyInterviewsEndpoint:
    """Test the legacy interviews endpoint"""

    def test_legacy_list_interviews(self, client):
        """Test the legacy interviews listing endpoint"""
        # Create some interviews first
        client.post("/api/v1/interviews", json={
            "user_id": 1, "company": "Legacy Test", "role": "Test Role", "type": "coding"
        })

        response = client.get("/api/v1/interviews?user_id=1&limit=10&offset=0")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert isinstance(data, list)
        
        # Check that items have expected fields (new format)
        if data:
            item = data[0]
            assert "id" in item
            assert "company" in item
            assert "role" in item
            assert "type" in item
            assert "starts_at" in item
            assert "user_id" in item

    def test_legacy_health_endpoint(self, client):
        """Test the legacy health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == HTTPStatus.OK
        
        data = response.json()
        assert data["status"] == "ok"
        assert data["scope"] == "v1"
