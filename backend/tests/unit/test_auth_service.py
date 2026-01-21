from app.services.auth_service import get_password_hash, verify_password, create_access_token

def test_hash_password():
    """Test password hashing"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    assert hashed != password
    assert len(hashed) > 0

def test_verify_password():
    """Test password verification"""
    password = "TestPassword123!"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_create_access_token():
    """Test JWT token creation"""
    token = create_access_token({"sub": "testuser"})
    assert isinstance(token, str)
    assert len(token) > 0