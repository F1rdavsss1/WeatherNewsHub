import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiUser, FiStar, FiSettings, FiLogOut } from 'react-icons/fi';
import { useStore } from '../store/useStore';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import toast from 'react-hot-toast';

export const Profile = () => {
  const navigate = useNavigate();
  const { user, logout } = useStore();
  const [activeTab, setActiveTab] = useState<'profile' | 'favorites' | 'settings'>('profile');

  if (!user) {
    navigate('/login');
    return null;
  }

  const handleLogout = () => {
    logout();
    toast.success('Вы вышли из аккаунта');
    navigate('/');
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
        Личный кабинет
      </h1>

      {/* Profile Header */}
      <Card className="p-6 mb-8">
        <div className="flex items-center space-x-4">
          {user.photoUrl ? (
            <img
              src={user.photoUrl}
              alt={user.username}
              className="w-20 h-20 rounded-full"
            />
          ) : (
            <div className="w-20 h-20 rounded-full bg-primary-500 flex items-center justify-center text-white text-3xl font-bold">
              {user.username[0].toUpperCase()}
            </div>
          )}
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {user.username}
            </h2>
            {user.email && (
              <p className="text-gray-600 dark:text-gray-400">{user.email}</p>
            )}
          </div>
          <Button variant="secondary" onClick={handleLogout}>
            <FiLogOut className="w-4 h-4 mr-2 inline" />
            Выйти
          </Button>
        </div>
      </Card>

      {/* Tabs */}
      <div className="flex space-x-2 border-b border-gray-200 dark:border-gray-700 mb-6">
        <button
          onClick={() => setActiveTab('profile')}
          className={`flex items-center space-x-2 px-4 py-2 font-medium transition-default ${
            activeTab === 'profile'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          <FiUser className="w-4 h-4" />
          <span>Профиль</span>
        </button>
        <button
          onClick={() => setActiveTab('favorites')}
          className={`flex items-center space-x-2 px-4 py-2 font-medium transition-default ${
            activeTab === 'favorites'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          <FiStar className="w-4 h-4" />
          <span>Избранное</span>
        </button>
        <button
          onClick={() => setActiveTab('settings')}
          className={`flex items-center space-x-2 px-4 py-2 font-medium transition-default ${
            activeTab === 'settings'
              ? 'text-primary-500 border-b-2 border-primary-500'
              : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
          }`}
        >
          <FiSettings className="w-4 h-4" />
          <span>Настройки</span>
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'profile' && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Информация профиля
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Имя пользователя
              </label>
              <p className="text-gray-900 dark:text-white">{user.username}</p>
            </div>
            {user.email && (
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Email
                </label>
                <p className="text-gray-900 dark:text-white">{user.email}</p>
              </div>
            )}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                Город по умолчанию
              </label>
              <p className="text-gray-900 dark:text-white">{user.defaultCity || 'Не установлен'}</p>
            </div>
          </div>
        </Card>
      )}

      {activeTab === 'favorites' && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Избранные города
          </h3>
          {user.favoriteCities.length > 0 ? (
            <div className="space-y-2">
              {user.favoriteCities.map((city) => (
                <div
                  key={city}
                  className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg"
                >
                  <span className="text-gray-900 dark:text-white">{city}</span>
                  <button
                    onClick={() => toast('Функция в разработке')}
                    className="text-red-500 hover:text-red-600 text-sm"
                  >
                    Удалить
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-600 dark:text-gray-400">
              У вас пока нет избранных городов
            </p>
          )}
          <Button variant="primary" className="mt-4" onClick={() => toast('Функция в разработке')}>
            Добавить город
          </Button>
        </Card>
      )}

      {activeTab === 'settings' && (
        <Card className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Настройки
          </h3>
          <div className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Тема
              </label>
              <select
                value={user.theme}
                onChange={() => toast('Функция в разработке')}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="light">Светлая</option>
                <option value="dark">Тёмная</option>
                <option value="system">Системная</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Язык
              </label>
              <select
                value={user.language}
                onChange={() => toast('Функция в разработке')}
                className="w-full px-4 py-2 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100"
              >
                <option value="ru">Русский</option>
                <option value="en">English</option>
              </select>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                  Ежедневная рассылка
                </label>
                <p className="text-sm text-gray-500 dark:text-gray-400">
                  Получать погоду и новости каждый день
                </p>
              </div>
              <input
                type="checkbox"
                checked={user.dailyDigest}
                onChange={() => toast('Функция в разработке')}
                className="w-5 h-5 text-primary-500 rounded focus:ring-primary-500"
              />
            </div>

            <Button variant="primary" onClick={() => toast.success('Настройки сохранены')}>
              Сохранить изменения
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
