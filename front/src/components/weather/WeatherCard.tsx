import { FiRefreshCw, FiStar } from 'react-icons/fi';
import { WiHumidity, WiStrongWind, WiBarometer, WiSunrise } from 'react-icons/wi';
import { Card } from '../ui/Card';
import type { WeatherResponse } from '../../types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

interface WeatherCardProps {
  weather: WeatherResponse;
  onRefresh?: () => void;
  onToggleFavorite?: () => void;
  isFavorite?: boolean;
}

export const WeatherCard = ({ weather, onRefresh, onToggleFavorite, isFavorite }: WeatherCardProps) => {
  const getWeatherIcon = (icon: string) => {
    return `https://openweathermap.org/img/wn/${icon}@4x.png`;
  };

  return (
    <Card className="p-6">
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            {weather.city}
          </h2>
          <p className="text-gray-600 dark:text-gray-400">{weather.country}</p>
        </div>
        <div className="flex space-x-2">
          {onRefresh && (
            <button
              onClick={onRefresh}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-default"
              aria-label="Обновить"
            >
              <FiRefreshCw className="w-5 h-5 text-gray-600 dark:text-gray-400" />
            </button>
          )}
          {onToggleFavorite && (
            <button
              onClick={onToggleFavorite}
              className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-default"
              aria-label={isFavorite ? 'Удалить из избранного' : 'Добавить в избранное'}
            >
              <FiStar
                className={`w-5 h-5 ${
                  isFavorite ? 'fill-yellow-400 text-yellow-400' : 'text-gray-600 dark:text-gray-400'
                }`}
              />
            </button>
          )}
        </div>
      </div>

      {/* Main Weather */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <img
            src={getWeatherIcon(weather.icon)}
            alt={weather.description}
            className="w-32 h-32"
          />
          <div>
            <div className="text-6xl font-bold text-gray-900 dark:text-white">
              {Math.round(weather.temperature)}°
            </div>
            <div className="text-gray-600 dark:text-gray-400 mt-1">
              Ощущается как {Math.round(weather.feelsLike)}°
            </div>
            <div className="text-gray-700 dark:text-gray-300 mt-1 capitalize">
              {weather.description}
            </div>
          </div>
        </div>
      </div>

      {/* Details Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <WiHumidity className="w-8 h-8 text-blue-500" />
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Влажность</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {weather.humidity}%
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <WiStrongWind className="w-8 h-8 text-gray-500" />
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Ветер</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {weather.windSpeed} м/с
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <WiBarometer className="w-8 h-8 text-purple-500" />
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Давление</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {Math.round(weather.pressure * 0.75)} мм
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3 p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
          <WiSunrise className="w-8 h-8 text-orange-500" />
          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400">Восход</div>
            <div className="text-lg font-semibold text-gray-900 dark:text-white">
              {format(new Date(weather.sunrise * 1000), 'HH:mm', { locale: ru })}
            </div>
          </div>
        </div>
      </div>
    </Card>
  );
};
