import type { HTMLAttributes, ReactNode } from 'react';

interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  hover?: boolean;
}

export const Card = ({ children, hover = false, className = '', ...props }: CardProps) => {
  return (
    <div
      className={`
        bg-white dark:bg-gray-800
        rounded-xl shadow-md
        border border-gray-200 dark:border-gray-700
        transition-default
        ${hover ? 'hover:-translate-y-1 hover:shadow-xl cursor-pointer' : ''}
        ${className}
      `}
      {...props}
    >
      {children}
    </div>
  );
};
