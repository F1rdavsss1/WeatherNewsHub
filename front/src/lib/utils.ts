export const getWeatherIcon = (icon: string, size: '2x' | '4x' = '2x') => {
  return `https://openweathermap.org/img/wn/${icon}@${size}.png`;
};

export const getWeatherEmoji = (icon: string): string => {
  const iconMap: Record<string, string> = {
    '01d': '☀️',
    '01n': '🌙',
    '02d': '⛅',
    '02n': '☁️',
    '03d': '☁️',
    '03n': '☁️',
    '04d': '☁️',
    '04n': '☁️',
    '09d': '🌧️',
    '09n': '🌧️',
    '10d': '🌦️',
    '10n': '🌧️',
    '11d': '⛈️',
    '11n': '⛈️',
    '13d': '❄️',
    '13n': '❄️',
    '50d': '🌫️',
    '50n': '🌫️',
  };
  
  return iconMap[icon] || '🌤️';
};

export const formatTemperature = (temp: number): string => {
  return `${Math.round(temp)}°`;
};

export const formatPressure = (pressure: number): string => {
  return `${Math.round(pressure * 0.75)} мм`;
};

export const formatWindSpeed = (speed: number): string => {
  return `${speed.toFixed(1)} м/с`;
};

export const getWindDirection = (degrees: number): string => {
  const directions = ['С', 'СВ', 'В', 'ЮВ', 'Ю', 'ЮЗ', 'З', 'СЗ'];
  const index = Math.round(degrees / 45) % 8;
  return directions[index];
};

export const cn = (...classes: (string | undefined | null | false)[]): string => {
  return classes.filter(Boolean).join(' ');
};
