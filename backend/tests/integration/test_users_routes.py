def test_register_user(client, test_user):
    """Test user registration"""
    response = client.post("/users/register", json=test_user)
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == test_user["username"]
    assert data["email"] == test_user["email"]
    assert "id" in data

def test_login_user(client, test_user):
    """Test user login"""
    # Register first
    client.post("/users/register", json=test_user)
    # Then login
    response = client.post("/users/login", json={
        "username": test_user["username"],
        "password": test_user["password"]
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_duplicate_user(client, test_user):
    """Test registering duplicate user"""
    client.post("/users/register", json=test_user)
    response = client.post("/users/register", json=test_user)
    assert response.status_code == 400