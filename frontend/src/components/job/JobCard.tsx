import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  onClick?: () => void;
}

const JobCard: React.FC<JobCardProps> = ({ job, onClick }) => {
  const navigate = useNavigate();

  const formatSalary = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `${job.salary_currency}${job.salary_min.toLocaleString()} - ${job.salary_currency}${job.salary_max.toLocaleString()} ${job.salary_type}`;
    } else if (job.salary_min) {
      return `${job.salary_currency}${job.salary_min.toLocaleString()}+ ${job.salary_type}`;
    }
    return null;
  };

  const getExperienceLevelDisplay = (level: string) => {
    const levelMap: Record<string, string> = {
      entry: 'Entry Level',
      junior: 'Junior',
      mid: 'Mid Level',
      senior: 'Senior',
      lead: 'Lead',
      executive: 'Executive'
    };
    return levelMap[level] || level;
  };

  const handleClick = () => {
    if (onClick) {
      onClick();
    } else {
      // Default behavior: navigate to job detail page
      navigate(`/jobs/${job.id}`);
    }
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      handleClick();
    }
  };

  return (
    <div
      className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 cursor-pointer border border-gray-200 hover:border-blue-300"
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`View details for ${job.title} at ${job.company.name}`}
    >
      {/* Header with badges */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex gap-2">
          {job.is_new && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
              New
            </span>
          )}
          {job.is_featured && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
              Featured
            </span>
          )}
          {job.is_urgent && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800">
              Urgent
            </span>
          )}
        </div>
        {job.is_remote && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
            Remote
          </span>
        )}
      </div>

      {/* Company logo placeholder */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
          {job.company.logo ? (
            <img
              src={job.company.logo}
              alt={`${job.company.name} logo`}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            <span className="text-gray-500 text-sm font-medium">
              {job.company.name.charAt(0).toUpperCase()}
            </span>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          {/* Job title */}
          <h3 className="text-lg font-semibold text-gray-900 mb-1 line-clamp-2">
            {job.title}
          </h3>
          
          {/* Company name */}
          <p className="text-sm text-gray-600 mb-2">
            {job.company.name}
          </p>
        </div>
      </div>

      {/* Location */}
      <div className="flex items-center text-sm text-gray-600 mb-3">
        <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
        </svg>
        <span className="truncate">{job.location}</span>
      </div>

      {/* Salary */}
      {formatSalary(job) && (
        <div className="flex items-center text-sm text-gray-600 mb-3">
          <svg className="w-4 h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
          </svg>
          <span className="truncate">{formatSalary(job)}</span>
        </div>
      )}

      {/* Experience level and categories */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
          {getExperienceLevelDisplay(job.experience_level)}
        </span>
        {job.categories.slice(0, 2).map((category) => (
          <span
            key={category.id}
            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            {category.name}
          </span>
        ))}
        {job.categories.length > 2 && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            +{job.categories.length - 2} more
          </span>
        )}
      </div>

      {/* Footer with posted date and application count */}
      <div className="flex justify-between items-center text-xs text-gray-500 pt-3 border-t border-gray-100">
        <span>{job.days_since_posted}</span>
        <span>{job.applications_count} applications</span>
      </div>
    </div>
  );
};

export default JobCard;