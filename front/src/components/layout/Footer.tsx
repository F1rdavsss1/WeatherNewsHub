import { Link } from 'react-router-dom';

export const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-50 dark:bg-gray-900 border-t border-gray-200 dark:border-gray-800 mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* About */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              WeatherNews Hub
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Современный сервис погоды и новостей с персонализацией и синхронизацией с Telegram-ботом.
            </p>
          </div>

          {/* Links */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Ссылки
            </h3>
            <ul className="space-y-2 text-sm">
              <li>
                <a
                  href="https://openweathermap.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-default"
                >
                  OpenWeatherMap API
                </a>
              </li>
              <li>
                <a
                  href="https://newsapi.org"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-default"
                >
                  NewsAPI
                </a>
              </li>
              <li>
                <Link
                  to="/privacy"
                  className="text-gray-600 dark:text-gray-400 hover:text-primary-500 transition-default"
                >
                  Политика конфиденциальности
                </Link>
              </li>
            </ul>
          </div>

          {/* Telegram Bot */}
          <div>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              Telegram Bot
            </h3>
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Получайте погоду и новости прямо в Telegram
            </p>
            <a
              href={`https://t.me/${import.meta.env.VITE_TELEGRAM_BOT_NAME}`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-default text-sm"
            >
              🤖 Открыть бота
            </a>
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-800 text-center text-sm text-gray-600 dark:text-gray-400">
          © {currentYear} WeatherNews Hub. Все права защищены.
        </div>
      </div>
    </footer>
  );
};
