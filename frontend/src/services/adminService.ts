import { httpClient } from './index';
import type { ApiResponse, PaginatedResponse } from '../types';

// Admin-specific interfaces
export interface AdminJobData {
  title: string;
  description: string;
  company_id: number;
  category_ids: number[];
  industry_id?: number;
  job_type_id: number;
  location: string;
  is_remote: boolean;
  experience_level: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'executive';
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  salary_type: 'hourly' | 'monthly' | 'annually';
  requirements: string[];
  responsibilities: string[];
  benefits?: string[];
  skills_required?: string[];
  application_deadline?: string;
  is_featured?: boolean;
  is_urgent?: boolean;
  is_active?: boolean;
}

export interface AdminJob {
  id: number;
  title: string;
  description: string;
  company: {
    id: number;
    name: string;
    logo?: string;
  };
  categories: Array<{
    id: number;
    name: string;
  }>;
  industry?: {
    id: number;
    name: string;
  };
  job_type: {
    id: number;
    name: string;
  };
  location: string;
  is_remote: boolean;
  experience_level: string;
  salary_min?: number;
  salary_max?: number;
  salary_currency: string;
  salary_type: string;
  requirements: string[];
  responsibilities: string[];
  benefits: string[];
  skills_required: string[];
  application_deadline?: string;
  is_featured: boolean;
  is_urgent: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  applications_count: number;
  views_count: number;
}

export interface AdminCompanyData {
  name: string;
  description?: string;
  website?: string;
  industry_id?: number;
  size?: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  founded_year?: number;
  location?: string;
  logo?: File;
  is_verified?: boolean;
  is_active?: boolean;
}

export interface AdminCompany {
  id: number;
  name: string;
  description?: string;
  website?: string;
  industry?: {
    id: number;
    name: string;
  };
  size?: string;
  founded_year?: number;
  location?: string;
  logo?: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  jobs_count: number;
}

export interface DashboardStats {
  total_jobs: number;
  active_jobs: number;
  featured_jobs: number;
  total_companies: number;
  verified_companies: number;
  total_applications: number;
  pending_applications: number;
  total_users: number;
  active_users: number;
  jobs_this_month: number;
  applications_this_month: number;
}

export interface AdminFilterParams {
  search?: string;
  is_active?: boolean;
  is_featured?: boolean;
  is_verified?: boolean;
  company_id?: number;
  industry_id?: number;
  job_type_id?: number;
  category_id?: number;
  date_from?: string;
  date_to?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export class AdminService {
  private readonly baseUrl = '/jobs';
  private readonly categoriesUrl = '/categories';
  private readonly applicationsUrl = '/applications';

  // Job Management (Admin Only)
  /**
   * Get all jobs including inactive ones (admin only)
   */
  async getAllJobs(params: AdminFilterParams = {}): Promise<PaginatedResponse<AdminJob>> {
    const response: ApiResponse<PaginatedResponse<AdminJob>> = await httpClient.get(
      `${this.baseUrl}/jobs/`,
      {
        ...params,
        include_inactive: true
      },
      true,
      false // Don't cache admin data
    );
    return response.data;
  }

  /**
   * Create new job posting (admin only)
   */
  async createJob(data: AdminJobData): Promise<AdminJob> {
    const response: ApiResponse<AdminJob> = await httpClient.post(
      `${this.baseUrl}/jobs/`,
      data
    );
    return response.data;
  }

  /**
   * Update job posting (admin only)
   */
  async updateJob(id: number, data: Partial<AdminJobData>): Promise<AdminJob> {
    const response: ApiResponse<AdminJob> = await httpClient.put(
      `${this.baseUrl}/jobs/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Partially update job posting (admin only)
   */
  async patchJob(id: number, data: Partial<AdminJobData>): Promise<AdminJob> {
    const response: ApiResponse<AdminJob> = await httpClient.patch(
      `${this.baseUrl}/jobs/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete/deactivate job posting (admin only)
   */
  async deleteJob(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/jobs/${id}/`);
  }

  /**
   * Toggle job featured status (admin only)
   */
  async toggleJobFeatured(id: number): Promise<AdminJob> {
    const response: ApiResponse<AdminJob> = await httpClient.post(
      `${this.baseUrl}/jobs/${id}/toggle_featured/`
    );
    return response.data;
  }

  /**
   * Reactivate deactivated job (admin only)
   */
  async reactivateJob(id: number): Promise<AdminJob> {
    const response: ApiResponse<AdminJob> = await httpClient.post(
      `${this.baseUrl}/jobs/${id}/reactivate/`
    );
    return response.data;
  }

  // Company Management (Admin Only)
  /**
   * Get all companies (admin only)
   */
  async getAllCompanies(params: AdminFilterParams = {}): Promise<PaginatedResponse<AdminCompany>> {
    const response: ApiResponse<PaginatedResponse<AdminCompany>> = await httpClient.get(
      `${this.baseUrl}/companies/`,
      params,
      true,
      false
    );
    return response.data;
  }

  /**
   * Create new company (admin only)
   */
  async createCompany(data: AdminCompanyData): Promise<AdminCompany> {
    if (data.logo) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        const value = data[key as keyof AdminCompanyData];
        if (value !== undefined) {
          if (key === 'logo' && value instanceof File) {
            formData.append(key, value);
          } else {
            formData.append(key, String(value));
          }
        }
      });

      const response: ApiResponse<AdminCompany> = await httpClient.postFormData(
        `${this.baseUrl}/companies/`,
        formData
      );
      return response.data;
    } else {
      const { logo, ...dataWithoutLogo } = data;
      const response: ApiResponse<AdminCompany> = await httpClient.post(
        `${this.baseUrl}/companies/`,
        dataWithoutLogo
      );
      return response.data;
    }
  }

  /**
   * Update company (admin only)
   */
  async updateCompany(id: number, data: Partial<AdminCompanyData>): Promise<AdminCompany> {
    if (data.logo) {
      const formData = new FormData();
      Object.keys(data).forEach(key => {
        const value = data[key as keyof AdminCompanyData];
        if (value !== undefined) {
          if (key === 'logo' && value instanceof File) {
            formData.append(key, value);
          } else {
            formData.append(key, String(value));
          }
        }
      });

      const response: ApiResponse<AdminCompany> = await httpClient.putFormData(
        `${this.baseUrl}/companies/${id}/`,
        formData
      );
      return response.data;
    } else {
      const { logo, ...dataWithoutLogo } = data;
      const response: ApiResponse<AdminCompany> = await httpClient.put(
        `${this.baseUrl}/companies/${id}/`,
        dataWithoutLogo
      );
      return response.data;
    }
  }

  /**
   * Delete company (admin only)
   */
  async deleteCompany(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/companies/${id}/`);
  }

  // Category Management (Admin Only)
  /**
   * Create new job category (admin only)
   */
  async createCategory(data: { name: string; description?: string; parent_id?: number }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.post(
      `${this.categoriesUrl}/categories/`,
      data
    );
    return response.data;
  }

  /**
   * Update job category (admin only)
   */
  async updateCategory(id: number, data: { name?: string; description?: string; parent_id?: number }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.put(
      `${this.categoriesUrl}/categories/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete job category (admin only)
   */
  async deleteCategory(id: number): Promise<void> {
    await httpClient.delete(`${this.categoriesUrl}/categories/${id}/`);
  }

  // Industry Management (Admin Only)
  /**
   * Create new industry (admin only)
   */
  async createIndustry(data: { name: string; description?: string }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.post(
      `${this.categoriesUrl}/industries/`,
      data
    );
    return response.data;
  }

  /**
   * Update industry (admin only)
   */
  async updateIndustry(id: number, data: { name?: string; description?: string }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.put(
      `${this.categoriesUrl}/industries/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete industry (admin only)
   */
  async deleteIndustry(id: number): Promise<void> {
    await httpClient.delete(`${this.categoriesUrl}/industries/${id}/`);
  }

  // Job Type Management (Admin Only)
  /**
   * Create new job type (admin only)
   */
  async createJobType(data: { name: string; description?: string }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.post(
      `${this.categoriesUrl}/job-types/`,
      data
    );
    return response.data;
  }

  /**
   * Update job type (admin only)
   */
  async updateJobType(id: number, data: { name?: string; description?: string }): Promise<any> {
    const response: ApiResponse<any> = await httpClient.put(
      `${this.categoriesUrl}/job-types/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete job type (admin only)
   */
  async deleteJobType(id: number): Promise<void> {
    await httpClient.delete(`${this.categoriesUrl}/job-types/${id}/`);
  }

  // Dashboard & Analytics
  /**
   * Get admin dashboard statistics
   */
  async getDashboardStats(): Promise<DashboardStats> {
    try {
      // Fetch all stats in parallel
      const [
        jobsResponse,
        activeJobsResponse,
        featuredJobsResponse,
        companiesResponse,
        verifiedCompaniesResponse,
        applicationsResponse,
        pendingApplicationsResponse
      ] = await Promise.allSettled([
        this.getAllJobs({ page_size: 1 }),
        this.getAllJobs({ is_active: true, page_size: 1 }),
        this.getAllJobs({ is_featured: true, page_size: 1 }),
        this.getAllCompanies({ page_size: 1 }),
        this.getAllCompanies({ is_verified: true, page_size: 1 }),
        httpClient.get(`${this.applicationsUrl}/applications/`, { page_size: 1 }),
        httpClient.get(`${this.applicationsUrl}/applications/admin/pending/`, { page_size: 1 })
      ]);

      return {
        total_jobs: jobsResponse.status === 'fulfilled' ? jobsResponse.value.count : 0,
        active_jobs: activeJobsResponse.status === 'fulfilled' ? activeJobsResponse.value.count : 0,
        featured_jobs: featuredJobsResponse.status === 'fulfilled' ? featuredJobsResponse.value.count : 0,
        total_companies: companiesResponse.status === 'fulfilled' ? companiesResponse.value.count : 0,
        verified_companies: verifiedCompaniesResponse.status === 'fulfilled' ? verifiedCompaniesResponse.value.count : 0,
        total_applications: applicationsResponse.status === 'fulfilled' ? (applicationsResponse.value.data as any)?.count || 0 : 0,
        pending_applications: pendingApplicationsResponse.status === 'fulfilled' ? (pendingApplicationsResponse.value.data as any)?.count || 0 : 0,
        total_users: 0, // Would need user endpoint
        active_users: 0, // Would need user endpoint
        jobs_this_month: 0, // Would need date filtering
        applications_this_month: 0 // Would need date filtering
      };
    } catch (error) {
      console.warn('Failed to fetch dashboard stats:', error);
      return {
        total_jobs: 0,
        active_jobs: 0,
        featured_jobs: 0,
        total_companies: 0,
        verified_companies: 0,
        total_applications: 0,
        pending_applications: 0,
        total_users: 0,
        active_users: 0,
        jobs_this_month: 0,
        applications_this_month: 0
      };
    }
  }

  /**
   * Get recent activity for admin dashboard
   */
  async getRecentActivity(limit: number = 10): Promise<any[]> {
    try {
      // Get recent jobs, applications, etc.
      const [recentJobs, recentApplications] = await Promise.allSettled([
        this.getAllJobs({ ordering: '-created_at', page_size: limit }),
        httpClient.get(`${this.applicationsUrl}/applications/`, { 
          ordering: '-applied_at', 
          page_size: limit 
        })
      ]);

      const activities: any[] = [];

      if (recentJobs.status === 'fulfilled') {
        recentJobs.value.results.forEach(job => {
          activities.push({
            type: 'job_created',
            title: `New job posted: ${job.title}`,
            description: `${job.company.name} posted a new job`,
            timestamp: job.created_at,
            data: job
          });
        });
      }

      if (recentApplications.status === 'fulfilled') {
        ((recentApplications.value.data as any)?.results || []).forEach((app: any) => {
          activities.push({
            type: 'application_submitted',
            title: `New application for ${app.job.title}`,
            description: `${app.user.first_name} ${app.user.last_name} applied`,
            timestamp: app.applied_at,
            data: app
          });
        });
      }

      // Sort by timestamp descending
      return activities.sort((a, b) => 
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      ).slice(0, limit);
    } catch (error) {
      console.warn('Failed to fetch recent activity:', error);
      return [];
    }
  }

  /**
   * Bulk operations
   */
  async bulkUpdateJobs(jobIds: number[], data: Partial<AdminJobData>): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      jobIds.map(id => this.patchJob(id, data))
    );

    results.forEach(result => {
      if (result.status === 'fulfilled') {
        success++;
      } else {
        failed++;
      }
    });

    return { success, failed };
  }

  /**
   * Bulk delete/deactivate jobs
   */
  async bulkDeleteJobs(jobIds: number[]): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      jobIds.map(id => this.deleteJob(id))
    );

    results.forEach(result => {
      if (result.status === 'fulfilled') {
        success++;
      } else {
        failed++;
      }
    });

    return { success, failed };
  }
}

// Create and export service instance
export const adminService = new AdminService();