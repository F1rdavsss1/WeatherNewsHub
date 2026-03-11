"""FastAPI сервер для фронтенда"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="WeatherNews Hub API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API ключи
OPENWEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "")
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "")

# Models
class WeatherResponse(BaseModel):
    city: str
    country: str
    temperature: float
    feelsLike: float
    humidity: int
    pressure: int
    windSpeed: float
    windDirection: int
    clouds: int
    visibility: int
    description: str
    icon: str
    sunrise: int
    sunset: int
    timestamp: int

class ForecastDay(BaseModel):
    date: str
    temperature: dict
    description: str
    icon: str
    humidity: int
    windSpeed: float

class ForecastResponse(BaseModel):
    days: List[ForecastDay]

class NewsArticle(BaseModel):
    title: str
    description: Optional[str]
    url: str
    urlToImage: Optional[str]
    publishedAt: str
    source: dict

class NewsResponse(BaseModel):
    articles: List[NewsArticle]
    totalResults: int
    page: int
    pageSize: int


@app.get("/")
async def root():
    return {"message": "WeatherNews Hub API", "status": "running"}


@app.get("/weather/current", response_model=WeatherResponse)
async def get_current_weather(city: str = "Москва"):
    """Получить текущую погоду"""
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "ru"
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            return WeatherResponse(
                city=data["name"],
                country=data["sys"]["country"],
                temperature=data["main"]["temp"],
                feelsLike=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                pressure=data["main"]["pressure"],
                windSpeed=data["wind"]["speed"],
                windDirection=data["wind"].get("deg", 0),
                clouds=data["clouds"]["all"],
                visibility=data.get("visibility", 10000) // 1000,
                description=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                sunrise=data["sys"]["sunrise"],
                sunset=data["sys"]["sunset"],
                timestamp=data["dt"]
            )
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Weather API error: {str(e)}")


@app.get("/weather/forecast", response_model=ForecastResponse)
async def get_forecast(city: str = "Москва", days: int = 7):
    """Получить прогноз погоды"""
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "ru",
                    "cnt": days * 8  # 8 записей в день (каждые 3 часа)
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Группируем по дням
            forecast_days = []
            current_date = None
            day_temps = []
            
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).date()
                
                if current_date != date:
                    if day_temps:
                        forecast_days.append({
                            "date": current_date.isoformat(),
                            "temperature": {
                                "min": min(day_temps),
                                "max": max(day_temps),
                                "day": sum(day_temps) / len(day_temps)
                            },
                            "description": item["weather"][0]["description"],
                            "icon": item["weather"][0]["icon"],
                            "humidity": item["main"]["humidity"],
                            "windSpeed": item["wind"]["speed"]
                        })
                    current_date = date
                    day_temps = []
                
                day_temps.append(item["main"]["temp"])
            
            # Добавляем последний день
            if day_temps:
                forecast_days.append({
                    "date": current_date.isoformat(),
                    "temperature": {
                        "min": min(day_temps),
                        "max": max(day_temps),
                        "day": sum(day_temps) / len(day_temps)
                    },
                    "description": data["list"][-1]["weather"][0]["description"],
                    "icon": data["list"][-1]["weather"][0]["icon"],
                    "humidity": data["list"][-1]["main"]["humidity"],
                    "windSpeed": data["list"][-1]["wind"]["speed"]
                })
            
            return ForecastResponse(days=forecast_days[:days])
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"Forecast API error: {str(e)}")


@app.get("/news", response_model=NewsResponse)
async def get_news(
    category: str = "general",
    country: str = "ru",
    page: int = 1,
    pageSize: int = 8
):
    """Получить новости"""
    if not NEWS_API_KEY:
        # Возвращаем mock данные если ключ не настроен
        return get_mock_news(category, page, pageSize)
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "apiKey": NEWS_API_KEY,
                    "category": category,
                    "country": country,
                    "page": page,
                    "pageSize": pageSize
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            return NewsResponse(
                articles=[
                    NewsArticle(
                        title=article["title"],
                        description=article.get("description"),
                        url=article["url"],
                        urlToImage=article.get("urlToImage"),
                        publishedAt=article["publishedAt"],
                        source={"name": article["source"]["name"]}
                    )
                    for article in data.get("articles", [])
                ],
                totalResults=data.get("totalResults", 0),
                page=page,
                pageSize=pageSize
            )
    except httpx.HTTPError as e:
        # При ошибке возвращаем mock данные
        print(f"News API error: {str(e)}, returning mock data")
        return get_mock_news(category, page, pageSize)


def get_mock_news(category: str, page: int, pageSize: int) -> NewsResponse:
    """Возвращает mock данные для новостей"""
    mock_articles = [
        {
            "title": "Новые технологии в области искусственного интеллекта",
            "description": "Исследователи представили революционный подход к обучению нейронных сетей",
            "url": "https://example.com/news/1",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Tech News"}
        },
        {
            "title": "Прорыв в квантовых вычислениях",
            "description": "Ученые достигли нового рекорда в стабильности кубитов",
            "url": "https://example.com/news/2",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Science Daily"}
        },
        {
            "title": "Запуск нового космического телескопа",
            "description": "NASA объявило о успешном запуске телескопа нового поколения",
            "url": "https://example.com/news/3",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Space News"}
        },
        {
            "title": "Развитие возобновляемой энергетики",
            "description": "Новые солнечные панели показали рекордную эффективность",
            "url": "https://example.com/news/4",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Energy Today"}
        },
        {
            "title": "Инновации в медицине",
            "description": "Разработан новый метод ранней диагностики заболеваний",
            "url": "https://example.com/news/5",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Medical Journal"}
        },
        {
            "title": "Достижения в области робототехники",
            "description": "Представлен робот с улучшенными возможностями взаимодействия",
            "url": "https://example.com/news/6",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Robotics Weekly"}
        },
        {
            "title": "Новые открытия в физике",
            "description": "Физики обнаружили новую элементарную частицу",
            "url": "https://example.com/news/7",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "Physics World"}
        },
        {
            "title": "Прогресс в области биотехнологий",
            "description": "Ученые создали новый биоматериал с уникальными свойствами",
            "url": "https://example.com/news/8",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
            "source": {"name": "BioTech News"}
        }
    ]
    
    return NewsResponse(
        articles=[
            NewsArticle(
                title=article["title"],
                description=article["description"],
                url=article["url"],
                urlToImage=article["urlToImage"],
                publishedAt=article["publishedAt"],
                source=article["source"]
            )
            for article in mock_articles[:pageSize]
        ],
        totalResults=len(mock_articles),
        page=page,
        pageSize=pageSize
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
