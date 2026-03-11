"""Работа с API погоды (OpenWeatherMap)"""
import logging
from typing import Optional, Dict, Any
import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)


class WeatherAPI:
    """Класс для работы с OpenWeatherMap API"""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_current_weather(self, city: str, lang: str = "ru") -> Optional[Dict[str, Any]]:
        """
        Получение текущей погоды
        
        Args:
            city: Название города
            lang: Язык ответа (ru/en)
            
        Returns:
            Словарь с данными о погоде или None при ошибке
        """
        url = f"{self.BASE_URL}/weather"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": lang
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_current_weather(data)
                    elif response.status == 404:
                        logger.warning(f"Город не найден: {city}")
                        return None
                    else:
                        logger.error(f"Ошибка API погоды: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при запросе погоды: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе погоды: {e}")
            return None
    
    async def get_forecast(self, city: str, days: int = 5, lang: str = "ru") -> Optional[Dict[str, Any]]:
        """
        Получение прогноза погоды
        
        Args:
            city: Название города
            days: Количество дней (1-7)
            lang: Язык ответа
            
        Returns:
            Словарь с прогнозом или None при ошибке
        """
        url = f"{self.BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": self.api_key,
            "units": "metric",
            "lang": lang,
            "cnt": days * 8  # 8 записей на день (каждые 3 часа)
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_forecast(data, days)
                    elif response.status == 404:
                        logger.warning(f"Город не найден: {city}")
                        return None
                    else:
                        logger.error(f"Ошибка API прогноза: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при запросе прогноза: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе прогноза: {e}")
            return None
    
    def _format_current_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Форматирование данных текущей погоды"""
        return {
            "city": data["name"],
            "country": data["sys"]["country"],
            "temp": round(data["main"]["temp"]),
            "feels_like": round(data["main"]["feels_like"]),
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "wind_speed": data["wind"]["speed"],
            "description": data["weather"][0]["description"].capitalize(),
            "icon": data["weather"][0]["icon"]
        }
    
    def _format_forecast(self, data: Dict[str, Any], days: int) -> Dict[str, Any]:
        """Форматирование данных прогноза"""
        forecast_list = []
        
        # Группировка по дням
        daily_data = {}
        for item in data["list"][:days * 8]:
            date = item["dt_txt"].split()[0]
            if date not in daily_data:
                daily_data[date] = {
                    "temps": [],
                    "descriptions": [],
                    "icons": []
                }
            daily_data[date]["temps"].append(item["main"]["temp"])
            daily_data[date]["descriptions"].append(item["weather"][0]["description"])
            daily_data[date]["icons"].append(item["weather"][0]["icon"])
        
        # Формирование итогового прогноза
        for date, info in list(daily_data.items())[:days]:
            forecast_list.append({
                "date": date,
                "temp_min": round(min(info["temps"])),
                "temp_max": round(max(info["temps"])),
                "description": max(set(info["descriptions"]), key=info["descriptions"].count).capitalize(),
                "icon": max(set(info["icons"]), key=info["icons"].count)
            })
        
        return {
            "city": data["city"]["name"],
            "country": data["city"]["country"],
            "forecast": forecast_list
        }


# Глобальный экземпляр
weather_api = WeatherAPI(settings.WEATHER_API_KEY)
