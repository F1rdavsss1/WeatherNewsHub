"""Тесты для Weather API"""
import pytest
from unittest.mock import AsyncMock, patch
from app.utils.weather_api import WeatherAPI


@pytest.fixture
def weather_api():
    """Фикстура для WeatherAPI"""
    return WeatherAPI(api_key="test_key")


@pytest.mark.asyncio
async def test_get_current_weather_success(weather_api):
    """Тест успешного получения погоды"""
    mock_response = {
        "name": "Moscow",
        "sys": {"country": "RU"},
        "main": {
            "temp": 15.5,
            "feels_like": 13.2,
            "humidity": 65,
            "pressure": 1013
        },
        "wind": {"speed": 3.5},
        "weather": [{"description": "облачно", "icon": "04d"}]
    }
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        result = await weather_api.get_current_weather("Moscow")
        
        assert result is not None
        assert result["city"] == "Moscow"
        assert result["temp"] == 16  # округлено
        assert result["humidity"] == 65


@pytest.mark.asyncio
async def test_get_current_weather_not_found(weather_api):
    """Тест получения погоды для несуществующего города"""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 404
        
        result = await weather_api.get_current_weather("NonExistentCity")
        
        assert result is None


@pytest.mark.asyncio
async def test_get_forecast_success(weather_api):
    """Тест успешного получения прогноза"""
    mock_response = {
        "city": {"name": "Moscow", "country": "RU"},
        "list": [
            {
                "dt_txt": "2024-03-08 12:00:00",
                "main": {"temp": 15.0},
                "weather": [{"description": "ясно", "icon": "01d"}]
            },
            {
                "dt_txt": "2024-03-08 15:00:00",
                "main": {"temp": 18.0},
                "weather": [{"description": "ясно", "icon": "01d"}]
            }
        ]
    }
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.status = 200
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(return_value=mock_response)
        
        result = await weather_api.get_forecast("Moscow", days=1)
        
        assert result is not None
        assert result["city"] == "Moscow"
        assert len(result["forecast"]) > 0
