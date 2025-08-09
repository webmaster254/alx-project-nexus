import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJob } from '../contexts/JobContext';
import { useFilter } from '../contexts/FilterContext';
import { useBookmark } from '../contexts/BookmarkContext';
import { useUrlFilters, usePullToRefresh, useResponsive, useInfiniteScroll, usePerformanceTracking } from '../hooks';
import JobCard from '../components/job/JobCard';
import JobCardSkeleton from '../components/job/JobCardSkeleton';
import { EmptyState } from '../components/common/EmptyState';
import { SearchBar, FilterDrawer, SortDropdown } from '../components/filter';
import { ResponsiveContainer, ResponsiveGrid } from '../components/layout';
import { recommendationService } from '../services/recommendationService';
import type { Job, JobRecommendation, SortOption } from '../types';

const JobListingPage: React.FC = () => {
  const navigate = useNavigate();
  const { state: jobState, fetchJobs } = useJob();
  const { state: filterState, clearFilters } = useFilter();
  const { loadBookmarkedJobs } = useBookmark();
  const [sortBy, setSortBy] = useState<string>('-created_at');
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  const mainRef = useRef<HTMLElement>(null);
  const { isMobile, isTablet } = useResponsive();
  
  // Performance tracking
  const { trackInteraction, trackApiCall } = usePerformanceTracking('job-listing');

  // Sort options
  const sortOptions: SortOption[] = [
    { value: '-created_at', label: 'Most Recent', description: 'Newest jobs first' },
    { value: 'created_at', label: 'Oldest First', description: 'Oldest jobs first' },
    { value: '-applications_count', label: 'Most Popular', description: 'Most applied jobs first' },
    { value: 'title', label: 'Job Title A-Z', description: 'Alphabetical by title' },
    { value: '-title', label: 'Job Title Z-A', description: 'Reverse alphabetical by title' },
    { value: '-salary_max', label: 'Highest Salary', description: 'Highest paying jobs first' },
    { value: 'salary_min', label: 'Lowest Salary', description: 'Lowest paying jobs first' },
  ];
  
  // Initialize URL filters synchronization
  useUrlFilters();

  // Pull-to-refresh functionality for mobile
  const handleRefresh = async () => {
    try {
      await fetchJobs({
        page: 1,
        page_size: 20,
        search: filterState.searchQuery || undefined,
        category: filterState.categories.length > 0 ? filterState.categories : undefined,
        location: filterState.locations.length > 0 ? filterState.locations : undefined,
        experience_level: filterState.experienceLevels.length > 0 ? filterState.experienceLevels : undefined,
        is_remote: filterState.isRemote !== null ? filterState.isRemote : undefined,
        job_type: filterState.jobTypes.length > 0 ? filterState.jobTypes : undefined,
        salary_min: filterState.salaryRange[0] > 0 ? filterState.salaryRange[0] : undefined,
        salary_max: filterState.salaryRange[1] < 1000000 ? filterState.salaryRange[1] : undefined,
      });
    } catch (err) {
      console.error('Failed to refresh jobs:', err);
    }
  };

  const { attachPullToRefreshListeners } = usePullToRefresh(handleRefresh, 80);

  const {
    jobs,
    isLoading,
    error,
    totalCount,
    currentPage,
    hasNextPage
  } = jobState;

  // Attach pull-to-refresh listeners
  useEffect(() => {
    if (mainRef.current) {
      const cleanup = attachPullToRefreshListeners(mainRef.current);
      return cleanup;
    }
  }, [attachPullToRefreshListeners]);

  // Load bookmarked jobs on mount
  useEffect(() => {
    loadBookmarkedJobs();
  }, [loadBookmarkedJobs]);

  // Load recommendations when no filters are active
  useEffect(() => {
    const loadRecommendations = async () => {
      if (!filterState.isActive && !filterState.searchQuery) {
        try {
          const personalizedRecs = await recommendationService.getPersonalizedRecommendations({ limit: 5 });
          setRecommendations(personalizedRecs);
          setShowRecommendations(personalizedRecs.length > 0);
        } catch (error) {
          console.warn('Failed to load recommendations:', error);
        }
      } else {
        setShowRecommendations(false);
      }
    };

    loadRecommendations();
  }, [filterState.isActive, filterState.searchQuery]);

  // Load jobs when component mounts or filters/sorting change
  useEffect(() => {
    const loadJobs = async () => {
      const startTime = performance.now();
      try {
        await fetchJobs({
          page: 1,
          page_size: 20,
          search: filterState.searchQuery || undefined,
          category: filterState.categories.length > 0 ? filterState.categories : undefined,
          location: filterState.locations.length > 0 ? filterState.locations : undefined,
          experience_level: filterState.experienceLevels.length > 0 ? filterState.experienceLevels : undefined,
          is_remote: filterState.isRemote !== null ? filterState.isRemote : undefined,
          job_type: filterState.jobTypes.length > 0 ? filterState.jobTypes : undefined,
          salary_min: filterState.salaryRange[0] > 0 ? filterState.salaryRange[0] : undefined,
          salary_max: filterState.salaryRange[1] < 1000000 ? filterState.salaryRange[1] : undefined,
          ordering: sortBy,
        });
        trackApiCall('jobs-fetch', startTime);
      } catch (err) {
        console.error('Failed to load jobs:', err);
        trackApiCall('jobs-fetch-error', startTime);
      }
    };

    loadJobs();
  }, [
    filterState.searchQuery,
    filterState.categories,
    filterState.locations,
    filterState.experienceLevels,
    filterState.isRemote,
    filterState.jobTypes,
    filterState.salaryRange,
    sortBy,
    fetchJobs,
    trackApiCall
  ]);

  const handleJobClick = (job: Job) => {
    trackInteraction('job-click');
    navigate(`/jobs/${job.id}`);
  };

  const handleLoadMore = async () => {
    if (hasNextPage && !isLoading) {
      try {
        await fetchJobs({
          page: currentPage + 1,
          page_size: 20,
          search: filterState.searchQuery || undefined,
          category: filterState.categories.length > 0 ? filterState.categories : undefined,
          location: filterState.locations.length > 0 ? filterState.locations : undefined,
          experience_level: filterState.experienceLevels.length > 0 ? filterState.experienceLevels : undefined,
          is_remote: filterState.isRemote !== null ? filterState.isRemote : undefined,
          job_type: filterState.jobTypes.length > 0 ? filterState.jobTypes : undefined,
          salary_min: filterState.salaryRange[0] > 0 ? filterState.salaryRange[0] : undefined,
          salary_max: filterState.salaryRange[1] < 1000000 ? filterState.salaryRange[1] : undefined,
        }, true); // append = true for pagination
      } catch (err) {
        console.error('Failed to load more jobs:', err);
      }
    }
  };

  // Infinite scroll for mobile devices
  const { loadMoreRef } = useInfiniteScroll({
    hasNextPage,
    isLoading,
    onLoadMore: handleLoadMore,
  });

  const renderSkeletons = () => {
    // Adjust skeleton count based on screen size
    const skeletonCount = isMobile ? 3 : isTablet ? 4 : 6;
    return Array.from({ length: skeletonCount }, (_, index) => (
      <JobCardSkeleton key={`skeleton-${index}`} />
    ));
  };

  const renderEmptyState = () => {
    const hasActiveFilters = 
      filterState.searchQuery ||
      filterState.categories.length > 0 ||
      filterState.locations.length > 0 ||
      filterState.experienceLevels.length > 0 ||
      filterState.isRemote !== null ||
      filterState.jobTypes.length > 0 ||
      filterState.salaryRange[0] > 0 ||
      filterState.salaryRange[1] < 1000000;

    if (hasActiveFilters) {
      return (
        <div className="col-span-full">
          <EmptyState
            title="No jobs found"
            description="We couldn't find any jobs matching your current filters. Try adjusting your search criteria or clearing some filters."
            action={{
              label: "Clear all filters",
              onClick: clearFilters
            }}
            icon={
              <svg
                className="w-16 h-16 text-gray-300"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            }
          />
        </div>
      );
    }

    return (
      <div className="col-span-full">
        <EmptyState
          title="No jobs available"
          description="There are currently no job postings available. Please check back later for new opportunities."
          icon={
            <svg
              className="w-16 h-16 text-gray-300"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1}
                d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6.5M16 6H8m0 0v-.5A2.5 2.5 0 0110.5 3h3A2.5 2.5 0 0116 5.5V6H8z"
              />
            </svg>
          }
        />
      </div>
    );
  };

  if (error) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                Error loading jobs
              </h3>
              <div className="mt-2 text-sm text-red-700">
                <p>{error}</p>
              </div>
              <div className="mt-4">
                <button
                  onClick={() => window.location.reload()}
                  className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Try again
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <main ref={mainRef} className="min-h-screen bg-gray-50">
      <ResponsiveContainer maxWidth="7xl" padding="md" mobilePadding="sm">
        {/* Pull-to-refresh indicator for mobile */}
        {isMobile && (
          <div 
            id="pull-to-refresh-indicator" 
            className="fixed top-16 left-1/2 transform -translate-x-1/2 z-30 opacity-0 transition-all duration-200"
            aria-hidden="true"
          >
            <div className="bg-white rounded-full p-2 shadow-lg">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
            </div>
          </div>
        )}

        {/* Header */}
        <div className="mb-6 sm:mb-8">
          <h1 className="text-responsive-2xl font-bold text-gray-900 mb-2">
            Job Opportunities
          </h1>
          {!isLoading && totalCount > 0 && (
            <p className="text-responsive-sm text-gray-600">
              {totalCount.toLocaleString()} {totalCount === 1 ? 'job' : 'jobs'} found
            </p>
          )}
        </div>

        {/* Search Bar */}
        <div className="mb-4 sm:mb-6">
          <SearchBar />
        </div>

        {/* Recommendations Section */}
        {showRecommendations && recommendations.length > 0 && (
          <div className="mb-6 sm:mb-8">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 sm:p-6 border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 flex items-center">
                  <svg className="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                  Recommended for You
                </h2>
                <button
                  onClick={() => setShowRecommendations(false)}
                  className="text-gray-400 hover:text-gray-600 p-1"
                  aria-label="Hide recommendations"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {recommendations.slice(0, 3).map((rec) => (
                  <JobCard
                    key={`rec-${rec.job.id}`}
                    job={rec.job}
                    onClick={() => handleJobClick(rec.job)}
                    showActions={false}
                  />
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Main Content Layout */}
        <div className="lg:grid lg:grid-cols-4 lg:gap-8">
          {/* Filter Sidebar - Desktop */}
          <div className="lg:col-span-1">
            <FilterDrawer />
          </div>

          {/* Job Listings */}
          <div className="lg:col-span-3">
            {/* Controls Bar */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-4 gap-4">
              <div className="flex items-center text-sm text-gray-600">
                {!isLoading && jobs.length > 0 && (
                  <span>
                    Showing {jobs.length} of {totalCount.toLocaleString()} jobs
                  </span>
                )}
              </div>
              
              {/* Sort Dropdown */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 hidden sm:inline">Sort by:</span>
                <SortDropdown
                  options={sortOptions}
                  value={sortBy}
                  onChange={setSortBy}
                  className="w-full sm:w-48"
                />
              </div>
            </div>
            {/* Job Grid - Enhanced Responsive Grid */}
            <ResponsiveGrid
              columns={{ xs: 1, sm: 2, lg: 3 }}
              gap="md"
              mobileGap="sm"
              className="mb-6 sm:mb-8"
            >
              {isLoading && jobs.length === 0 ? (
                renderSkeletons()
              ) : jobs.length > 0 ? (
                jobs.map((job) => (
                  <JobCard
                    key={job.id}
                    job={job}
                    onClick={() => handleJobClick(job)}
                  />
                ))
              ) : (
                renderEmptyState()
              )}
            </ResponsiveGrid>

          {/* Load More Button */}
          {hasNextPage && jobs.length > 0 && (
            <div className="text-center px-4">
              <button
                onClick={handleLoadMore}
                disabled={isLoading}
                className="inline-flex items-center justify-center w-full sm:w-auto px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 touch-manipulation"
                style={{ minHeight: '44px' }}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Loading...
                  </>
                ) : (
                  'Load More Jobs'
                )}
              </button>
            </div>
          )}

          {/* Loading more indicator */}
          {isLoading && jobs.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 mt-6">
              {renderSkeletons()}
            </div>
          )}

          {/* Infinite scroll trigger - invisible element for mobile */}
          {hasNextPage && jobs.length > 0 && isMobile && (
            <div ref={loadMoreRef} className="h-4 w-full" aria-hidden="true" />
          )}
        </div>
      </div>
      </ResponsiveContainer>
    </main>
  );
};

export default JobListingPage;