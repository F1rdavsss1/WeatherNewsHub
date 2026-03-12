import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { authApi } from '../lib/api';
import { useStore } from '../store/useStore';
import toast from 'react-hot-toast';

export const Login = () => {
  const navigate = useNavigate();
  const { setUser } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [code, setCode] = useState('');
  const [showCodeInput, setShowCodeInput] = useState(false);

  const handleTelegramLogin = async () => {
    if (!code || code.length !== 6) {
      toast.error('Введите 6-значный код из Telegram');
      return;
    }

    setIsLoading(true);
    try {
      const response = await authApi.loginWithTelegram(code);
      
      if (response.success) {
        setUser(response.user);
        localStorage.setItem('telegram_user', JSON.stringify(response.user));
        toast.success('Вход выполнен успешно!');
        navigate('/');
      } else {
        toast.error(response.message || 'Неверный код');
      }
    } catch (error: any) {
      toast.error('Ошибка входа. Проверьте код.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-dark flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-md glass-effect rounded-3xl p-8">
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">
            Вход через Telegram
          </h1>
          <p className="text-gray-400">
            Получите код в Telegram боте
          </p>
        </div>

        {!showCodeInput ? (
          <div className="space-y-4">
            <div className="bg-blue-500/10 border border-blue-500/30 rounded-xl p-4 mb-6">
              <p className="text-blue-300 text-sm mb-2">
                📱 Как войти:
              </p>
              <ol className="text-gray-300 text-sm space-y-1 list-decimal list-inside">
                <li>Откройте Telegram бот @WeatherNewsHubot</li>
                <li>Отправьте команду /login</li>
                <li>Скопируйте полученный код</li>
                <li>Введите код ниже</li>
              </ol>
            </div>

            <button
              onClick={() => setShowCodeInput(true)}
              className="w-full px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-xl transition-default text-white font-medium flex items-center justify-center space-x-2"
            >
              <span>✈️</span>
              <span>У меня есть код</span>
            </button>

            <a
              href="https://t.me/WeatherNewsHubot"
              target="_blank"
              rel="noopener noreferrer"
              className="block w-full px-6 py-3 bg-dark-card/50 hover:bg-dark-cardHover border border-dark-border rounded-xl transition-default text-white font-medium text-center"
            >
              Открыть Telegram бота
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Код из Telegram
              </label>
              <input
                type="text"
                placeholder="123456"
                maxLength={6}
                value={code}
                onChange={(e) => setCode(e.target.value.replace(/\D/g, ''))}
                className="w-full px-4 py-3 rounded-xl bg-dark-card/50 border border-dark-border text-white text-center text-2xl tracking-widest placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-default"
                autoFocus
              />
              <p className="mt-2 text-xs text-gray-400 text-center">
                Код действителен 5 минут
              </p>
            </div>

            <button
              onClick={handleTelegramLogin}
              disabled={isLoading || code.length !== 6}
              className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl transition-default text-white font-medium disabled:opacity-50"
            >
              {isLoading ? 'Проверка...' : 'Войти'}
            </button>

            <button
              onClick={() => {
                setShowCodeInput(false);
                setCode('');
              }}
              className="w-full px-6 py-3 bg-dark-card/50 hover:bg-dark-cardHover rounded-xl transition-default text-gray-300 font-medium"
            >
              Назад
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
