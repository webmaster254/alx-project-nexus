import React from 'react';
import { Job } from '../../types';

interface SuccessStepProps {
  job: Job;
  onClose: () => void;
}

const SuccessStep: React.FC<SuccessStepProps> = ({ job, onClose }) => {
  const handleViewJobs = () => {
    onClose();
    // Navigate to jobs page
    window.location.href = '/';
  };

  const handleViewProfile = () => {
    onClose();
    // Navigate to profile page
    window.location.href = '/profile';
  };

  return (
    <div className="p-6">
      <div className="text-center py-8">
        {/* Success Icon */}
        <div className="w-16 h-16 mx-auto mb-6 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        </div>

        {/* Success Message */}
        <h3 className="text-2xl font-bold text-gray-900 mb-2">
          Application Submitted Successfully!
        </h3>
        <p className="text-gray-600 mb-6">
          Your application for <span className="font-medium">{job.title}</span> at{' '}
          <span className="font-medium">{job.company.name}</span> has been submitted.
        </p>

        {/* What Happens Next */}
        <div className="bg-blue-50 rounded-lg p-6 mb-8 text-left">
          <h4 className="text-lg font-semibold text-blue-900 mb-4">What happens next?</h4>
          <div className="space-y-3 text-sm text-blue-800">
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-medium text-blue-900">1</span>
              </div>
              <div>
                <p className="font-medium">Application Review</p>
                <p className="text-blue-700">The hiring team at {job.company.name} will review your application and documents.</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-medium text-blue-900">2</span>
              </div>
              <div>
                <p className="font-medium">Direct Contact</p>
                <p className="text-blue-700">If your profile matches their requirements, they'll contact you directly via email or phone.</p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-200 rounded-full flex items-center justify-center mr-3 mt-0.5">
                <span className="text-xs font-medium text-blue-900">3</span>
              </div>
              <div>
                <p className="font-medium">Track Progress</p>
                <p className="text-blue-700">You can track your application status and view all your applications in your profile.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Application Details */}
        <div className="bg-gray-50 rounded-lg p-4 mb-8 text-left">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Application Summary</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Position:</span>
              <span className="text-gray-900 font-medium">{job.title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Company:</span>
              <span className="text-gray-900 font-medium">{job.company.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Location:</span>
              <span className="text-gray-900 font-medium">{job.location}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Submitted:</span>
              <span className="text-gray-900 font-medium">
                {new Date().toLocaleDateString('en-US', {
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit'
                })}
              </span>
            </div>
          </div>
        </div>

        {/* Tips */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-8 text-left">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">Pro Tips</h4>
              <div className="mt-1 text-sm text-yellow-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Keep your email notifications enabled to hear back from employers</li>
                  <li>Continue applying to similar positions to increase your chances</li>
                  <li>Update your profile regularly to stay competitive</li>
                  <li>Follow up politely if you don't hear back within 2 weeks</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={handleViewProfile}
            className="px-6 py-2 text-sm font-medium text-blue-700 bg-blue-100 border border-blue-200 rounded-md hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            View My Applications
          </button>
          <button
            onClick={handleViewJobs}
            className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Browse More Jobs
          </button>
          <button
            onClick={onClose}
            className="px-6 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default SuccessStep;