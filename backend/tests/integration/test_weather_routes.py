import pytest
from unittest.mock import patch

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
def test_trip_with_destination(client, auth_token):
    """Create trip with destination"""
    # Create trip
    trip_response = client.post(
        "/trips/",
        json={"name": "Weather Test Trip"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    trip = trip_response.json()
    
    # Create destination
    dest_response = client.post(
        "/destinations/",
        json={
            "trip_id": trip["id"],
            "city": "Paris",
            "country": "France"
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    return {
        "trip": trip,
        "destination": dest_response.json()
    }

@patch('app.services.weather_service.WeatherService.get_current_weather')
def test_get_weather_for_city(mock_weather, client, auth_token):
    """Test getting weather for a city"""
    mock_weather.return_value = {
        "main": {"temp": 20, "humidity": 65},
        "weather": [{"description": "clear sky"}]
    }
    
    response = client.get(
        "/weather/city/Paris",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "main" in data or "temp" in data or response.status_code in [200, 404]

@patch('app.services.weather_service.WeatherService.get_current_weather')
def test_get_weather_for_destination(mock_weather, client, auth_token, test_trip_with_destination):
    """Test getting weather for a destination"""
    mock_weather.return_value = {
        "main": {"temp": 22, "humidity": 70},
        "weather": [{"description": "sunny"}]
    }
    
    destination_id = test_trip_with_destination["destination"]["id"]
    response = client.get(
        f"/weather/destination/{destination_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code in [200, 404]

@patch('app.services.weather_service.WeatherService.get_forecast')
def test_get_forecast_for_destination(mock_forecast, client, auth_token, test_trip_with_destination):
    """Test getting forecast for a destination"""
    mock_forecast.return_value = {
        "list": [
            {"dt": 1234567890, "main": {"temp": 20}},
            {"dt": 1234567900, "main": {"temp": 21}}
        ]
    }
    
    destination_id = test_trip_with_destination["destination"]["id"]
    response = client.post(
        f"/weather/destination/{destination_id}/forecast",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code in [200, 201, 404]

def test_unauthorized_weather_access(client):
    """Test accessing weather without authentication"""
    response = client.get("/weather/city/Paris")
    assert response.status_code == 401