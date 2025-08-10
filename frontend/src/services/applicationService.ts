import { httpClient } from './index';
import type { ApiResponse, PaginatedResponse } from '../types';

export interface ApplicationStatus {
  id: number;
  name: string;
  description?: string;
  is_default?: boolean;
  created_at: string;
  updated_at: string;
}

export interface Document {
  id: number;
  user: number;
  document_type: string;
  file: string;
  file_name: string;
  file_size: number;
  uploaded_at: string;
  is_active: boolean;
}

export interface Application {
  id: number;
  job: {
    id: number;
    title: string;
    company: {
      id: number;
      name: string;
      logo?: string;
    };
    location: string;
    salary_min?: number;
    salary_max?: number;
    salary_currency: string;
    application_deadline?: string;
  };
  user: {
    id: number;
    first_name: string;
    last_name: string;
    email: string;
  };
  status: ApplicationStatus;
  cover_letter: string;
  resume?: Document;
  additional_documents?: Document[];
  applied_at: string;
  updated_at: string;
  notes?: string;
}

export interface CreateApplicationData {
  job_id: number;
  cover_letter: string;
  resume_id?: number;
  additional_document_ids?: number[];
}

export interface UpdateApplicationData {
  status_id?: number;
  notes?: string;
  cover_letter?: string;
}

export interface ApplicationFilterParams {
  status__name?: string;
  job__id?: number;
  job__company__id?: number;
  search?: string;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export interface DocumentUploadData {
  document_type: string;
  file: File;
  file_name?: string;
}

export class ApplicationService {
  private readonly baseUrl = '/applications';

  /**
   * Get all applications (user's own or all for admin)
   */
  async getApplications(params: ApplicationFilterParams = {}): Promise<PaginatedResponse<Application>> {
    const response: ApiResponse<PaginatedResponse<Application>> = await httpClient.get(
      `${this.baseUrl}/applications/`,
      params,
      true, // enable retry
      true, // enable cache
      5 * 60 * 1000 // 5 minutes TTL
    );
    return response.data;
  }

  /**
   * Get current user's applications (original simple format)
   */
  async getMyApplicationsSimple(): Promise<Application[]> {
    const response: ApiResponse<Application[]> = await httpClient.get(
      `${this.baseUrl}/applications/my-applications/`,
      {},
      true,
      true,
      5 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get current user's applications (with pagination and filtering)
   */
  async getMyApplications(params: Omit<ApplicationFilterParams, 'user__id'> = {}): Promise<PaginatedResponse<Application>> {
    try {
      // First try the paginated endpoint
      const response: ApiResponse<PaginatedResponse<Application>> = await httpClient.get(
        `${this.baseUrl}/applications/my-applications/`,
        params,
        true,
        true,
        5 * 60 * 1000
      );
      return response.data;
    } catch (error) {
      console.warn('Paginated endpoint failed, falling back to simple endpoint:', error);
      // Fallback to simple endpoint and convert to paginated format
      const applications = await this.getMyApplicationsSimple();
      
      // Apply client-side filtering and pagination
      let filteredApps = applications;
      
      // Apply search filter
      if (params.search) {
        const searchLower = params.search.toLowerCase();
        filteredApps = filteredApps.filter(app => 
          app.job?.title?.toLowerCase().includes(searchLower) ||
          app.job?.company?.name?.toLowerCase().includes(searchLower) ||
          app.status?.name?.toLowerCase().includes(searchLower)
        );
      }
      
      // Apply status filter
      if (params.status__name && params.status__name !== 'all') {
        filteredApps = filteredApps.filter(app => app.status?.name === params.status__name);
      }
      
      // Apply sorting
      if (params.ordering) {
        const isDesc = params.ordering.startsWith('-');
        const field = isDesc ? params.ordering.substring(1) : params.ordering;
        
        filteredApps.sort((a, b) => {
          let aVal, bVal;
          if (field === 'applied_at' || field === 'updated_at') {
            aVal = new Date(a[field] || 0).getTime();
            bVal = new Date(b[field] || 0).getTime();
          } else if (field === 'company') {
            aVal = a.job?.company?.name || '';
            bVal = b.job?.company?.name || '';
          } else if (field === 'job_title') {
            aVal = a.job?.title || '';
            bVal = b.job?.title || '';
          } else {
            aVal = a[field as keyof Application] || '';
            bVal = b[field as keyof Application] || '';
          }
          
          if (aVal < bVal) return isDesc ? 1 : -1;
          if (aVal > bVal) return isDesc ? -1 : 1;
          return 0;
        });
      }
      
      // Apply pagination
      const page = params.page || 1;
      const pageSize = params.page_size || 10;
      const startIndex = (page - 1) * pageSize;
      const paginatedApps = filteredApps.slice(startIndex, startIndex + pageSize);
      
      return {
        count: filteredApps.length,
        next: page * pageSize < filteredApps.length ? `page=${page + 1}` : undefined,
        previous: page > 1 ? `page=${page - 1}` : undefined,
        results: paginatedApps
      };
    }
  }

  /**
   * Get applications by status
   */
  async getApplicationsByStatus(status: string, params: ApplicationFilterParams = {}): Promise<PaginatedResponse<Application>> {
    const response: ApiResponse<PaginatedResponse<Application>> = await httpClient.get(
      `${this.baseUrl}/applications/by-status/${status}/`,
      params,
      true,
      true,
      5 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get applications for specific job (admin only)
   */
  async getApplicationsByJob(jobId: number, params: ApplicationFilterParams = {}): Promise<PaginatedResponse<Application>> {
    const response: ApiResponse<PaginatedResponse<Application>> = await httpClient.get(
      `${this.baseUrl}/applications/by-job/${jobId}/`,
      params,
      true,
      true,
      2 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get pending applications for admin review
   */
  async getPendingApplications(params: ApplicationFilterParams = {}): Promise<PaginatedResponse<Application>> {
    const response: ApiResponse<PaginatedResponse<Application>> = await httpClient.get(
      `${this.baseUrl}/applications/admin/pending/`,
      params,
      true,
      true,
      2 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get application details
   */
  async getApplication(id: number): Promise<Application> {
    const response: ApiResponse<Application> = await httpClient.get(
      `${this.baseUrl}/applications/${id}/`,
      {},
      true,
      true,
      10 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Submit job application
   */
  async createApplication(data: CreateApplicationData): Promise<Application> {
    const response: ApiResponse<Application> = await httpClient.post(
      `${this.baseUrl}/applications/`,
      data
    );
    return response.data;
  }

  /**
   * Update application (admin only)
   */
  async updateApplication(id: number, data: UpdateApplicationData): Promise<Application> {
    const response: ApiResponse<Application> = await httpClient.put(
      `${this.baseUrl}/applications/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Partially update application
   */
  async patchApplication(id: number, data: Partial<UpdateApplicationData>): Promise<Application> {
    const response: ApiResponse<Application> = await httpClient.patch(
      `${this.baseUrl}/applications/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Withdraw application
   */
  async withdrawApplication(id: number): Promise<Application> {
    const response: ApiResponse<Application> = await httpClient.post(
      `${this.baseUrl}/applications/${id}/withdraw/`
    );
    return response.data;
  }

  /**
   * Delete application (admin only)
   */
  async deleteApplication(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/applications/${id}/`);
  }

  /**
   * Get all application statuses
   */
  async getApplicationStatuses(): Promise<ApplicationStatus[]> {
    const response: ApiResponse<ApplicationStatus[]> = await httpClient.get(
      `${this.baseUrl}/application-statuses/`,
      {},
      true,
      true,
      30 * 60 * 1000 // 30 minutes cache
    );
    return response.data;
  }

  /**
   * Get available application statuses
   */
  async getAvailableStatuses(): Promise<ApplicationStatus[]> {
    const response: ApiResponse<ApplicationStatus[]> = await httpClient.get(
      `${this.baseUrl}/application-statuses/available/`,
      {},
      true,
      true,
      30 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get user's documents
   */
  async getDocuments(): Promise<Document[]> {
    const response: ApiResponse<Document[]> = await httpClient.get(
      `${this.baseUrl}/documents/`,
      {},
      true,
      true,
      10 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Upload document
   */
  async uploadDocument(data: DocumentUploadData): Promise<Document> {
    const formData = new FormData();
    formData.append('document_type', data.document_type);
    formData.append('file', data.file);
    if (data.file_name) {
      formData.append('file_name', data.file_name);
    }

    const response: ApiResponse<Document> = await httpClient.postFormData(
      `${this.baseUrl}/documents/`,
      formData
    );
    return response.data;
  }

  /**
   * Get document details
   */
  async getDocument(id: number): Promise<Document> {
    const response: ApiResponse<Document> = await httpClient.get(
      `${this.baseUrl}/documents/${id}/`,
      {},
      true,
      true,
      15 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Update document
   */
  async updateDocument(id: number, data: Partial<DocumentUploadData>): Promise<Document> {
    const formData = new FormData();
    if (data.document_type) {
      formData.append('document_type', data.document_type);
    }
    if (data.file) {
      formData.append('file', data.file);
    }
    if (data.file_name) {
      formData.append('file_name', data.file_name);
    }

    const response: ApiResponse<Document> = await httpClient.putFormData(
      `${this.baseUrl}/documents/${id}/`,
      formData
    );
    return response.data;
  }

  /**
   * Delete document
   */
  async deleteDocument(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/documents/${id}/`);
  }

  /**
   * Check if user has already applied to a job
   */
  async hasAppliedToJob(jobId: number): Promise<boolean> {
    try {
      const applications = await this.getMyApplications({
        job__id: jobId,
        page_size: 1
      });
      return applications.count > 0;
    } catch (error) {
      console.warn('Failed to check application status:', error);
      return false;
    }
  }

  /**
   * Get application statistics for admin dashboard
   */
  async getApplicationStats(): Promise<{
    total: number;
    pending: number;
    reviewed: number;
    accepted: number;
    rejected: number;
    withdrawn: number;
  }> {
    try {
      const [total, pending, reviewed, accepted, rejected, withdrawn] = await Promise.allSettled([
        this.getApplications({ page_size: 1 }),
        this.getApplicationsByStatus('pending', { page_size: 1 }),
        this.getApplicationsByStatus('reviewed', { page_size: 1 }),
        this.getApplicationsByStatus('accepted', { page_size: 1 }),
        this.getApplicationsByStatus('rejected', { page_size: 1 }),
        this.getApplicationsByStatus('withdrawn', { page_size: 1 })
      ]);

      return {
        total: total.status === 'fulfilled' ? total.value.count : 0,
        pending: pending.status === 'fulfilled' ? pending.value.count : 0,
        reviewed: reviewed.status === 'fulfilled' ? reviewed.value.count : 0,
        accepted: accepted.status === 'fulfilled' ? accepted.value.count : 0,
        rejected: rejected.status === 'fulfilled' ? rejected.value.count : 0,
        withdrawn: withdrawn.status === 'fulfilled' ? withdrawn.value.count : 0
      };
    } catch (error) {
      console.warn('Failed to get application stats:', error);
      return {
        total: 0,
        pending: 0,
        reviewed: 0,
        accepted: 0,
        rejected: 0,
        withdrawn: 0
      };
    }
  }
}

// Create and export service instance
export const applicationService = new ApplicationService();