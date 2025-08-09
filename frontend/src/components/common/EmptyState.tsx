import React from 'react';
import { Search, Briefcase, Filter, Plus } from 'lucide-react';

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
    variant?: 'primary' | 'secondary';
  };
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
}) => {
  return (
    <div className={`text-center py-12 px-4 ${className}`}>
      <div className="flex justify-center mb-4">
        {icon || <Briefcase className="h-12 w-12 text-gray-400" />}
      </div>
      
      <h3 className="text-lg font-medium text-gray-900 mb-2">
        {title}
      </h3>
      
      <p className="text-gray-600 mb-6 max-w-md mx-auto">
        {description}
      </p>
      
      {action && (
        <button
          onClick={action.onClick}
          className={`inline-flex items-center px-4 py-2 rounded-md font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 ${
            action.variant === 'secondary'
              ? 'bg-gray-100 text-gray-700 hover:bg-gray-200 focus:ring-gray-500'
              : 'bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500'
          }`}
        >
          {action.label}
        </button>
      )}
    </div>
  );
};

// Specific empty state components for common scenarios
export const NoJobsFound: React.FC<{
  hasFilters?: boolean;
  onClearFilters?: () => void;
  onBrowseAll?: () => void;
}> = ({ hasFilters, onClearFilters, onBrowseAll }) => {
  if (hasFilters) {
    return (
      <EmptyState
        icon={<Filter className="h-12 w-12 text-gray-400" />}
        title="No jobs match your filters"
        description="Try adjusting your search criteria or clearing some filters to see more results."
        action={
          onClearFilters
            ? {
                label: 'Clear Filters',
                onClick: onClearFilters,
                variant: 'secondary',
              }
            : undefined
        }
      />
    );
  }

  return (
    <EmptyState
      icon={<Briefcase className="h-12 w-12 text-gray-400" />}
      title="No jobs available"
      description="There are currently no job postings available. Check back later for new opportunities."
      action={
        onBrowseAll
          ? {
              label: 'Browse All Jobs',
              onClick: onBrowseAll,
            }
          : undefined
      }
    />
  );
};

export const NoSearchResults: React.FC<{
  searchQuery: string;
  onClearSearch?: () => void;
}> = ({ searchQuery, onClearSearch }) => (
  <EmptyState
    icon={<Search className="h-12 w-12 text-gray-400" />}
    title={`No results for "${searchQuery}"`}
    description="Try searching with different keywords or check your spelling."
    action={
      onClearSearch
        ? {
            label: 'Clear Search',
            onClick: onClearSearch,
            variant: 'secondary',
          }
        : undefined
    }
  />
);

export const NoApplications: React.FC<{
  onBrowseJobs?: () => void;
}> = ({ onBrowseJobs }) => (
  <EmptyState
    icon={<Plus className="h-12 w-12 text-gray-400" />}
    title="No applications yet"
    description="You haven't applied to any jobs yet. Start browsing to find your next opportunity."
    action={
      onBrowseJobs
        ? {
            label: 'Browse Jobs',
            onClick: onBrowseJobs,
          }
        : undefined
    }
  />
);