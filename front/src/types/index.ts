export interface WeatherResponse {
  city: string;
  country: string;
  temperature: number;
  feelsLike: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  windDirection: number;
  clouds: number;
  visibility: number;
  description: string;
  icon: string;
  sunrise: number;
  sunset: number;
  timestamp: number;
}

export interface ForecastDay {
  date: string;
  temperature: {
    min: number;
    max: number;
    day: number;
  };
  description: string;
  icon: string;
  humidity: number;
  windSpeed: number;
  hourly?: HourlyForecast[];
}

export interface HourlyForecast {
  time: string;
  temperature: number;
  icon: string;
  description: string;
}

export interface ForecastResponse {
  days: ForecastDay[];
}

export interface NewsArticle {
  title: string;
  description: string;
  url: string;
  urlToImage: string;
  publishedAt: string;
  source: {
    name: string;
  };
}

export interface NewsResponse {
  articles: NewsArticle[];
  totalResults: number;
  page: number;
  pageSize: number;
}

export interface User {
  id: number;
  username: string;
  email?: string;
  photoUrl?: string;
  defaultCity?: string;
  favoriteCities: string[];
  newsCategories: string[];
  dailyDigest: boolean;
  digestTime: string;
  digestContent: 'weather' | 'both';
  theme: 'light' | 'dark' | 'system';
  language: 'ru' | 'en';
}

export interface NewsParams {
  category?: string;
  country?: string;
  q?: string;
  page?: number;
  pageSize?: number;
}
