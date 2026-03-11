import { Card } from '../ui/Card';
import type { ForecastDay } from '../../types';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';
import { getWeatherIcon } from '../../lib/utils';

interface ForecastWeekProps {
  forecast: ForecastDay[];
}

export const ForecastWeek = ({ forecast }: ForecastWeekProps) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
      {forecast.map((day, index) => (
        <Card
          key={index}
          hover
          className="p-4 text-center cursor-pointer"
        >
          <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
            {format(new Date(day.date), 'EEE', { locale: ru })}
          </div>
          <div className="text-xs text-gray-500 dark:text-gray-500 mb-3">
            {format(new Date(day.date), 'd MMM', { locale: ru })}
          </div>
          
          <img
            src={getWeatherIcon(day.icon, '2x')}
            alt={day.description}
            className="w-16 h-16 mx-auto mb-2"
          />
          
          <div className="text-lg font-bold text-gray-900 dark:text-white mb-1">
            {Math.round(day.temperature.max)}°
          </div>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            {Math.round(day.temperature.min)}°
          </div>
          
          <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-center space-x-2 text-xs text-gray-600 dark:text-gray-400">
              <span>💧 {day.humidity}%</span>
            </div>
          </div>
        </Card>
      ))}
    </div>
  );
};
