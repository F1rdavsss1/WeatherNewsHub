export const NEWS_CATEGORIES = [
  { value: '', label: 'Все' },
  { value: 'general', label: 'Главные' },
  { value: 'technology', label: 'Технологии' },
  { value: 'science', label: 'Наука' },
  { value: 'sports', label: 'Спорт' },
  { value: 'business', label: 'Бизнес' },
  { value: 'health', label: 'Здоровье' },
  { value: 'entertainment', label: 'Развлечения' },
] as const;

export const COUNTRIES = [
  { value: 'ru', label: 'Россия', flag: '🇷🇺' },
  { value: 'us', label: 'США', flag: '🇺🇸' },
  { value: 'gb', label: 'Великобритания', flag: '🇬🇧' },
  { value: 'de', label: 'Германия', flag: '🇩🇪' },
  { value: 'fr', label: 'Франция', flag: '🇫🇷' },
] as const;

export const POPULAR_CITIES = [
  'Москва',
  'Санкт-Петербург',
  'Новосибирск',
  'Екатеринбург',
  'Казань',
  'Нижний Новгород',
  'Челябинск',
  'Самара',
  'Омск',
  'Ростов-на-Дону',
  'Уфа',
  'Красноярск',
  'Воронеж',
  'Пермь',
  'Волгоград',
] as const;

export const WEATHER_TABS = [
  { value: 'now', label: 'Сейчас' },
  { value: 'hourly', label: 'По часам' },
  { value: 'week', label: 'На неделю' },
] as const;

export const THEME_OPTIONS = [
  { value: 'light', label: 'Светлая', icon: '☀️' },
  { value: 'dark', label: 'Тёмная', icon: '🌙' },
  { value: 'system', label: 'Системная', icon: '💻' },
] as const;

export const LANGUAGE_OPTIONS = [
  { value: 'ru', label: 'Русский', flag: '🇷🇺' },
  { value: 'en', label: 'English', flag: '🇬🇧' },
] as const;

export const API_ENDPOINTS = {
  WEATHER_CURRENT: '/weather/current',
  WEATHER_FORECAST: '/weather/forecast',
  NEWS: '/news',
  AUTH_LOGIN: '/auth/login',
  AUTH_REGISTER: '/auth/register',
  AUTH_TELEGRAM: '/auth/telegram',
  USER_PROFILE: '/user/profile',
  USER_FAVORITES: '/user/favorites',
} as const;

export const QUERY_KEYS = {
  WEATHER: 'weather',
  FORECAST: 'forecast',
  NEWS: 'news',
  USER: 'user',
} as const;

export const STORAGE_KEYS = {
  TOKEN: 'token',
  THEME: 'theme',
  LANGUAGE: 'language',
} as const;
