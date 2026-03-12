import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { weatherApi, newsApi } from '../lib/api';
import { useStore } from '../store/useStore';
import { mockWeather, mockForecast, mockNews } from '../lib/mockData';
import { WiHumidity, WiStrongWind, WiBarometer, WiSunrise } from 'react-icons/wi';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import toast from 'react-hot-toast';

const NEWS_CATEGORIES = [
  { value: 'general', label: 'Главное' },
  { value: 'technology', label: 'Технологии' },
  { value: 'science', label: 'Наука' },
  { value: 'sports', label: 'Спорт' },
  { value: 'business', label: 'Бизнес' },
];

export const Home = () => {
  const { currentCity } = useStore();
  const [activeCategory, setActiveCategory] = useState('general');
  const [newsPage, setNewsPage] = useState(1);

  // Weather Query с fallback на mock данные
  const { data: weatherData, isLoading: weatherLoading, error: weatherError } = useQuery({
    queryKey: ['weather', currentCity],
    queryFn: () => weatherApi.getCurrent(currentCity),
    retry: 1,
    staleTime: 5 * 60 * 1000,
  });

  // Forecast Query с fallback на mock данные - прогноз на 30 дней
  const { data: forecastData, error: forecastError } = useQuery({
    queryKey: ['forecast', currentCity],
    queryFn: () => weatherApi.getForecast(currentCity, 30),
    retry: 1,
    staleTime: 5 * 60 * 1000,
  });

  // News Query с fallback на mock данные и автообновлением каждый час
  const { data: newsData, isLoading: newsLoading, error: newsError } = useQuery({
    queryKey: ['news', activeCategory, newsPage],
    queryFn: () => newsApi.getNews({
      category: activeCategory,
      country: 'ru',
      page: newsPage,
      pageSize: 8,
    }),
    retry: 1,
    staleTime: 60 * 60 * 1000, // 1 час
    refetchInterval: 60 * 60 * 1000, // Обновлять каждый час
  });

  // Используем реальные данные или fallback на mock
  const weather = weatherData || mockWeather;
  const forecast = forecastData || mockForecast;
  const news = newsData || mockNews;

  // Проверяем, используются ли реальные данные
  const isUsingMockWeather = !weatherData;
  const isUsingMockNews = !newsData;

  const getWeatherIcon = (icon: string) => {
    return `https://openweathermap.org/img/wn/${icon}@4x.png`;
  };

  const handleLoadMore = () => {
    setNewsPage(prev => prev + 1);
  };

  return (
    <div className="min-h-screen bg-gradient-dark">
      <div className="container mx-auto px-4 py-8 space-y-8">
        {/* Weather Section */}
        <section>
          {weatherLoading ? (
            <div className="flex items-center justify-center h-96">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Main Weather Card */}
                <div className="lg:col-span-2 glass-effect rounded-3xl p-8">
                  <div className="flex items-start justify-between mb-6">
                    <div>
                      <h2 className="text-3xl font-bold text-white mb-1">
                        {weather.city || currentCity}
                      </h2>
                      <p className="text-gray-400">{weather.country || 'RU'}</p>
                      {isUsingMockWeather && (
                        <p className="text-xs text-yellow-400 mt-1">
                          ⚠️ Демо данные (API недоступен)
                        </p>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center">
                      <img
                        src={getWeatherIcon(weather.icon)}
                        alt={weather.description}
                        className="w-32 h-32"
                      />
                      <div>
                        <div className="text-7xl font-bold text-white">
                          {Math.round(weather.temperature)}°
                        </div>
                        <div className="text-gray-400 mt-2">
                          Ощущается как {Math.round(weather.feelsLike)}°
                        </div>
                        <div className="text-white mt-1 capitalize">
                          {weather.description}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Weather Details Grid */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="bg-dark-card/50 rounded-2xl p-4">
                      <WiHumidity className="w-8 h-8 text-blue-400 mb-2" />
                      <div className="text-sm text-gray-400">Влажность</div>
                      <div className="text-2xl font-semibold text-white">
                        {weather.humidity}%
                      </div>
                    </div>

                    <div className="bg-dark-card/50 rounded-2xl p-4">
                      <WiStrongWind className="w-8 h-8 text-gray-400 mb-2" />
                      <div className="text-sm text-gray-400">Ветер</div>
                      <div className="text-2xl font-semibold text-white">
                        {weather.windSpeed} м/с
                      </div>
                    </div>

                    <div className="bg-dark-card/50 rounded-2xl p-4">
                      <WiBarometer className="w-8 h-8 text-purple-400 mb-2" />
                      <div className="text-sm text-gray-400">Давление</div>
                      <div className="text-2xl font-semibold text-white">
                        {Math.round(weather.pressure * 0.75)} мм
                      </div>
                    </div>

                    <div className="bg-dark-card/50 rounded-2xl p-4">
                      <WiSunrise className="w-8 h-8 text-orange-400 mb-2" />
                      <div className="text-sm text-gray-400">Рассвет и закат</div>
                      <div className="text-lg font-semibold text-white">
                        {format(new Date(weather.sunrise * 1000), 'HH:mm', { locale: ru })}
                      </div>
                    </div>
                  </div>
                </div>

                {/* Forecast Cards */}
                <div className="space-y-4">
                  {forecast.days.slice(0, 4).map((day, index) => (
                    <div key={index} className="glass-effect rounded-2xl p-4 flex items-center justify-between">
                      <div>
                        <div className="text-white font-medium">
                          {index === 0 ? 'Сегодня' : format(new Date(day.date), 'EEE', { locale: ru })}
                        </div>
                        <div className="text-gray-400 text-sm">
                          {format(new Date(day.date), 'd MMM', { locale: ru })}
                        </div>
                      </div>
                      <img
                        src={getWeatherIcon(day.icon)}
                        alt={day.description}
                        className="w-12 h-12"
                      />
                      <div className="text-right">
                        <div className="text-white font-semibold">
                          {Math.round(day.temperature.max)}°
                        </div>
                        <div className="text-gray-400 text-sm">
                          {Math.round(day.temperature.min)}°
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Прогноз на месяц */}
              <div className="mt-8 glass-effect rounded-3xl p-8">
                <h3 className="text-2xl font-bold text-white mb-6">Прогноз на месяц</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                  {forecast.days.slice(0, 30).map((day, index) => (
                    <div
                      key={index}
                      className="bg-dark-card/50 rounded-2xl p-4 text-center hover:bg-dark-cardHover transition-default cursor-pointer"
                    >
                      <div className="text-sm text-gray-400 mb-2">
                        {format(new Date(day.date), 'd MMM', { locale: ru })}
                      </div>
                      <img
                        src={getWeatherIcon(day.icon)}
                        alt={day.description}
                        className="w-16 h-16 mx-auto mb-2"
                      />
                      <div className="text-lg font-bold text-white">
                        {Math.round(day.temperature.max)}°
                      </div>
                      <div className="text-sm text-gray-400">
                        {Math.round(day.temperature.min)}°
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
        </section>

        {/* News Section */}
        <section>
          <div className="flex items-center space-x-4 mb-6">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 rounded-xl bg-primary-600 flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z" />
                </svg>
              </div>
              <h2 className="text-2xl font-bold text-white">Лента новостей</h2>
              {isUsingMockNews && (
                <span className="text-xs text-yellow-400 px-3 py-1 bg-yellow-400/10 rounded-full">
                  ⚠️ Демо данные (API недоступен)
                </span>
              )}
            </div>
          </div>

          {/* News Categories */}
          <div className="flex flex-wrap gap-3 mb-6">
            {NEWS_CATEGORIES.map((cat) => (
              <button
                key={cat.value}
                onClick={() => {
                  setActiveCategory(cat.value);
                  setNewsPage(1);
                }}
                className={`px-6 py-2.5 rounded-xl font-medium transition-default ${
                  activeCategory === cat.value
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-card/50 text-gray-400 hover:bg-dark-cardHover hover:text-white'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>

          {/* News Grid */}
          {newsLoading && newsPage === 1 ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-primary-500"></div>
            </div>
          ) : (
            <>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {news.articles.map((article, index) => (
                  <a
                    key={index}
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="glass-effect rounded-2xl p-6 hover:scale-105 transition-all duration-300 group flex flex-col"
                  >
                    <h3 className="text-white font-semibold mb-3 line-clamp-2 group-hover:text-primary-400 transition-colors text-lg">
                      {article.title}
                    </h3>
                    
                    {article.description && (
                      <p className="text-gray-400 text-sm mb-4 line-clamp-3 flex-1">
                        {article.description}
                      </p>
                    )}
                    
                    <div className="flex items-center justify-between text-xs text-gray-500 mt-auto pt-4 border-t border-gray-700/50">
                      <span className="font-medium text-primary-400">{article.source.name}</span>
                      <span>
                        {format(new Date(article.publishedAt), 'd MMM, HH:mm', { locale: ru })}
                      </span>
                    </div>
                  </a>
                ))}
              </div>

              {news.totalResults > news.articles.length && (
                <div className="flex justify-center mt-8">
                  <button
                    onClick={handleLoadMore}
                    disabled={newsLoading}
                    className="px-8 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl transition-default text-white font-medium disabled:opacity-50"
                  >
                    {newsLoading ? 'Загрузка...' : 'Загрузить еще'}
                  </button>
                </div>
              )}
            </>
          )}
        </section>
      </div>
    </div>
  );
};
