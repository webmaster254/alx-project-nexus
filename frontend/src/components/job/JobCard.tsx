import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useResponsive } from '../../hooks';
import { useBookmark } from '../../contexts/BookmarkContext';
import { shareService } from '../../services/shareService';
import { Job } from '../../types';

interface JobCardProps {
  job: Job;
  onClick?: () => void;
  showActions?: boolean;
}

const JobCard: React.FC<JobCardProps> = ({ job, onClick, showActions = true }) => {
  const navigate = useNavigate();
  const { isMobile } = useResponsive();
  const { isJobBookmarked, toggleBookmark } = useBookmark();
  const [isBookmarking, setIsBookmarking] = useState(false);
  const [showShareMenu, setShowShareMenu] = useState(false);

  // Handle both list and detail API response formats
  const companyName = job.company?.name || (job as any).company_name || 'Unknown Company';
  const companyLogo = job.company?.logo || (job as any).company_logo;

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

  const handleBookmarkClick = async (e: React.MouseEvent) => {
    e.stopPropagation();
    if (isBookmarking) return;

    try {
      setIsBookmarking(true);
      await toggleBookmark(job.id);
    } catch (error) {
      console.error('Failed to toggle bookmark:', error);
    } finally {
      setIsBookmarking(false);
    }
  };

  const handleShareClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    setShowShareMenu(!showShareMenu);
  };

  const handleShareOption = async (type: 'copy' | 'email' | 'linkedin' | 'twitter') => {
    setShowShareMenu(false);
    
    try {
      switch (type) {
        case 'copy':
          { const success = await shareService.shareJob(job);
          if (success) {
            // Could show a toast notification here
            console.log('Link copied to clipboard');
          }
          break; }
        case 'email':
          shareService.shareViaEmail(job);
          break;
        case 'linkedin':
          shareService.shareOnLinkedIn(job);
          break;
        case 'twitter':
          shareService.shareOnTwitter(job);
          break;
      }
    } catch (error) {
      console.error('Failed to share job:', error);
    }
  };

  return (
    <div
      className={`bg-white rounded-lg shadow-md hover:shadow-lg active:shadow-xl transition-all duration-200 cursor-pointer border border-gray-200 hover:border-blue-300 active:border-blue-400 touch-manipulation tap-highlight-none select-none ${
        isMobile ? 'p-4' : 'p-4 sm:p-6'
      }`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`View details for ${job.title} at ${companyName}`}
      style={{ minHeight: isMobile ? '120px' : '44px' }} // Larger minimum height for mobile
    >
      {/* Header with badges and actions */}
      <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start mb-3 gap-2">
        <div className="flex flex-wrap gap-1 sm:gap-2">
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
          {job.is_remote && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
              Remote
            </span>
          )}
        </div>

        {/* Action buttons */}
        {showActions && (
          <div className="flex items-center gap-1 relative">
            {/* Bookmark button */}
            <button
              onClick={handleBookmarkClick}
              disabled={isBookmarking}
              className={`p-2 rounded-full transition-colors duration-200 touch-manipulation ${
                isJobBookmarked(job.id)
                  ? 'text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100'
                  : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
              } ${isBookmarking ? 'opacity-50 cursor-not-allowed' : ''}`}
              aria-label={isJobBookmarked(job.id) ? 'Remove from bookmarks' : 'Add to bookmarks'}
              style={{ minHeight: '36px', minWidth: '36px' }}
            >
              {isBookmarking ? (
                <svg className="w-4 h-4 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
              ) : (
                <svg 
                  className="w-4 h-4" 
                  fill={isJobBookmarked(job.id) ? 'currentColor' : 'none'} 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 5a2 2 0 012-2h10a2 2 0 012 2v16l-7-3.5L5 21V5z" />
                </svg>
              )}
            </button>

            {/* Share button */}
            <button
              onClick={handleShareClick}
              className="p-2 rounded-full text-gray-400 hover:text-gray-600 hover:bg-gray-100 transition-colors duration-200 touch-manipulation"
              aria-label="Share job"
              style={{ minHeight: '36px', minWidth: '36px' }}
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
              </svg>
            </button>

            {/* Share menu dropdown */}
            {showShareMenu && (
              <div className="absolute top-full right-0 mt-1 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-10">
                <div className="py-1">
                  <button
                    onClick={() => handleShareOption('copy')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy link
                  </button>
                  <button
                    onClick={() => handleShareOption('email')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Share via email
                  </button>
                  <button
                    onClick={() => handleShareOption('linkedin')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                    Share on LinkedIn
                  </button>
                  <button
                    onClick={() => handleShareOption('twitter')}
                    className="w-full px-4 py-2 text-left text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-3"
                  >
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                    Share on Twitter
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Company logo placeholder */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0">
          {companyLogo ? (
            <img
              src={companyLogo}
              alt={`${companyName} logo`}
              className="w-full h-full object-cover rounded-lg"
            />
          ) : (
            <span className="text-gray-500 text-sm font-medium">
              {companyName.charAt(0).toUpperCase()}
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
            {companyName}
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
        {job.categories?.slice(0, 2).map((category) => (
          <span
            key={category.id}
            className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800"
          >
            {category.name}
          </span>
        )) || []}
        {(job.categories?.length || 0) > 2 && (
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
            +{(job.categories?.length || 0) - 2} more
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