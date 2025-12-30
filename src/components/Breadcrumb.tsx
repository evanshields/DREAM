import React from 'react';
import { ChevronRight, Home } from 'lucide-react';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  onClick?: () => void;
}

interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ items, className = '' }) => {
  return (
    <nav aria-label="Breadcrumb" className={className}>
      <ol className="flex items-center gap-2 text-sm text-secondary flex-wrap">
        {items.map((item, index) => {
          const isLast = index === items.length - 1;
          return (
            <li key={index} className="flex items-center">
              {index === 0 && (
                <Home className="w-4 h-4 mr-1 text-secondary-muted" aria-hidden="true" />
              )}
              {isLast ? (
                <span className="text-primary font-medium" aria-current="page">
                  {item.label}
                </span>
              ) : (
                <>
                  {item.onClick ? (
                    <button
                      onClick={item.onClick}
                      className="hover:text-primary hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded px-1"
                      aria-label={`Navigate to ${item.label}`}
                    >
                      {item.label}
                    </button>
                  ) : (
                    <a
                      href={item.href}
                      className="hover:text-primary hover:underline focus:outline-none focus:ring-2 focus:ring-primary rounded px-1"
                    >
                      {item.label}
                    </a>
                  )}
                </>
              )}
              {!isLast && (
                <ChevronRight className="w-4 h-4 mx-2 text-secondary-muted" aria-hidden="true" />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
};

export default Breadcrumb;

