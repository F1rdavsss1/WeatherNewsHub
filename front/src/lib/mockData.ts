import type { WeatherResponse, ForecastResponse, NewsResponse } from '../types';

export const mockWeather: WeatherResponse = {
  city: 'Москва',
  country: 'RU',
  temperature: 5,
  feelsLike: 2,
  humidity: 76,
  pressure: 1013,
  windSpeed: 3,
  windDirection: 180,
  clouds: 40,
  visibility: 10,
  description: 'Переменная облачность',
  icon: '02d',
  sunrise: Date.now() / 1000 - 3600,
  sunset: Date.now() / 1000 + 7200,
  timestamp: Date.now() / 1000,
};

export const mockForecast: ForecastResponse = {
  days: Array.from({ length: 30 }, (_, i) => {
    const baseTemp = 5;
    const tempVariation = Math.sin(i / 3) * 4; // Волнообразное изменение
    const randomVariation = (Math.random() - 0.5) * 3;
    
    const icons = ['01d', '02d', '03d', '04d', '09d', '10d', '13d'];
    const descriptions = ['Ясно', 'Малооблачно', 'Облачно', 'Пасмурно', 'Дождь', 'Небольшой дождь', 'Снег'];
    
    const iconIndex = Math.floor(Math.random() * icons.length);
    
    return {
      date: new Date(Date.now() + 86400000 * i).toISOString(),
      temperature: {
        min: Math.round(baseTemp + tempVariation + randomVariation - 2),
        max: Math.round(baseTemp + tempVariation + randomVariation + 5),
        day: Math.round(baseTemp + tempVariation + randomVariation + 1.5)
      },
      description: descriptions[iconIndex],
      icon: icons[iconIndex],
      humidity: 65 + Math.floor(Math.random() * 20),
      windSpeed: 2 + Math.random() * 4,
    };
  }),
};

export const mockNews: NewsResponse = {
  articles: [
    {
      title: 'Новый прорыв в квантовых вычислениях',
      description: 'Ученые объявили о создании самого мощного квантового компьютера, способного решать задачи, недоступные классическим суперкомпьютерам.',
      url: 'https://example.com/news1',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 7200000).toISOString(),
      source: { name: 'TechNews' },
    },
    {
      title: 'Запуск новой космической миссии на Марс',
      description: 'NASA объявило о запуске новой миссии по исследованию Марса с целью поиска признаков древней жизни.',
      url: 'https://example.com/news2',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 14400000).toISOString(),
      source: { name: 'Space Today' },
    },
    {
      title: 'Революция в области искусственного интеллекта',
      description: 'Новая модель ИИ демонстрирует беспрецедентные способности в понимании и генерации естественного языка.',
      url: 'https://example.com/news3',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 21600000).toISOString(),
      source: { name: 'AI Weekly' },
    },
    {
      title: 'Открытие нового вида динозавров',
      description: 'Палеонтологи обнаружили останки ранее неизвестного вида динозавров, жившего 70 миллионов лет назад.',
      url: 'https://example.com/news4',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 28800000).toISOString(),
      source: { name: 'Science Daily' },
    },
    {
      title: 'Прорыв в лечении рака',
      description: 'Новый метод иммунотерапии показал 90% эффективность в клинических испытаниях.',
      url: 'https://example.com/news5',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 36000000).toISOString(),
      source: { name: 'Medical News' },
    },
    {
      title: 'Новая технология солнечных панелей',
      description: 'Разработаны солнечные панели с эффективностью 50%, что вдвое превышает текущие показатели.',
      url: 'https://example.com/news6',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 43200000).toISOString(),
      source: { name: 'Green Tech' },
    },
    {
      title: 'Достижения в области робототехники',
      description: 'Представлен новый робот с улучшенными возможностями взаимодействия с людьми.',
      url: 'https://example.com/news7',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 50400000).toISOString(),
      source: { name: 'Robotics Weekly' },
    },
    {
      title: 'Прогресс в области биотехнологий',
      description: 'Ученые создали новый биоматериал с уникальными свойствами для медицинских применений.',
      url: 'https://example.com/news8',
      urlToImage: null,
      publishedAt: new Date(Date.now() - 57600000).toISOString(),
      source: { name: 'BioTech News' },
    },
  ],
  totalResults: 100,
  page: 1,
  pageSize: 8,
};
