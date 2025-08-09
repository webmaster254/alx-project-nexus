import { httpClient } from './index';
import type { Job, PaginatedResponse, JobListParams, FilterParams, ApiResponse } from '../types';

export class JobService {
  private readonly baseUrl = '/jobs';

  /**
   * Fetch paginated list of jobs with optional parameters
   */
  async getJobs(params: JobListParams = {}): Promise<PaginatedResponse<Job>> {
    // Cache job listings for 2 minutes (shorter TTL for frequently changing data)
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      this.buildJobParams(params),
      true, // enable retry
      true, // enable cache
      2 * 60 * 1000 // 2 minutes TTL
    );
    return response.data;
  }

  /**
   * Fetch a single job by ID
   */
  async getJob(id: number): Promise<Job> {
    // Cache individual job details for 5 minutes (longer TTL for less frequently changing data)
    const response: ApiResponse<Job> = await httpClient.get(
      `${this.baseUrl}/${id}/`,
      undefined,
      true, // enable retry
      true, // enable cache
      5 * 60 * 1000 // 5 minutes TTL
    );
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
    // Cache featured jobs for 10 minutes (longer TTL for curated content)
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      { is_featured: true, page_size: 10 },
      true, // enable retry
      true, // enable cache
      10 * 60 * 1000 // 10 minutes TTL
    );
    return response.data.results;
  }

  /**
   * Get recent jobs
   */
  async getRecentJobs(limit: number = 10): Promise<Job[]> {
    // Cache recent jobs for 1 minute (short TTL for time-sensitive data)
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/`,
      { ordering: '-created_at', page_size: limit },
      true, // enable retry
      true, // enable cache
      1 * 60 * 1000 // 1 minute TTL
    );
    return response.data.results;
  }

  /**
   * Get similar jobs based on a job ID
   */
  async getSimilarJobs(jobId: number, limit: number = 5): Promise<Job[]> {
    // Cache similar jobs for 15 minutes (longer TTL for recommendation data)
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/similar/`,
      { job_id: jobId, page_size: limit },
      true, // enable retry
      true, // enable cache
      15 * 60 * 1000 // 15 minutes TTL
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