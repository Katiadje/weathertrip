import pytest
from unittest.mock import Mock, patch
from app.services.weather_service import WeatherService

@pytest.fixture
def weather_service():
    """Create weather service instance"""
    return WeatherService(api_key="test_api_key")

def test_weather_service_init(weather_service):
    """Test weather service initialization"""
    assert weather_service.api_key == "test_api_key"
    assert weather_service.base_url is not None

@patch('requests.get')
def test_get_weather_success(mock_get, weather_service):
    """Test successful weather fetch"""
    mock_response = Mock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "main": {"temp": 20, "humidity": 65},
        "weather": [{"description": "clear sky"}],
        "name": "Paris"
    }
    mock_get.return_value = mock_response
    
    result = weather_service.get_current_weather("Paris", "FR")
    assert result is not None
    assert "temp" in result.get("main", {})

@patch('requests.get')
def test_get_weather_failure(mock_get, weather_service):
    """Test weather fetch failure"""
    mock_response = Mock()
    mock_response.status_code = 404
    mock_get.return_value = mock_response
    
    result = weather_service.get_current_weather("InvalidCity", "XX")
    assert result is None or "error" in result