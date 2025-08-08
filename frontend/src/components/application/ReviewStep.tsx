import React from 'react';
import { Job } from '../../types';
import { useUser } from '../../contexts/UserContext';
import { ApplicationFormData } from './ApplicationForm';

interface ReviewStepProps {
  job: Job;
  formData: ApplicationFormData;
  onSubmit: () => void;
  onBack: () => void;
  isSubmitting: boolean;
  submitError: string | null;
}

const ReviewStep: React.FC<ReviewStepProps> = ({
  job,
  formData,
  onSubmit,
  onBack,
  isSubmitting,
  submitError
}) => {
  const { state: userState } = useUser();

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getDocumentTypeLabel = (type: string) => {
    switch (type) {
      case 'resume':
        return 'Resume/CV';
      case 'cover_letter':
        return 'Cover Letter';
      case 'portfolio':
        return 'Portfolio';
      default:
        return type;
    }
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        <div className="text-sm text-gray-600">
          <p>Please review your application details before submitting. Once submitted, you cannot make changes.</p>
        </div>

        {/* Job Information */}
        <div className="bg-blue-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-3">Position Details</h4>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-blue-700">Job Title:</span>
              <span className="text-blue-900 font-medium">{job.title}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Company:</span>
              <span className="text-blue-900 font-medium">{job.company.name}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-blue-700">Location:</span>
              <span className="text-blue-900 font-medium">{job.location}</span>
            </div>
            {job.salary_display && (
              <div className="flex justify-between">
                <span className="text-blue-700">Salary:</span>
                <span className="text-blue-900 font-medium">{job.salary_display}</span>
              </div>
            )}
          </div>
        </div>

        {/* Personal Information */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Your Information</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Name:</span>
              <span className="text-gray-900 font-medium">
                {userState.user?.first_name} {userState.user?.last_name}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Email:</span>
              <span className="text-gray-900 font-medium">{userState.user?.email}</span>
            </div>
            {userState.user?.profile?.phone && (
              <div className="flex justify-between">
                <span className="text-gray-600">Phone:</span>
                <span className="text-gray-900 font-medium">{userState.user.profile.phone}</span>
              </div>
            )}
            {userState.user?.profile?.location && (
              <div className="flex justify-between">
                <span className="text-gray-600">Location:</span>
                <span className="text-gray-900 font-medium">{userState.user.profile.location}</span>
              </div>
            )}
          </div>
        </div>

        {/* Cover Letter */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Cover Letter</h4>
          <div className="text-sm text-gray-700 whitespace-pre-wrap bg-gray-50 p-3 rounded border max-h-40 overflow-y-auto">
            {formData.coverLetter}
          </div>
          <p className="text-xs text-gray-500 mt-2">
            {formData.coverLetter.length} characters
          </p>
        </div>

        {/* Documents */}
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Uploaded Documents</h4>
          {formData.documents.length > 0 ? (
            <div className="space-y-3">
              {formData.documents.map((doc, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded border">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0">
                      <svg className="h-6 w-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                      </svg>
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{doc.title}</p>
                      <p className="text-xs text-gray-500">
                        {getDocumentTypeLabel(doc.document_type)} • {formatFileSize(doc.file.size)}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Ready
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No documents uploaded</p>
          )}
        </div>

        {/* Terms and Conditions */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg className="h-5 w-5 text-yellow-400" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h4 className="text-sm font-medium text-yellow-800">Before You Submit</h4>
              <div className="mt-1 text-sm text-yellow-700">
                <ul className="list-disc list-inside space-y-1">
                  <li>Your application will be sent directly to {job.company.name}</li>
                  <li>You cannot edit your application after submission</li>
                  <li>The employer will contact you directly if interested</li>
                  <li>You can track your application status in your profile</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {submitError && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-red-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
              </div>
              <div className="ml-3">
                <h4 className="text-sm font-medium text-red-800">Submission Error</h4>
                <p className="mt-1 text-sm text-red-700">{submitError}</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex justify-between pt-6 mt-6 border-t border-gray-200">
        <button
          onClick={onBack}
          disabled={isSubmitting}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Back
        </button>
        <button
          onClick={onSubmit}
          disabled={isSubmitting}
          className="px-6 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
        >
          {isSubmitting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Submitting...
            </>
          ) : (
            'Submit Application'
          )}
        </button>
      </div>
    </div>
  );
};

export default ReviewStep;