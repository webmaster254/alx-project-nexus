import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useJob } from '../contexts/JobContext';
import { useFilter } from '../contexts/FilterContext';
import { useUrlFilters } from '../hooks/useUrlFilters';
import JobCard from '../components/job/JobCard';
import JobCardSkeleton from '../components/job/JobCardSkeleton';
import EmptyState from '../components/common/EmptyState';
import { SearchBar, FilterDrawer } from '../components/filter';
import type { Job } from '../types';

const JobListingPage: React.FC = () => {
  const navigate = useNavigate();
  const { state: jobState, fetchJobs } = useJob();
  const { state: filterState, clearFilters } = useFilter();
  
  // Initialize URL filters synchronization
  useUrlFilters();

  const {
    jobs,
    isLoading,
    error,
    totalCount,
    currentPage,
    hasNextPage
  } = jobState;

  // Load jobs when component mounts or filters change
  useEffect(() => {
    const loadJobs = async () => {
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
        console.error('Failed to load jobs:', err);
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
    fetchJobs
  ]);

  const handleJobClick = (job: Job) => {
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

  const renderSkeletons = () => {
    return Array.from({ length: 6 }, (_, index) => (
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
            actionText="Clear all filters"
            onAction={clearFilters}
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
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Job Opportunities
        </h1>
        {!isLoading && totalCount > 0 && (
          <p className="text-gray-600">
            {totalCount.toLocaleString()} {totalCount === 1 ? 'job' : 'jobs'} found
          </p>
        )}
      </div>

      {/* Search Bar */}
      <div className="mb-6">
        <SearchBar />
      </div>

      {/* Main Content Layout */}
      <div className="lg:grid lg:grid-cols-4 lg:gap-8">
        {/* Filter Sidebar - Desktop */}
        <div className="lg:col-span-1">
          <FilterDrawer />
        </div>

        {/* Job Listings */}
        <div className="lg:col-span-3">
          {/* Job Grid - Responsive: 3 columns desktop, 2 tablet, 1 mobile */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
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
          </div>

          {/* Load More Button */}
          {hasNextPage && jobs.length > 0 && (
            <div className="text-center">
              <button
                onClick={handleLoadMore}
                disabled={isLoading}
                className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200"
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
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mt-6">
              {renderSkeletons()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobListingPage;