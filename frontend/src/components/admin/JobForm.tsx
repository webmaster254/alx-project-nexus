import React, { useState, useEffect } from 'react';
import { X, Save, Plus, Minus, AlertCircle, CheckCircle } from 'lucide-react';
import { adminService, companyService, categoryService } from '../../services';
import type { AdminJobData, AdminJob } from '../../services/adminService';
import type { Company } from '../../services/companyService';
import type { Industry, JobType } from '../../services/categoryService';

interface JobFormProps {
  job?: AdminJob; // If editing existing job
  onClose: () => void;
  onSuccess: (job: AdminJob) => void;
}

const JobForm: React.FC<JobFormProps> = ({ job, onClose, onSuccess }) => {
  const isEditing = !!job;
  
  const [formData, setFormData] = useState<AdminJobData>({
    title: '',
    description: '',
    company_id: 0,
    category_ids: [],
    industry_id: undefined,
    job_type_id: 0,
    location: '',
    is_remote: false,
    experience_level: 'mid',
    salary_min: undefined,
    salary_max: undefined,
    salary_currency: 'USD',
    salary_type: 'annually',
    requirements: [''],
    responsibilities: [''],
    benefits: [],
    skills_required: [],
    application_deadline: undefined,
    is_featured: false,
    is_urgent: false,
    is_active: true
  });

  // Data for dropdowns
  const [companies, setCompanies] = useState<Company[]>([]);
  const [categories, setCategories] = useState<any[]>([]);
  const [industries, setIndustries] = useState<Industry[]>([]);
  const [jobTypes, setJobTypes] = useState<JobType[]>([]);

  // State management
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  // Load form data on mount
  useEffect(() => {
    loadFormData();
  }, []);

  // Populate form if editing
  useEffect(() => {
    if (isEditing && job) {
      setFormData({
        title: job.title,
        description: job.description,
        company_id: job.company.id,
        category_ids: job.categories.map(cat => cat.id),
        industry_id: job.industry?.id,
        job_type_id: job.job_type.id,
        location: job.location,
        is_remote: job.is_remote,
        experience_level: job.experience_level as any,
        salary_min: job.salary_min,
        salary_max: job.salary_max,
        salary_currency: job.salary_currency,
        salary_type: job.salary_type as any,
        requirements: job.requirements.length > 0 ? job.requirements : [''],
        responsibilities: job.responsibilities.length > 0 ? job.responsibilities : [''],
        benefits: job.benefits || [],
        skills_required: job.skills_required || [],
        application_deadline: job.application_deadline,
        is_featured: job.is_featured,
        is_urgent: job.is_urgent,
        is_active: job.is_active
      });
    }
  }, [isEditing, job]);

  const loadFormData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [companiesData, categoriesData, industriesData, jobTypesData] = await Promise.all([
        companyService.getAllCompanies(),
        categoryService.getAllCategories(),
        categoryService.getAllIndustries(),
        categoryService.getAllJobTypes()
      ]);

      setCompanies(companiesData);
      setCategories(categoriesData);
      setIndustries(industriesData);
      setJobTypes(jobTypesData);
    } catch (error: any) {
      setError('Failed to load form data');
      console.error('Failed to load form data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    // Validation
    if (!formData.title.trim()) {
      setError('Job title is required');
      setSaving(false);
      return;
    }

    if (!formData.description.trim()) {
      setError('Job description is required');
      setSaving(false);
      return;
    }

    if (!formData.company_id) {
      setError('Please select a company');
      setSaving(false);
      return;
    }

    if (formData.category_ids.length === 0) {
      setError('Please select at least one category');
      setSaving(false);
      return;
    }

    if (!formData.job_type_id) {
      setError('Please select a job type');
      setSaving(false);
      return;
    }

    // Filter out empty requirements and responsibilities
    const cleanedData = {
      ...formData,
      requirements: formData.requirements.filter(req => req.trim() !== ''),
      responsibilities: formData.responsibilities.filter(resp => resp.trim() !== '')
    };

    try {
      let result: AdminJob;
      if (isEditing && job) {
        result = await adminService.updateJob(job.id, cleanedData);
        setSuccess('Job updated successfully!');
      } else {
        result = await adminService.createJob(cleanedData);
        setSuccess('Job created successfully!');
      }

      setTimeout(() => {
        onSuccess(result);
        onClose();
      }, 1500);
    } catch (error: any) {
      setError(error.message || `Failed to ${isEditing ? 'update' : 'create'} job`);
    } finally {
      setSaving(false);
    }
  };

  const handleArrayFieldChange = (
    field: 'requirements' | 'responsibilities' | 'benefits' | 'skills_required',
    index: number,
    value: string
  ) => {
    const newArray = [...formData[field]];
    newArray[index] = value;
    setFormData(prev => ({ ...prev, [field]: newArray }));
  };

  const addArrayField = (field: 'requirements' | 'responsibilities' | 'benefits' | 'skills_required') => {
    setFormData(prev => ({
      ...prev,
      [field]: [...prev[field], '']
    }));
  };

  const removeArrayField = (
    field: 'requirements' | 'responsibilities' | 'benefits' | 'skills_required',
    index: number
  ) => {
    if (formData[field].length > 1) {
      const newArray = formData[field].filter((_, i) => i !== index);
      setFormData(prev => ({ ...prev, [field]: newArray }));
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            <span className="ml-3 text-gray-600">Loading form data...</span>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-900">
            {isEditing ? 'Edit Job' : 'Create New Job'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-5 w-5 text-gray-400" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error/Success Messages */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center">
                <AlertCircle className="h-5 w-5 text-red-400 mr-2" />
                <span className="text-red-800">{error}</span>
              </div>
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center">
                <CheckCircle className="h-5 w-5 text-green-400 mr-2" />
                <span className="text-green-800">{success}</span>
              </div>
            </div>
          )}

          {/* Basic Information */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-2">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., Senior Software Engineer"
                required
              />
            </div>

            <div>
              <label htmlFor="company_id" className="block text-sm font-medium text-gray-700 mb-2">
                Company <span className="text-red-500">*</span>
              </label>
              <select
                id="company_id"
                value={formData.company_id}
                onChange={(e) => setFormData(prev => ({ ...prev, company_id: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value={0}>Select a company</option>
                {companies.map(company => (
                  <option key={company.id} value={company.id}>{company.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Categories and Job Type */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <label htmlFor="category_ids" className="block text-sm font-medium text-gray-700 mb-2">
                Categories <span className="text-red-500">*</span>
              </label>
              <select
                id="category_ids"
                multiple
                value={formData.category_ids.map(String)}
                onChange={(e) => {
                  const values = Array.from(e.target.selectedOptions, option => Number(option.value));
                  setFormData(prev => ({ ...prev, category_ids: values }));
                }}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                size={4}
              >
                {categories.map(category => (
                  <option key={category.id} value={category.id}>{category.name}</option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">Hold Ctrl/Cmd to select multiple</p>
            </div>

            <div>
              <label htmlFor="job_type_id" className="block text-sm font-medium text-gray-700 mb-2">
                Job Type <span className="text-red-500">*</span>
              </label>
              <select
                id="job_type_id"
                value={formData.job_type_id}
                onChange={(e) => setFormData(prev => ({ ...prev, job_type_id: Number(e.target.value) }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                required
              >
                <option value={0}>Select job type</option>
                {jobTypes.map(jobType => (
                  <option key={jobType.id} value={jobType.id}>{jobType.name}</option>
                ))}
              </select>
            </div>

            <div>
              <label htmlFor="industry_id" className="block text-sm font-medium text-gray-700 mb-2">
                Industry
              </label>
              <select
                id="industry_id"
                value={formData.industry_id || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  industry_id: e.target.value ? Number(e.target.value) : undefined 
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="">Select industry</option>
                {industries.map(industry => (
                  <option key={industry.id} value={industry.id}>{industry.name}</option>
                ))}
              </select>
            </div>
          </div>

          {/* Location and Remote */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div>
              <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">
                Location <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="location"
                value={formData.location}
                onChange={(e) => setFormData(prev => ({ ...prev, location: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="e.g., New York, NY or Remote"
                required
              />
            </div>

            <div className="flex items-center space-x-6 pt-8">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_remote}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_remote: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Remote Work</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_featured}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_featured: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Featured</span>
              </label>

              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.is_urgent}
                  onChange={(e) => setFormData(prev => ({ ...prev, is_urgent: e.target.checked }))}
                  className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">Urgent</span>
              </label>
            </div>
          </div>

          {/* Experience Level and Salary */}
          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div>
              <label htmlFor="experience_level" className="block text-sm font-medium text-gray-700 mb-2">
                Experience Level
              </label>
              <select
                id="experience_level"
                value={formData.experience_level}
                onChange={(e) => setFormData(prev => ({ ...prev, experience_level: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="entry">Entry Level</option>
                <option value="junior">Junior</option>
                <option value="mid">Mid Level</option>
                <option value="senior">Senior</option>
                <option value="lead">Lead</option>
                <option value="executive">Executive</option>
              </select>
            </div>

            <div>
              <label htmlFor="salary_min" className="block text-sm font-medium text-gray-700 mb-2">
                Min Salary
              </label>
              <input
                type="number"
                id="salary_min"
                value={formData.salary_min || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  salary_min: e.target.value ? Number(e.target.value) : undefined 
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="50000"
              />
            </div>

            <div>
              <label htmlFor="salary_max" className="block text-sm font-medium text-gray-700 mb-2">
                Max Salary
              </label>
              <input
                type="number"
                id="salary_max"
                value={formData.salary_max || ''}
                onChange={(e) => setFormData(prev => ({ 
                  ...prev, 
                  salary_max: e.target.value ? Number(e.target.value) : undefined 
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                placeholder="80000"
              />
            </div>

            <div>
              <label htmlFor="salary_type" className="block text-sm font-medium text-gray-700 mb-2">
                Salary Type
              </label>
              <select
                id="salary_type"
                value={formData.salary_type}
                onChange={(e) => setFormData(prev => ({ ...prev, salary_type: e.target.value as any }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="hourly">Hourly</option>
                <option value="monthly">Monthly</option>
                <option value="annually">Annually</option>
              </select>
            </div>
          </div>

          {/* Description */}
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
              Job Description <span className="text-red-500">*</span>
            </label>
            <textarea
              id="description"
              rows={6}
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
              placeholder="Describe the role, company culture, and what makes this position exciting..."
              required
            />
          </div>

          {/* Requirements */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Requirements <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={() => addArrayField('requirements')}
                className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                <Plus className="h-3 w-3 mr-1" />
                Add
              </button>
            </div>
            {formData.requirements.map((req, index) => (
              <div key={index} className="flex items-center space-x-2 mb-2">
                <input
                  type="text"
                  value={req}
                  onChange={(e) => handleArrayFieldChange('requirements', index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Bachelor's degree in Computer Science"
                />
                <button
                  type="button"
                  onClick={() => removeArrayField('requirements', index)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                  disabled={formData.requirements.length === 1}
                >
                  <Minus className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Responsibilities */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Responsibilities <span className="text-red-500">*</span>
              </label>
              <button
                type="button"
                onClick={() => addArrayField('responsibilities')}
                className="inline-flex items-center px-3 py-1 bg-blue-600 text-white text-sm rounded hover:bg-blue-700"
              >
                <Plus className="h-3 w-3 mr-1" />
                Add
              </button>
            </div>
            {formData.responsibilities.map((resp, index) => (
              <div key={index} className="flex items-center space-x-2 mb-2">
                <input
                  type="text"
                  value={resp}
                  onChange={(e) => handleArrayFieldChange('responsibilities', index, e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                  placeholder="e.g., Develop and maintain web applications"
                />
                <button
                  type="button"
                  onClick={() => removeArrayField('responsibilities', index)}
                  className="p-2 text-red-600 hover:bg-red-50 rounded"
                  disabled={formData.responsibilities.length === 1}
                >
                  <Minus className="h-4 w-4" />
                </button>
              </div>
            ))}
          </div>

          {/* Application Deadline */}
          <div>
            <label htmlFor="application_deadline" className="block text-sm font-medium text-gray-700 mb-2">
              Application Deadline
            </label>
            <input
              type="date"
              id="application_deadline"
              value={formData.application_deadline || ''}
              onChange={(e) => setFormData(prev => ({ 
                ...prev, 
                application_deadline: e.target.value || undefined 
              }))}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          {/* Form Actions */}
          <div className="flex items-center justify-end space-x-4 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
              disabled={saving}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={saving}
            >
              {saving ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  {isEditing ? 'Updating...' : 'Creating...'}
                </div>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {isEditing ? 'Update Job' : 'Create Job'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default JobForm;