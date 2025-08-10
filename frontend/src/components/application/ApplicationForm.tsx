import React, { useState, useCallback, useEffect } from 'react';
import { Job } from '../../types';
import { applicationService } from '../../services';
import type { CreateApplicationData } from '../../services/applicationService';
import { useUser } from '../../contexts/UserContext';
import PersonalInfoStep from './PersonalInfoStep';
import DocumentsStep from './DocumentsStep';
import ReviewStep from './ReviewStep';
import SuccessStep from './SuccessStep';

interface ApplicationFormProps {
  job: Job;
  onClose: () => void;
  onSuccess?: () => void;
}

export type ApplicationStep = 'personal' | 'documents' | 'review' | 'success';

export interface ApplicationFormData {
  coverLetter: string;
  documents: {
    document_type: 'resume' | 'cover_letter' | 'portfolio';
    title: string;
    file: File;
  }[];
}

const ApplicationForm: React.FC<ApplicationFormProps> = ({ job, onClose, onSuccess }) => {
  const { state: userState } = useUser();
  const [currentStep, setCurrentStep] = useState<ApplicationStep>('personal');
  const [formData, setFormData] = useState<ApplicationFormData>({
    coverLetter: '',
    documents: []
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  const updateFormData = useCallback((updates: Partial<ApplicationFormData>) => {
    setFormData(prev => ({ ...prev, ...updates }));
  }, []);

  // Check if user has already applied
  useEffect(() => {
    const checkApplicationStatus = async () => {
      if (userState.isAuthenticated) {
        try {
          const hasApplied = await applicationService.hasAppliedToJob(job.id);
          if (hasApplied) {
            setSubmitError('You have already applied for this position');
          }
        } catch (error) {
          console.warn('Failed to check application status:', error);
        }
      }
    };

    checkApplicationStatus();
  }, [job.id, userState.isAuthenticated]);

  const handleSubmit = useCallback(async () => {
    if (!userState.isAuthenticated) {
      setSubmitError('You must be logged in to apply for jobs');
      return;
    }

    setIsSubmitting(true);
    setSubmitError(null);

    try {
      // Check if already applied
      const hasApplied = await applicationService.hasAppliedToJob(job.id);
      if (hasApplied) {
        setSubmitError('You have already applied for this position');
        setIsSubmitting(false);
        return;
      }

      // Prepare application data for new API
      const applicationData: CreateApplicationData = {
        job_id: job.id,
        cover_letter: formData.coverLetter,
        // Note: For now, we'll use the existing document handling
        // In a full implementation, documents would be uploaded separately first
      };

      await applicationService.createApplication(applicationData);
      setCurrentStep('success');
      onSuccess?.();
    } catch (error) {
      console.error('Application submission failed:', error);
      setSubmitError(
        error instanceof Error 
          ? error.message 
          : 'Failed to submit application. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  }, [userState.isAuthenticated, job.id, formData, onSuccess]);

  const handleNext = useCallback(() => {
    switch (currentStep) {
      case 'personal':
        setCurrentStep('documents');
        break;
      case 'documents':
        setCurrentStep('review');
        break;
      case 'review':
        handleSubmit();
        break;
    }
  }, [currentStep, handleSubmit]);

  const handleBack = useCallback(() => {
    switch (currentStep) {
      case 'documents':
        setCurrentStep('personal');
        break;
      case 'review':
        setCurrentStep('documents');
        break;
    }
  }, [currentStep]);

  const getStepTitle = () => {
    switch (currentStep) {
      case 'personal':
        return 'Personal Information';
      case 'documents':
        return 'Upload Documents';
      case 'review':
        return 'Review Application';
      case 'success':
        return 'Application Submitted';
      default:
        return '';
    }
  };

  const getStepNumber = () => {
    switch (currentStep) {
      case 'personal':
        return 1;
      case 'documents':
        return 2;
      case 'review':
        return 3;
      case 'success':
        return 4;
      default:
        return 1;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-2 sm:p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[95vh] sm:max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="px-4 sm:px-6 py-3 sm:py-4 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-semibold text-gray-900">
                Apply for {job.title}
              </h2>
              <p className="text-sm text-gray-600 mt-1">
                {job.company.name} • {job.location}
              </p>
            </div>
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 active:text-gray-700 transition-colors touch-manipulation"
              aria-label="Close application form"
              style={{ minHeight: '44px', minWidth: '44px' }}
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          {/* Progress Steps */}
          {currentStep !== 'success' && (
            <div className="mt-4">
              <div className="flex items-center">
                {[1, 2, 3].map((step) => (
                  <React.Fragment key={step}>
                    <div className={`flex items-center justify-center w-8 h-8 rounded-full text-sm font-medium ${
                      step <= getStepNumber()
                        ? 'bg-blue-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                    }`}>
                      {step}
                    </div>
                    {step < 3 && (
                      <div className={`flex-1 h-1 mx-2 ${
                        step < getStepNumber() ? 'bg-blue-600' : 'bg-gray-200'
                      }`} />
                    )}
                  </React.Fragment>
                ))}
              </div>
              <div className="mt-2">
                <h3 className="text-lg font-medium text-gray-900">{getStepTitle()}</h3>
              </div>
            </div>
          )}
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto touch-manipulation">
          {currentStep === 'personal' && (
            <PersonalInfoStep
              job={job}
              formData={formData}
              updateFormData={updateFormData}
              onNext={handleNext}
              onCancel={onClose}
            />
          )}

          {currentStep === 'documents' && (
            <DocumentsStep
              formData={formData}
              updateFormData={updateFormData}
              onNext={handleNext}
              onBack={handleBack}
            />
          )}

          {currentStep === 'review' && (
            <ReviewStep
              job={job}
              formData={formData}
              onSubmit={handleNext}
              onBack={handleBack}
              isSubmitting={isSubmitting}
              submitError={submitError}
            />
          )}

          {currentStep === 'success' && (
            <SuccessStep
              job={job}
              onClose={onClose}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default ApplicationForm;