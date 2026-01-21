import pytest

@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token"""
    client.post("/users/register", json=test_user)
    response = client.post("/users/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    return response.json()["access_token"]

@pytest.fixture
def test_trip(client, auth_token):
    """Create a test trip"""
    response = client.post(
        "/trips/",
        json={"name": "Test Trip", "description": "Test Description"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    return response.json()

def test_create_destination(client, auth_token, test_trip):
    """Test creating a destination"""
    response = client.post(
        "/destinations/",
        json={
            "trip_id": test_trip["id"],
            "city": "Paris",
            "country": "France"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["city"] == "Paris"
    assert data["country"] == "France"
    assert "id" in data

def test_get_trip_destinations(client, auth_token, test_trip):
    """Test getting destinations for a trip"""
    # Create a destination first
    client.post(
        "/destinations/",
        json={
            "trip_id": test_trip["id"],
            "city": "London",
            "country": "UK"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    response = client.get(
        f"/destinations/trip/{test_trip['id']}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0

def test_update_destination(client, auth_token, test_trip):
    """Test updating a destination"""
    # Create destination
    create_response = client.post(
        "/destinations/",
        json={
            "trip_id": test_trip["id"],
            "city": "Berlin",
            "country": "Germany"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    destination_id = create_response.json()["id"]
    
    # Update it
    response = client.put(
        f"/destinations/{destination_id}",
        json={"city": "Munich", "country": "Germany"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert response.json()["city"] == "Munich"

def test_delete_destination(client, auth_token, test_trip):
    """Test deleting a destination"""
    # Create destination
    create_response = client.post(
        "/destinations/",
        json={
            "trip_id": test_trip["id"],
            "city": "Rome",
            "country": "Italy"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    destination_id = create_response.json()["id"]
    
    # Delete it
    response = client.delete(
        f"/destinations/{destination_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204 or response.status_code == 200