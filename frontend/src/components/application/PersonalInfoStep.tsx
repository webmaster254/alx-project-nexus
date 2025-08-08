import React, { useState, useEffect } from 'react';
import { Job } from '../../types';
import { useUser } from '../../contexts/UserContext';
import { ApplicationFormData } from './ApplicationForm';

interface PersonalInfoStepProps {
  job: Job;
  formData: ApplicationFormData;
  updateFormData: (updates: Partial<ApplicationFormData>) => void;
  onNext: () => void;
  onCancel: () => void;
}

const PersonalInfoStep: React.FC<PersonalInfoStepProps> = ({
  job,
  formData,
  updateFormData,
  onNext,
  onCancel
}) => {
  const { state: userState } = useUser();
  const [coverLetter, setCoverLetter] = useState(formData.coverLetter);
  const [errors, setErrors] = useState<Record<string, string>>({});

  useEffect(() => {
    updateFormData({ coverLetter });
  }, [coverLetter, updateFormData]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!coverLetter.trim()) {
      newErrors.coverLetter = 'Cover letter is required';
    } else if (coverLetter.trim().length < 50) {
      newErrors.coverLetter = 'Cover letter must be at least 50 characters long';
    } else if (coverLetter.trim().length > 2000) {
      newErrors.coverLetter = 'Cover letter must be less than 2000 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateForm()) {
      onNext();
    }
  };

  const handleCoverLetterChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setCoverLetter(value);
    
    // Clear error when user starts typing
    if (errors.coverLetter && value.trim()) {
      setErrors(prev => ({ ...prev, coverLetter: '' }));
    }
  };

  if (!userState.isAuthenticated) {
    return (
      <div className="p-6">
        <div className="text-center py-8">
          <div className="w-16 h-16 mx-auto mb-4 bg-yellow-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">Login Required</h3>
          <p className="text-gray-600 mb-6">
            You need to be logged in to apply for jobs. Please log in or create an account to continue.
          </p>
          <div className="flex gap-3 justify-center">
            <button
              onClick={onCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Cancel
            </button>
            <button
              onClick={() => {
                // Navigate to login page
                window.location.href = '/auth?mode=login';
              }}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
            >
              Log In
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* User Information Display */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Your Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Name:</span>
              <span className="ml-2 text-gray-900">
                {userState.user?.first_name} {userState.user?.last_name}
              </span>
            </div>
            <div>
              <span className="text-gray-500">Email:</span>
              <span className="ml-2 text-gray-900">{userState.user?.email}</span>
            </div>
            {userState.user?.profile?.phone && (
              <div>
                <span className="text-gray-500">Phone:</span>
                <span className="ml-2 text-gray-900">{userState.user.profile.phone}</span>
              </div>
            )}
            {userState.user?.profile?.location && (
              <div>
                <span className="text-gray-500">Location:</span>
                <span className="ml-2 text-gray-900">{userState.user.profile.location}</span>
              </div>
            )}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            You can update your profile information in your account settings.
          </p>
        </div>

        {/* Cover Letter */}
        <div>
          <label htmlFor="coverLetter" className="block text-sm font-medium text-gray-700 mb-2">
            Cover Letter *
          </label>
          <textarea
            id="coverLetter"
            name="coverLetter"
            rows={8}
            value={coverLetter}
            onChange={handleCoverLetterChange}
            className={`w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
              errors.coverLetter ? 'border-red-300' : 'border-gray-300'
            }`}
            placeholder={`Dear ${job.company.name} Hiring Team,

I am writing to express my interest in the ${job.title} position. I believe my skills and experience make me a strong candidate for this role...`}
            aria-describedby={errors.coverLetter ? 'coverLetter-error' : 'coverLetter-help'}
          />
          {errors.coverLetter && (
            <p id="coverLetter-error" className="mt-1 text-sm text-red-600" role="alert">
              {errors.coverLetter}
            </p>
          )}
          {!errors.coverLetter && (
            <p id="coverLetter-help" className="mt-1 text-sm text-gray-500">
              {coverLetter.length}/2000 characters • Minimum 50 characters required
            </p>
          )}
        </div>

        {/* Job Information Reminder */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Applying for:</h4>
          <div className="text-sm text-blue-800">
            <p className="font-medium">{job.title}</p>
            <p>{job.company.name} • {job.location}</p>
            {job.salary_display && (
              <p className="mt-1">{job.salary_display}</p>
            )}
          </div>
        </div>
      </div>

      {/* Actions */}
      <div className="flex justify-between pt-6 mt-6 border-t border-gray-200">
        <button
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Cancel
        </button>
        <button
          onClick={handleNext}
          className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          Next: Upload Documents
        </button>
      </div>
    </div>
  );
};

export default PersonalInfoStep;