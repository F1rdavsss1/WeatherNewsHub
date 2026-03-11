import { useState, useRef, useEffect } from 'react';
import { FiSearch } from 'react-icons/fi';
import { useStore } from '../../store/useStore';
import { POPULAR_CITIES } from '../../lib/constants';

export const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const { setCurrentCity } = useStore();
  const wrapperRef = useRef<HTMLDivElement>(null);

  const filteredCities = query
    ? POPULAR_CITIES.filter(city => city.toLowerCase().includes(query.toLowerCase()))
    : POPULAR_CITIES.slice(0, 5);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSelectCity = (city: string) => {
    setCurrentCity(city);
    setQuery('');
    setIsOpen(false);
  };

  return (
    <div ref={wrapperRef} className="relative w-full">
      <div className="relative">
        <FiSearch className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-500 w-5 h-5" />
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setIsOpen(true);
          }}
          onFocus={() => setIsOpen(true)}
          placeholder="Поиск города"
          className="w-full pl-12 pr-4 py-3 rounded-xl bg-dark-card/50 border border-dark-border text-white placeholder-gray-500 focus:outline-none focus:border-primary-500 transition-default"
        />
      </div>

      {isOpen && filteredCities.length > 0 && (
        <div className="absolute top-full left-0 right-0 mt-2 bg-dark-card border border-dark-border rounded-xl shadow-2xl max-h-64 overflow-y-auto z-50">
          {filteredCities.map((city) => (
            <button
              key={city}
              onClick={() => handleSelectCity(city)}
              className="w-full px-4 py-3 text-left hover:bg-dark-cardHover transition-default first:rounded-t-xl last:rounded-b-xl"
            >
              <span className="text-white font-medium">{city}</span>
              <span className="text-gray-500 text-sm ml-2">Россия</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
};
