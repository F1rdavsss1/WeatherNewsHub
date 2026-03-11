"""Работа с API новостей (CurrentsAPI)"""
import logging
from typing import Optional, Dict, Any, List
import aiohttp
from app.config import settings

logger = logging.getLogger(__name__)


class NewsAPI:
    """Класс для работы с CurrentsAPI"""
    
    BASE_URL = "https://api.currentsapi.services/v1"
    
    # Категории новостей
    CATEGORIES = {
        "general": "Общие",
        "technology": "Технологии",
        "science": "Наука",
        "sports": "Спорт",
        "business": "Бизнес",
        "health": "Здоровье",
        "entertainment": "Развлечения"
    }
    
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    async def get_top_headlines(
        self,
        category: str = "general",
        language: str = "ru",
        page_size: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Получение топ новостей
        
        Args:
            category: Категория новостей
            language: Язык новостей (ru/en)
            page_size: Количество новостей
            
        Returns:
            Список новостей или None при ошибке
        """
        url = f"{self.BASE_URL}/latest-news"
        params = {
            "apiKey": self.api_key,
            "category": category,
            "language": language,
            "page_size": page_size
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news(data.get("news", []))
                    elif response.status == 429:
                        logger.error("Превышен лимит запросов к CurrentsAPI")
                        return None
                    else:
                        logger.error(f"Ошибка API новостей: {response.status}")
                        return None
        except aiohttp.ClientError as e:
            logger.error(f"Ошибка сети при запросе новостей: {e}")
            return None
        except Exception as e:
            logger.error(f"Неожиданная ошибка при запросе новостей: {e}")
            return None
    
    async def search_news(
        self,
        query: str,
        language: str = "ru",
        page_size: int = 5
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Поиск новостей по запросу
        
        Args:
            query: Поисковый запрос
            language: Язык новостей
            page_size: Количество новостей
            
        Returns:
            Список новостей или None при ошибке
        """
        url = f"{self.BASE_URL}/search"
        params = {
            "apiKey": self.api_key,
            "keywords": query,
            "language": language,
            "page_size": page_size
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_news(data.get("news", []))
                    else:
                        logger.error(f"Ошибка поиска новостей: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Ошибка при поиске новостей: {e}")
            return None
    
    def _format_news(self, articles: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Форматирование новостей"""
        formatted = []
        for article in articles:
            # CurrentsAPI использует другую структуру данных
            formatted.append({
                "title": article.get("title", "Без заголовка"),
                "description": article.get("description", "Нет описания"),
                "url": article.get("url", ""),
                "source": article.get("author", "Неизвестный источник"),
                "published_at": article.get("published", ""),
                "image": article.get("image", "default")
            })
        return formatted
    
    @classmethod
    def get_category_name(cls, category: str, lang: str = "ru") -> str:
        """Получение названия категории"""
        if lang == "ru":
            return cls.CATEGORIES.get(category, "Общие")
        return category.capitalize()


# Глобальный экземпляр
news_api = NewsAPI(settings.NEWS_API_KEY)
