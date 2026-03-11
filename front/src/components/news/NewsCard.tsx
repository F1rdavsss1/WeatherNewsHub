import { Card } from '../ui/Card';
import type { NewsArticle } from '../../types';
import { formatDistanceToNow } from 'date-fns';
import { ru } from 'date-fns/locale';

interface NewsCardProps {
  article: NewsArticle;
}

export const NewsCard = ({ article }: NewsCardProps) => {
  const timeAgo = formatDistanceToNow(new Date(article.publishedAt), {
    addSuffix: true,
    locale: ru,
  });

  return (
    <Card hover className="overflow-hidden h-full flex flex-col">
      {article.urlToImage && (
        <div className="aspect-video w-full overflow-hidden">
          <img
            src={article.urlToImage}
            alt={article.title}
            className="w-full h-full object-cover"
            onError={(e) => {
              (e.target as HTMLImageElement).src = 'https://via.placeholder.com/400x225?text=No+Image';
            }}
          />
        </div>
      )}
      
      <div className="p-4 flex-1 flex flex-col">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
          {article.title}
        </h3>
        
        {article.description && (
          <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-3 flex-1">
            {article.description}
          </p>
        )}
        
        <div className="flex items-center justify-between mt-auto">
          <div className="flex items-center space-x-2 text-sm text-gray-500 dark:text-gray-400">
            <span className="font-medium">{article.source.name}</span>
            <span>•</span>
            <span>{timeAgo}</span>
          </div>
          
          <a
            href={article.url}
            target="_blank"
            rel="noopener noreferrer"
            className="text-primary-500 hover:text-primary-600 text-sm font-medium transition-default"
          >
            Читать →
          </a>
        </div>
      </div>
    </Card>
  );
};
