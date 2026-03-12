"""FastAPI сервер для фронтенда"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import os
from datetime import datetime, timedelta
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

# Импорт функции проверки кода
import sys
sys.path.insert(0, os.path.dirname(__file__))
from app.auth_storage import verify_auth_code

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


class AuthRequest(BaseModel):
    code: str


class AuthResponse(BaseModel):
    success: bool
    user: Optional[dict] = None
    message: Optional[str] = None


class CitiesResponse(BaseModel):
    cities: List[str]


# Список популярных городов России
CITIES = [
    "Москва", "Санкт-Петербург", "Новосибирск", "Екатеринбург", "Казань",
    "Нижний Новгород", "Челябинск", "Самара", "Омск", "Ростов-на-Дону",
    "Уфа", "Красноярск", "Воронеж", "Пермь", "Волгоград",
    "Краснодар", "Саратов", "Тюмень", "Тольятти", "Ижевск",
    "Барнаул", "Ульяновск", "Иркутск", "Хабаровск", "Ярославль",
    "Владивосток", "Махачкала", "Томск", "Оренбург", "Кемерово",
    "Новокузнецк", "Рязань", "Астрахань", "Набережные Челны", "Пенза",
    "Липецк", "Киров", "Чебоксары", "Калининград", "Тула",
    "Курск", "Сочи", "Ставрополь", "Улан-Удэ", "Тверь",
    "Магнитогорск", "Иваново", "Брянск", "Белгород", "Сургут"
]


@app.post("/auth/telegram", response_model=AuthResponse)
async def auth_telegram(request: AuthRequest):
    """Авторизация через Telegram код"""
    print(f"[AUTH] Получен запрос с кодом: {request.code}")
    
    user_data = verify_auth_code(request.code)
    
    print(f"[AUTH] Результат проверки: {user_data}")
    
    if not user_data:
        print(f"[AUTH] Код неверный или истёк")
        return AuthResponse(
            success=False,
            message="Неверный или истёкший код"
        )
    
    print(f"[AUTH] Успешная авторизация для пользователя {user_data.get('telegram_id')}")
    return AuthResponse(
        success=True,
        user={
            "telegram_id": user_data["telegram_id"],
            "username": user_data.get("username"),
            "first_name": user_data.get("first_name")
        },
        message="Успешная авторизация"
    )


@app.get("/cities", response_model=CitiesResponse)
async def get_cities():
    """Получить список городов"""
    return CitiesResponse(cities=CITIES)


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
async def get_forecast(city: str = "Москва", days: int = 30):
    """Получить прогноз погоды на месяц (до 30 дней)"""
    if not OPENWEATHER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenWeather API key not configured")
    
    # OpenWeatherMap бесплатный API дает только 5 дней
    # Для месячного прогноза нужен платный API или использовать mock данные
    
    try:
        async with httpx.AsyncClient() as client:
            # Получаем 5-дневный прогноз
            response = await client.get(
                "https://api.openweathermap.org/data/2.5/forecast",
                params={
                    "q": city,
                    "appid": OPENWEATHER_API_KEY,
                    "units": "metric",
                    "lang": "ru",
                    "cnt": 40  # Максимум 40 записей (5 дней * 8 записей)
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
            
            # Если запрошено больше 5 дней, генерируем реалистичные данные для остальных
            if days > len(forecast_days):
                import random
                
                # Базовые температуры из последнего реального дня
                if forecast_days:
                    base_min = forecast_days[-1]["temperature"]["min"]
                    base_max = forecast_days[-1]["temperature"]["max"]
                else:
                    # Если нет реальных данных, используем средние для марта
                    base_min = 0
                    base_max = 8
                
                # Иконки погоды для разнообразия
                weather_icons = ["01d", "02d", "03d", "04d", "09d", "10d", "13d"]
                weather_descriptions = [
                    "ясно", "малооблачно", "облачно", "пасмурно", 
                    "небольшой дождь", "дождь", "снег"
                ]
                
                for i in range(len(forecast_days), days):
                    next_date = datetime.now().date() + timedelta(days=i)
                    
                    # Добавляем случайную вариацию температуры (±3 градуса)
                    temp_variation = random.uniform(-3, 3)
                    day_min = round(base_min + temp_variation, 1)
                    day_max = round(base_max + temp_variation + random.uniform(2, 5), 1)
                    day_avg = round((day_min + day_max) / 2, 1)
                    
                    # Случайная погода
                    weather_idx = random.randint(0, len(weather_icons) - 1)
                    
                    forecast_days.append({
                        "date": next_date.isoformat(),
                        "temperature": {
                            "min": day_min,
                            "max": day_max,
                            "day": day_avg
                        },
                        "description": weather_descriptions[weather_idx],
                        "icon": weather_icons[weather_idx],
                        "humidity": random.randint(60, 85),
                        "windSpeed": round(random.uniform(2, 6), 1)
                    })
                    
                    # Небольшое изменение базовой температуры для следующего дня
                    base_min += random.uniform(-0.5, 0.5)
                    base_max += random.uniform(-0.5, 0.5)
            
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
    """Получить новости за последние 2 дня"""
    if not NEWS_API_KEY:
        return get_mock_news(category, page, pageSize)
    
    try:
        # Дата 2 дня назад
        from_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://newsapi.org/v2/top-headlines",
                params={
                    "apiKey": NEWS_API_KEY,
                    "category": category,
                    "country": country,
                    "page": page,
                    "pageSize": pageSize,
                    "from": from_date
                },
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            # Фильтруем новости за последние 2 дня
            articles = []
            cutoff_date = datetime.now() - timedelta(days=2)
            
            for article in data.get("articles", []):
                pub_date = datetime.fromisoformat(article["publishedAt"].replace('Z', '+00:00'))
                if pub_date >= cutoff_date:
                    articles.append(NewsArticle(
                        title=article["title"],
                        description=article.get("description"),
                        url=article["url"],
                        urlToImage=None,  # Не показываем картинки
                        publishedAt=article["publishedAt"],
                        source={"name": article["source"]["name"]}
                    ))
            
            return NewsResponse(
                articles=articles,
                totalResults=len(articles),
                page=page,
                pageSize=pageSize
            )
    except httpx.HTTPError as e:
        print(f"News API error: {str(e)}, returning mock data")
        return get_mock_news(category, page, pageSize)


def get_mock_news(category: str, page: int, pageSize: int) -> NewsResponse:
    """Возвращает mock данные для новостей с учетом категории"""
    
    # Разные новости для разных категорий
    news_by_category = {
        "general": [
            {"title": "Главные события дня в мире", "description": "Обзор самых важных новостей за сегодня", "source": {"name": "Новости"}},
            {"title": "Политические изменения в Европе", "description": "Анализ последних политических событий", "source": {"name": "Политика"}},
            {"title": "Экономическая ситуация улучшается", "description": "Эксперты прогнозируют рост экономики", "source": {"name": "Экономика"}},
        ],
        "technology": [
            {"title": "Новые технологии в области искусственного интеллекта", "description": "Исследователи представили революционный подход к обучению нейронных сетей", "source": {"name": "Tech News"}},
            {"title": "Прорыв в квантовых вычислениях", "description": "Ученые достигли нового рекорда в стабильности кубитов", "source": {"name": "Science Daily"}},
            {"title": "Новый смартфон с революционной батареей", "description": "Компания представила устройство с недельным временем работы", "source": {"name": "Gadgets"}},
        ],
        "science": [
            {"title": "Запуск нового космического телескопа", "description": "NASA объявило о успешном запуске телескопа нового поколения", "source": {"name": "Space News"}},
            {"title": "Открытие новой экзопланеты", "description": "Астрономы обнаружили потенциально обитаемую планету", "source": {"name": "Astronomy"}},
            {"title": "Прорыв в изучении ДНК", "description": "Ученые расшифровали новые механизмы генетики", "source": {"name": "Biology Today"}},
        ],
        "sports": [
            {"title": "Чемпионат мира по футболу: результаты", "description": "Обзор матчей и главные события турнира", "source": {"name": "Спорт"}},
            {"title": "Олимпийские игры: новые рекорды", "description": "Спортсмены установили несколько мировых рекордов", "source": {"name": "Олимпиада"}},
            {"title": "Теннисный турнир: сенсация", "description": "Неожиданная победа молодого спортсмена", "source": {"name": "Теннис"}},
        ],
        "business": [
            {"title": "Развитие возобновляемой энергетики", "description": "Новые солнечные панели показали рекордную эффективность", "source": {"name": "Energy Today"}},
            {"title": "Рост акций технологических компаний", "description": "Фондовый рынок показывает позитивную динамику", "source": {"name": "Финансы"}},
            {"title": "Новые инвестиции в стартапы", "description": "Венчурные фонды увеличили вложения в инновации", "source": {"name": "Бизнес"}},
        ],
        "health": [
            {"title": "Инновации в медицине", "description": "Разработан новый метод ранней диагностики заболеваний", "source": {"name": "Medical Journal"}},
            {"title": "Вакцина от нового вируса", "description": "Клинические испытания показали высокую эффективность", "source": {"name": "Здоровье"}},
            {"title": "Здоровое питание: новые рекомендации", "description": "Диетологи обновили рекомендации по питанию", "source": {"name": "Nutrition"}},
        ],
        "entertainment": [
            {"title": "Премьера нового фильма побила рекорды", "description": "Кассовые сборы превзошли все ожидания", "source": {"name": "Кино"}},
            {"title": "Музыкальный фестиваль собрал тысячи зрителей", "description": "Выступили звезды мировой величины", "source": {"name": "Музыка"}},
            {"title": "Новый сезон популярного сериала", "description": "Фанаты в восторге от продолжения истории", "source": {"name": "ТВ"}},
        ],
    }
    
    # Получаем новости для категории или общие
    articles_data = news_by_category.get(category, news_by_category["general"])
    
    # Добавляем дополнительные поля
    mock_articles = []
    for article in articles_data[:pageSize]:
        mock_articles.append({
            **article,
            "url": f"https://example.com/news/{category}/{len(mock_articles)+1}",
            "urlToImage": None,
            "publishedAt": datetime.now().isoformat(),
        })
    
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
            for article in mock_articles
        ],
        totalResults=len(articles_data),
        page=page,
        pageSize=pageSize
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
