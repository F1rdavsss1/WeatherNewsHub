import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { authApi } from '../lib/api';
import { useStore } from '../store/useStore';
import toast from 'react-hot-toast';

const loginSchema = z.object({
  email: z.string().email('Неверный формат email'),
  password: z.string().min(6, 'Пароль должен быть не менее 6 символов'),
});

type LoginForm = z.infer<typeof loginSchema>;

export const Login = () => {
  const navigate = useNavigate();
  const { setUser, setToken } = useStore();
  const [isLoading, setIsLoading] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginForm) => {
    setIsLoading(true);
    try {
      const response = await authApi.loginWithEmail(data.email, data.password);
      setToken(response.token);
      setUser(response.user);
      toast.success('Вход выполнен успешно!');
      navigate('/');
    } catch (error: any) {
      toast.error(error.response?.data?.message || 'Ошибка входа');
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
            Вход в аккаунт
          </h1>
          <p className="text-gray-400">
            Войдите, чтобы получить доступ ко всем функциям
          </p>
        </div>

        {/* Telegram Login */}
        <div className="mb-6">
          <button
            className="w-full px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded-xl transition-default text-white font-medium flex items-center justify-center space-x-2"
            onClick={() => toast.success('Telegram авторизация в разработке')}
          >
            <span>✈️</span>
            <span>Войти через Telegram</span>
          </button>
        </div>

        <div className="relative mb-6">
          <div className="absolute inset-0 flex items-center">
            <div className="w-full border-t border-dark-border"></div>
          </div>
          <div className="relative flex justify-center text-sm">
            <span className="px-2 bg-dark-card text-gray-500">или</span>
          </div>
        </div>

        {/* Email Login Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
            <input
              type="email"
              placeholder="your@email.com"
              className="w-full px-4 py-3 rounded-xl bg-dark-card/50 border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-default"
              {...register('email')}
            />
            {errors.email && (
              <p className="mt-1 text-sm text-red-400">{errors.email.message}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Пароль</label>
            <input
              type="password"
              placeholder="••••••••"
              className="w-full px-4 py-3 rounded-xl bg-dark-card/50 border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-default"
              {...register('password')}
            />
            {errors.password && (
              <p className="mt-1 text-sm text-red-400">{errors.password.message}</p>
            )}
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full px-6 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl transition-default text-white font-medium disabled:opacity-50"
          >
            {isLoading ? 'Загрузка...' : 'Войти'}
          </button>
        </form>

        <div className="mt-6 text-center space-y-2">
          <button className="text-sm text-primary-400 hover:text-primary-300 transition-default">
            Забыли пароль?
          </button>
          <div className="text-sm text-gray-400">
            Нет аккаунта?{' '}
            <button
              onClick={() => navigate('/register')}
              className="text-primary-400 hover:text-primary-300 font-medium transition-default"
            >
              Зарегистрироваться
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
