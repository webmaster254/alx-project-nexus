import React, { useEffect, useState, Suspense } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useJob } from '../contexts/JobContext';
import { jobService } from '../services/jobService';
import { Job } from '../types';
import { Breadcrumb, LoadingSpinner } from '../components/common';

// Lazy load the ApplicationForm component
const ApplicationForm = React.lazy(() => import('../components/application/ApplicationForm'));


const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { state, setCurrentJob, setSimilarJobs, setError } = useJob();
  const [job, setJob] = useState<Job | null>(null);
  const [isLoadingJob, setIsLoadingJob] = useState(true);
  const [jobError, setJobError] = useState<string | null>(null);
  const [showApplicationForm, setShowApplicationForm] = useState(false);

  useEffect(() => {
    const fetchJobDetails = async () => {
      if (!id) {
        setJobError('Job ID is required');
        setIsLoadingJob(false);
        return;
      }

      try {
        setIsLoadingJob(true);
        setJobError(null);
        
        // Fetch job details
        const jobData = await jobService.getJob(parseInt(id));
        setJob(jobData);
        setCurrentJob(jobData);

        // Fetch similar jobs
        try {
          const similarJobs = await jobService.getSimilarJobs(parseInt(id));
          setSimilarJobs(similarJobs);
        } catch (error) {
          // Don't fail the whole page if similar jobs fail
          console.warn('Failed to fetch similar jobs:', error);
        }
      } catch (error) {
        const errorMessage = error instanceof Error ? error.message : 'Failed to fetch job details';
        setJobError(errorMessage);
        setError(errorMessage);
      } finally {
        setIsLoadingJob(false);
      }
    };

    fetchJobDetails();
  }, [id, setCurrentJob, setSimilarJobs, setError]);

  const formatSalary = (job: Job) => {
    if (job.salary_min && job.salary_max) {
      return `${job.salary_currency}${job.salary_min.toLocaleString()} - ${job.salary_currency}${job.salary_max.toLocaleString()} ${job.salary_type}`;
    } else if (job.salary_min) {
      return `${job.salary_currency}${job.salary_min.toLocaleString()}+ ${job.salary_type}`;
    }
    return 'Salary not specified';
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

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const handleSimilarJobClick = (similarJob: Job) => {
    navigate(`/jobs/${similarJob.id}`);
  };

  const handleApplyClick = () => {
    setShowApplicationForm(true);
  };

  const handleCloseApplicationForm = () => {
    setShowApplicationForm(false);
  };

  const handleApplicationSuccess = () => {
    // Optionally refresh job data to update application count
    // For now, just close the form - the success step will handle this
  };

  if (isLoadingJob) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Breadcrumb skeleton */}
        <div className="bg-white border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="h-4 bg-gray-200 rounded w-64 animate-pulse"></div>
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="max-w-4xl mx-auto">
            {/* Header skeleton */}
            <div className="bg-white rounded-lg shadow-sm p-8 mb-8">
              <div className="flex items-start gap-6 mb-6">
                <div className="w-16 h-16 bg-gray-200 rounded-lg animate-pulse"></div>
                <div className="flex-1">
                  <div className="h-8 bg-gray-200 rounded w-3/4 mb-2 animate-pulse"></div>
                  <div className="h-6 bg-gray-200 rounded w-1/2 mb-4 animate-pulse"></div>
                  <div className="flex gap-2">
                    <div className="h-6 bg-gray-200 rounded w-20 animate-pulse"></div>
                    <div className="h-6 bg-gray-200 rounded w-16 animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* Content skeleton */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg shadow-sm p-8">
                  <div className="h-6 bg-gray-200 rounded w-1/3 mb-4 animate-pulse"></div>
                  <div className="space-y-2">
                    <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded w-3/4 animate-pulse"></div>
                  </div>
                </div>
              </div>
              <div>
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <div className="h-6 bg-gray-200 rounded w-1/2 mb-4 animate-pulse"></div>
                  <div className="space-y-3">
                    <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                    <div className="h-4 bg-gray-200 rounded animate-pulse"></div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (jobError || !job) {
    return (
      <div className="min-h-screen bg-gray-50">
        {/* Breadcrumb */}
        <div className="bg-white border-b">
          <div className="container mx-auto px-4 py-4">
            <Breadcrumb
              items={[
                { label: 'Jobs', href: '/' },
                { label: 'Job Details', current: true }
              ]}
            />
          </div>
        </div>

        <div className="container mx-auto px-4 py-8">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-white rounded-lg shadow-sm p-8">
              <div className="w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">Job Not Found</h1>
              <p className="text-gray-600 mb-6">
                {jobError || 'The job you are looking for could not be found.'}
              </p>
              <Link
                to="/"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Back to Jobs
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Breadcrumb Navigation */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3 sm:py-4">
          <Breadcrumb
            items={[
              { label: 'Jobs', href: '/' },
              { label: job.title, current: true }
            ]}
          />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 sm:py-8">
        <div className="max-w-4xl mx-auto">
          {/* Job Header */}
          <div className="bg-white rounded-lg shadow-sm p-4 sm:p-6 lg:p-8 mb-6 sm:mb-8">
            <div className="flex flex-col sm:flex-row sm:items-start gap-4 sm:gap-6 mb-4 sm:mb-6">
              {/* Company Logo */}
              <div className="w-16 h-16 sm:w-16 sm:h-16 bg-gray-200 rounded-lg flex items-center justify-center flex-shrink-0 mx-auto sm:mx-0">
                {job.company.logo ? (
                  <img
                    src={job.company.logo}
                    alt={`${job.company.name} logo`}
                    className="w-full h-full object-cover rounded-lg"
                  />
                ) : (
                  <span className="text-gray-500 text-xl font-medium">
                    {job.company.name.charAt(0).toUpperCase()}
                  </span>
                )}
              </div>

              <div className="flex-1 min-w-0">
                {/* Job Title */}
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                  {job.title}
                </h1>

                {/* Company Name */}
                <p className="text-xl text-gray-600 mb-4">
                  {job.company.name}
                </p>

                {/* Badges */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {job.is_new && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
                      New
                    </span>
                  )}
                  {job.is_featured && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-800">
                      Featured
                    </span>
                  )}
                  {job.is_urgent && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800">
                      Urgent
                    </span>
                  )}
                  {job.is_remote && (
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800">
                      Remote
                    </span>
                  )}
                </div>

                {/* Key Info */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                  <div className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span>{job.location}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                    <span>{formatSalary(job)}</span>
                  </div>
                  <div className="flex items-center text-gray-600">
                    <svg className="w-5 h-5 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                    </svg>
                    <span>{getExperienceLevelDisplay(job.experience_level)}</span>
                  </div>
                </div>
              </div>

              {/* Apply Button */}
              <div className="flex-shrink-0 w-full sm:w-auto">
                {job.can_apply ? (
                  <button 
                    onClick={handleApplyClick}
                    className="w-full sm:w-auto px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 active:bg-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors touch-manipulation"
                    style={{ minHeight: '44px' }}
                  >
                    Apply Now
                  </button>
                ) : (
                  <button 
                    disabled 
                    className="w-full sm:w-auto px-6 py-3 bg-gray-300 text-gray-500 font-medium rounded-lg cursor-not-allowed"
                    style={{ minHeight: '44px' }}
                  >
                    Applications Closed
                  </button>
                )}
              </div>
            </div>

            {/* Categories */}
            <div className="flex flex-wrap gap-2">
              {job.categories.map((category) => (
                <span
                  key={category.id}
                  className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800"
                >
                  {category.name}
                </span>
              ))}
            </div>
          </div>

          {/* Main Content */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column - Job Details */}
            <div className="lg:col-span-2 space-y-8">
              {/* Job Description */}
              <div className="bg-white rounded-lg shadow-sm p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">Job Description</h2>
                <div className="prose max-w-none text-gray-700">
                  <div dangerouslySetInnerHTML={{ __html: job.description.replace(/\n/g, '<br>') }} />
                </div>
              </div>

              {/* Required Skills */}
              {job.required_skills && (
                <div className="bg-white rounded-lg shadow-sm p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Required Skills</h2>
                  <div className="prose max-w-none text-gray-700">
                    <div dangerouslySetInnerHTML={{ __html: job.required_skills.replace(/\n/g, '<br>') }} />
                  </div>
                </div>
              )}

              {/* Preferred Skills */}
              {job.preferred_skills && (
                <div className="bg-white rounded-lg shadow-sm p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-4">Preferred Skills</h2>
                  <div className="prose max-w-none text-gray-700">
                    <div dangerouslySetInnerHTML={{ __html: job.preferred_skills.replace(/\n/g, '<br>') }} />
                  </div>
                </div>
              )}
            </div>

            {/* Right Column - Job Info & Similar Jobs */}
            <div className="space-y-8">
              {/* Job Information */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Information</h3>
                <div className="space-y-4">
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Industry</dt>
                    <dd className="mt-1 text-sm text-gray-900">{job.industry.name}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Job Type</dt>
                    <dd className="mt-1 text-sm text-gray-900">{job.job_type.name}</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Posted</dt>
                    <dd className="mt-1 text-sm text-gray-900">{formatDate(job.created_at)}</dd>
                  </div>
                  {job.application_deadline && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Application Deadline</dt>
                      <dd className="mt-1 text-sm text-gray-900">{formatDate(job.application_deadline)}</dd>
                    </div>
                  )}
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Applications</dt>
                    <dd className="mt-1 text-sm text-gray-900">{job.applications_count} applications</dd>
                  </div>
                  <div>
                    <dt className="text-sm font-medium text-gray-500">Views</dt>
                    <dd className="mt-1 text-sm text-gray-900">{job.views_count} views</dd>
                  </div>
                </div>
              </div>

              {/* Company Information */}
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">About {job.company.name}</h3>
                <div className="space-y-4">
                  {job.company.description && (
                    <p className="text-sm text-gray-700">{job.company.description}</p>
                  )}
                  {job.company.website && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Website</dt>
                      <dd className="mt-1">
                        <a
                          href={job.company.website}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-sm text-blue-600 hover:text-blue-800"
                        >
                          {job.company.website}
                        </a>
                      </dd>
                    </div>
                  )}
                  {job.company.size && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Company Size</dt>
                      <dd className="mt-1 text-sm text-gray-900">{job.company.size}</dd>
                    </div>
                  )}
                  {job.company.location && (
                    <div>
                      <dt className="text-sm font-medium text-gray-500">Company Location</dt>
                      <dd className="mt-1 text-sm text-gray-900">{job.company.location}</dd>
                    </div>
                  )}
                </div>
              </div>

              {/* Similar Jobs */}
              {state.similarJobs.length > 0 && (
                <div className="bg-white rounded-lg shadow-sm p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Similar Jobs</h3>
                  <div className="space-y-4">
                    {state.similarJobs.map((similarJob) => (
                      <div key={similarJob.id} className="border border-gray-200 rounded-lg p-4 hover:border-blue-300 transition-colors">
                        <h4 className="font-medium text-gray-900 mb-1">
                          <button
                            onClick={() => handleSimilarJobClick(similarJob)}
                            className="text-left hover:text-blue-600 transition-colors"
                          >
                            {similarJob.title}
                          </button>
                        </h4>
                        <p className="text-sm text-gray-600 mb-2">{similarJob.company.name}</p>
                        <div className="flex items-center text-xs text-gray-500">
                          <span>{similarJob.location}</span>
                          <span className="mx-2">•</span>
                          <span>{getExperienceLevelDisplay(similarJob.experience_level)}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Application Form Modal */}
      {showApplicationForm && job && (
        <Suspense fallback={
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8">
              <LoadingSpinner size="lg" />
              <p className="mt-4 text-gray-600">Loading application form...</p>
            </div>
          </div>
        }>
          <ApplicationForm
            job={job}
            onClose={handleCloseApplicationForm}
            onSuccess={handleApplicationSuccess}
          />
        </Suspense>
      )}
    </div>
  );
};

export default JobDetailPage;
