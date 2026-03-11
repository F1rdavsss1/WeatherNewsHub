import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiSearch, FiUser, FiMenu, FiX, FiBell } from 'react-icons/fi';
import { useStore } from '../../store/useStore';
import { SearchBar } from '../weather/SearchBar';

export const Header = () => {
  const { user } = useStore();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  return (
    <header className="sticky top-0 z-50 glass-effect">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-20">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-3">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
              </svg>
            </div>
            <div className="hidden sm:block">
              <div className="text-xl font-bold">
                <span className="text-white">WeatherNews</span>
                <span className="text-primary-400">Hub</span>
              </div>
            </div>
          </Link>

          {/* Desktop Search */}
          <div className="hidden md:block flex-1 max-w-xl mx-8">
            <SearchBar />
          </div>

          {/* Desktop Actions */}
          <div className="hidden md:flex items-center space-x-3">
            <button className="p-3 rounded-xl hover:bg-dark-cardHover transition-default">
              <FiSearch className="w-5 h-5 text-gray-400" />
            </button>

            <button className="p-3 rounded-xl hover:bg-dark-cardHover transition-default relative">
              <FiBell className="w-5 h-5 text-gray-400" />
              <span className="absolute top-2 right-2 w-2 h-2 bg-primary-500 rounded-full"></span>
            </button>

            {user ? (
              <Link to="/profile">
                <div className="flex items-center space-x-2 px-4 py-2 rounded-xl hover:bg-dark-cardHover transition-default">
                  {user.photoUrl ? (
                    <img src={user.photoUrl} alt={user.username} className="w-8 h-8 rounded-full" />
                  ) : (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-primary-500 to-primary-700 flex items-center justify-center text-white text-sm font-semibold">
                      {user.username[0].toUpperCase()}
                    </div>
                  )}
                  <span className="text-sm font-medium text-white">
                    {user.username}
                  </span>
                </div>
              </Link>
            ) : (
              <Link to="/login">
                <button className="flex items-center space-x-2 px-5 py-2.5 bg-primary-600 hover:bg-primary-700 rounded-xl transition-default">
                  <FiUser className="w-4 h-4" />
                  <span className="font-medium">Войти</span>
                </button>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="md:hidden p-2 rounded-xl hover:bg-dark-cardHover"
          >
            {mobileMenuOpen ? (
              <FiX className="w-6 h-6 text-gray-400" />
            ) : (
              <FiMenu className="w-6 h-6 text-gray-400" />
            )}
          </button>
        </div>

        {/* Mobile Search */}
        <div className="md:hidden pb-4">
          <SearchBar />
        </div>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="md:hidden border-t border-dark-border bg-dark-card/95 backdrop-blur-xl">
          <div className="container mx-auto px-4 py-4 space-y-3">
            <button className="w-full flex items-center space-x-3 p-3 rounded-xl hover:bg-dark-cardHover text-left">
              <FiBell className="w-5 h-5 text-gray-400" />
              <span className="text-white">Уведомления</span>
            </button>

            {user ? (
              <Link
                to="/profile"
                className="w-full flex items-center space-x-3 p-3 rounded-xl hover:bg-dark-cardHover"
                onClick={() => setMobileMenuOpen(false)}
              >
                <FiUser className="w-5 h-5 text-gray-400" />
                <span className="text-white">Профиль</span>
              </Link>
            ) : (
              <Link to="/login" onClick={() => setMobileMenuOpen(false)}>
                <button className="w-full px-5 py-3 bg-primary-600 hover:bg-primary-700 rounded-xl transition-default text-white font-medium">
                  Войти
                </button>
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
};
