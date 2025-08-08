import { httpClient } from './index';
import type { Job, PaginatedResponse, JobListParams, FilterParams, ApiResponse } from '../types';

export class JobService {
  private readonly baseUrl = '/jobs';

  /**
   * Fetch paginated list of jobs with optional parameters
   */
  async getJobs(params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      this.buildJobParams(params)
    );
    return response.data;
  }

  /**
   * Fetch a single job by ID
   */
  async getJob(id: number): Promise<Job> {
    const response: ApiResponse<Job> = await httpClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  /**
   * Search jobs with query and filters
   */
  async searchJobs(query: string, filters: FilterParams = {}): Promise<PaginatedResponse<Job>> {
    const params: JobListParams = {
      search: query,
      category: filters.categories,
      location: filters.locations,
      experience_level: filters.experience_levels,
      is_remote: filters.is_remote,
      salary_min: filters.salary_range?.[0],
      salary_max: filters.salary_range?.[1],
      job_type: filters.job_types,
    };

    return this.getJobs(params);
  }

  /**
   * Get featured jobs
   */
  async getFeaturedJobs(): Promise<Job[]> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      { is_featured: true, page_size: 10 }
    );
    return response.data.results;
  }

  /**
   * Get recent jobs
   */
  async getRecentJobs(limit: number = 10): Promise<Job[]> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      { ordering: '-created_at', page_size: limit }
    );
    return response.data.results;
  }

  /**
   * Get similar jobs based on a job ID
   */
  async getSimilarJobs(jobId: number, limit: number = 5): Promise<Job[]> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/similar/`,
      { job_id: jobId, page_size: limit }
    );
    return response.data.results;
  }

  /**
   * Get jobs by category
   */
  async getJobsByCategory(categoryId: number, params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    const jobParams = {
      ...params,
      category: [categoryId],
    };
    return this.getJobs(jobParams);
  }

  /**
   * Get jobs by location
   */
  async getJobsByLocation(location: string, params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    const jobParams = {
      ...params,
      location: [location],
    };
    return this.getJobs(jobParams);
  }

  /**
   * Get remote jobs
   */
  async getRemoteJobs(params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    const jobParams = {
      ...params,
      is_remote: true,
    };
    return this.getJobs(jobParams);
  }

  /**
   * Build query parameters for job requests
   */
  private buildJobParams(params: JobListParams): Record<string, any> {
    const queryParams: Record<string, any> = {};

    // Handle pagination
    if (params.page) queryParams.page = params.page;
    if (params.page_size) queryParams.page_size = params.page_size;

    // Handle arrays - convert to comma-separated strings or multiple params
    if (params.category && params.category.length > 0) {
      queryParams.category = params.category.join(',');
    }
    if (params.location && params.location.length > 0) {
      queryParams.location = params.location.join(',');
    }
    if (params.experience_level && params.experience_level.length > 0) {
      queryParams.experience_level = params.experience_level.join(',');
    }
    if (params.job_type && params.job_type.length > 0) {
      queryParams.job_type = params.job_type.join(',');
    }

    // Handle boolean and other simple params
    if (params.is_remote !== undefined) queryParams.is_remote = params.is_remote;
    if (params.salary_min) queryParams.salary_min = params.salary_min;
    if (params.salary_max) queryParams.salary_max = params.salary_max;
    if (params.search) queryParams.search = params.search;
    if (params.ordering) queryParams.ordering = params.ordering;

    return queryParams;
  }
}

// Create and export service instance
export const jobService = new JobService();