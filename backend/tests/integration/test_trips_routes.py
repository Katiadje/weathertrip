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

def test_create_trip(client, auth_token):
    """Test creating a trip"""
    response = client.post(
        "/trips/",
        json={"name": "Voyage à Paris", "description": "Vacances d'été"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Voyage à Paris"
    assert "id" in data

def test_get_trips(client, auth_token):
    """Test getting all trips"""
    response = client.get(
        "/trips/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_unauthorized_access(client):
    """Test accessing trips without token"""
    response = client.get("/trips/")
    assert response.status_code == 401