import React from 'react';

const JobCardSkeleton: React.FC = () => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-200 animate-pulse">
      {/* Header with badges */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex gap-2">
          <div className="h-5 w-12 bg-gray-200 rounded-full"></div>
          <div className="h-5 w-16 bg-gray-200 rounded-full"></div>
        </div>
        <div className="h-5 w-14 bg-gray-200 rounded-full"></div>
      </div>

      {/* Company logo and job info */}
      <div className="flex items-start gap-4 mb-4">
        <div className="w-12 h-12 bg-gray-200 rounded-lg flex-shrink-0"></div>
        
        <div className="flex-1 min-w-0">
          {/* Job title */}
          <div className="h-6 bg-gray-200 rounded mb-2 w-3/4"></div>
          
          {/* Company name */}
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>
      </div>

      {/* Location */}
      <div className="flex items-center mb-3">
        <div className="w-4 h-4 bg-gray-200 rounded mr-1 flex-shrink-0"></div>
        <div className="h-4 bg-gray-200 rounded w-2/3"></div>
      </div>

      {/* Salary */}
      <div className="flex items-center mb-3">
        <div className="w-4 h-4 bg-gray-200 rounded mr-1 flex-shrink-0"></div>
        <div className="h-4 bg-gray-200 rounded w-1/2"></div>
      </div>

      {/* Experience level and categories */}
      <div className="flex flex-wrap gap-2 mb-4">
        <div className="h-6 w-20 bg-gray-200 rounded-full"></div>
        <div className="h-6 w-16 bg-gray-200 rounded-full"></div>
        <div className="h-6 w-18 bg-gray-200 rounded-full"></div>
      </div>

      {/* Footer */}
      <div className="flex justify-between items-center pt-3 border-t border-gray-100">
        <div className="h-3 w-16 bg-gray-200 rounded"></div>
        <div className="h-3 w-20 bg-gray-200 rounded"></div>
      </div>
    </div>
  );
};

export default JobCardSkeleton;