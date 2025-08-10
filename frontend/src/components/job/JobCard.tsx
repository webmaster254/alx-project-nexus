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
      className={`group relative bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-500 cursor-pointer border border-gray-100 hover:border-blue-200 touch-manipulation tap-highlight-none select-none transform hover:-translate-y-2 overflow-hidden ${
        isMobile ? 'p-5' : 'p-6'
      }`}
      onClick={handleClick}
      onKeyDown={handleKeyDown}
      tabIndex={0}
      role="button"
      aria-label={`View details for ${job.title} at ${companyName}`}
      style={{ minHeight: isMobile ? '140px' : '280px' }}
    >
      {/* Gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-indigo-50/30 to-purple-50/50 opacity-0 group-hover:opacity-100 transition-opacity duration-500 rounded-3xl"></div>
      
      {/* Content wrapper with relative positioning */}
      <div className="relative z-10 h-full flex flex-col">
        {/* Header with badges and actions */}
        <div className="flex justify-between items-start mb-4">
          <div className="flex flex-wrap gap-2">
            {job.is_new && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-green-400 to-emerald-500 text-white shadow-md">
                ✨ New
              </span>
            )}
            {job.is_featured && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-blue-500 to-indigo-500 text-white shadow-md">
                🌟 Featured
              </span>
            )}
            {job.is_urgent && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-red-500 to-pink-500 text-white shadow-md animate-pulse">
                🔥 Urgent
              </span>
            )}
            {job.is_remote && (
              <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-gradient-to-r from-purple-500 to-violet-500 text-white shadow-md">
                🏠 Remote
              </span>
            )}
          </div>

          {/* Action buttons */}
          {showActions && (
            <div className="flex items-center gap-2 relative">
              {/* Bookmark button */}
              <button
                onClick={handleBookmarkClick}
                disabled={isBookmarking}
                className={`p-2.5 rounded-xl transition-all duration-300 touch-manipulation shadow-md hover:shadow-lg transform hover:scale-110 ${
                  isJobBookmarked(job.id)
                    ? 'bg-gradient-to-r from-red-500 to-pink-500 text-white hover:from-red-600 hover:to-pink-600'
                    : 'bg-white/80 backdrop-blur-sm text-gray-500 hover:text-gray-700 border border-gray-200 hover:border-gray-300'
                } ${isBookmarking ? 'opacity-50 cursor-not-allowed' : ''}`}
                aria-label={isJobBookmarked(job.id) ? 'Remove from bookmarks' : 'Add to bookmarks'}
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
                className="p-2.5 rounded-xl bg-white/80 backdrop-blur-sm text-gray-500 hover:text-blue-600 border border-gray-200 hover:border-blue-300 transition-all duration-300 touch-manipulation shadow-md hover:shadow-lg transform hover:scale-110"
                aria-label="Share job"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                </svg>
              </button>

              {/* Share menu dropdown */}
              {showShareMenu && (
                <div className="absolute top-full right-0 mt-2 w-52 bg-white/95 backdrop-blur-lg border border-gray-200 rounded-2xl shadow-2xl z-20 overflow-hidden">
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

        {/* Company logo and job info */}
        <div className="flex items-start gap-4 mb-5 flex-1">
          <div className="w-14 h-14 bg-gradient-to-br from-gray-100 to-gray-200 rounded-2xl flex items-center justify-center flex-shrink-0 shadow-md group-hover:scale-105 transition-transform duration-300">
            {companyLogo ? (
              <img
                src={companyLogo}
                alt={`${companyName} logo`}
                className="w-full h-full object-cover rounded-2xl"
              />
            ) : (
              <span className="text-gray-600 text-lg font-bold">
                {companyName.charAt(0).toUpperCase()}
              </span>
            )}
          </div>
          
          <div className="flex-1 min-w-0">
            {/* Job title */}
            <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors duration-300">
              {job.title}
            </h3>
            
            {/* Company name */}
            <p className="text-sm font-medium text-gray-600 mb-3 flex items-center gap-2">
              <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
              {companyName}
            </p>
          </div>
        </div>

        {/* Job details grid */}
        <div className="space-y-3 mb-5 flex-1">
          {/* Location */}
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-blue-200 transition-colors duration-300">
              <svg className="w-4 h-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <span className="font-medium">{job.location}</span>
          </div>

          {/* Salary */}
          {formatSalary(job) && (
            <div className="flex items-center text-sm text-gray-600">
              <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-green-200 transition-colors duration-300">
                <svg className="w-4 h-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                </svg>
              </div>
              <span className="font-medium">{formatSalary(job)}</span>
            </div>
          )}

          {/* Experience level */}
          <div className="flex items-center text-sm text-gray-600">
            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center mr-3 group-hover:bg-purple-200 transition-colors duration-300">
              <svg className="w-4 h-4 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span className="font-medium">{getExperienceLevelDisplay(job.experience_level)}</span>
          </div>

          {/* Application deadline */}
          {job.application_deadline && (() => {
            const deadlineDate = new Date(job.application_deadline);
            const today = new Date();
            const timeDiff = deadlineDate.getTime() - today.getTime();
            const daysDiff = Math.ceil(timeDiff / (1000 * 3600 * 24));
            const isUrgent = daysDiff <= 7 && daysDiff >= 0;
            const isExpired = daysDiff < 0;
            
            return (
              <div className={`flex items-center text-sm ${isExpired ? 'text-red-700' : isUrgent ? 'text-orange-600' : 'text-gray-600'}`}>
                <div className={`w-8 h-8 rounded-lg flex items-center justify-center mr-3 group-hover:opacity-80 transition-colors duration-300 ${
                  isExpired ? 'bg-red-100 group-hover:bg-red-200' :
                  isUrgent ? 'bg-orange-100 group-hover:bg-orange-200' : 
                  'bg-blue-100 group-hover:bg-blue-200'
                }`}>
                  <svg className={`w-4 h-4 ${
                    isExpired ? 'text-red-600' :
                    isUrgent ? 'text-orange-600' : 
                    'text-blue-600'
                  }`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3a2 2 0 012-2h4a2 2 0 012 2v4m-6 8V9a1 1 0 011-1h2a1 1 0 011 1v8a1 1 0 01-1 1H9a1 1 0 01-1-1z" />
                  </svg>
                </div>
                <span className="font-medium">
                  {isExpired ? 'Expired: ' : 'Deadline: '}
                  {deadlineDate.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                  })}
                  {isUrgent && !isExpired && (
                    <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                      {daysDiff === 0 ? 'Today!' : daysDiff === 1 ? 'Tomorrow!' : `${daysDiff} days left`}
                    </span>
                  )}
                </span>
              </div>
            );
          })()}
        </div>

        {/* Categories */}
        {job.categories && job.categories.length > 0 && (
          <div className="flex flex-wrap gap-2 mb-4">
            {job.categories?.slice(0, 2).map((category) => (
              <span
                key={category.id}
                className="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-semibold bg-gradient-to-r from-indigo-100 to-purple-100 text-indigo-700 border border-indigo-200/50"
              >
                {category.name}
              </span>
            )) || []}
            {(job.categories?.length || 0) > 2 && (
              <span className="inline-flex items-center px-3 py-1.5 rounded-xl text-xs font-semibold bg-gray-100 text-gray-600 border border-gray-200">
                +{(job.categories?.length || 0) - 2} more
              </span>
            )}
          </div>
        )}

        {/* Footer with posted date and application count */}
        <div className="flex justify-between items-center pt-4 border-t border-gray-100/80 mt-auto">
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span className="font-medium">{job.days_since_posted}</span>
          </div>
          <div className="flex items-center gap-2 text-xs text-gray-500">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span className="font-medium">{job.applications_count} applications</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobCard;