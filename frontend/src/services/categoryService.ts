import { httpClient } from './index';
import type { Category, PaginatedResponse, Job, ApiResponse } from '../types';

// Extended interfaces for admin operations
export interface Industry {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  companies_count?: number;
  jobs_count?: number;
}

export interface JobType {
  id: number;
  name: string;
  description?: string;
  created_at: string;
  updated_at: string;
  jobs_count?: number;
}

export interface CategoryData {
  name: string;
  description?: string;
  parent_id?: number;
  is_active?: boolean;
}

export interface IndustryData {
  name: string;
  description?: string;
}

export interface JobTypeData {
  name: string;
  description?: string;
}

export interface CategoryFilterParams {
  search?: string;
  parent_id?: number;
  parent_id__isnull?: boolean;
  is_active?: boolean;
  include_job_count?: boolean;
  include_children?: boolean;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export class CategoryService {
  private readonly baseUrl = '/categories';

  // Categories
  /**
   * Fetch all categories with pagination
   */
  async getCategories(params: CategoryFilterParams = {}): Promise<PaginatedResponse<Category>> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/categories/`,
      params,
      true,
      true,
      10 * 60 * 1000 // 10 minutes cache
    );
    return response.data;
  }

  /**
   * Fetch all categories as array (for compatibility)
   */
  async getAllCategories(): Promise<Category[]> {
    const response = await this.getCategories({ page_size: 1000 });
    return response.results;
  }

  /**
   * Fetch a single category by ID
   */
  async getCategory(id: number): Promise<Category> {
    const response: ApiResponse<Category> = await httpClient.get(
      `${this.baseUrl}/categories/${id}/`,
      {},
      true,
      true,
      10 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Create new category (admin only)
   */
  async createCategory(data: CategoryData): Promise<Category> {
    const response: ApiResponse<Category> = await httpClient.post(
      `${this.baseUrl}/categories/`,
      data
    );
    return response.data;
  }

  /**
   * Update category (admin only)
   */
  async updateCategory(id: number, data: Partial<CategoryData>): Promise<Category> {
    const response: ApiResponse<Category> = await httpClient.put(
      `${this.baseUrl}/categories/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Partially update category (admin only)
   */
  async patchCategory(id: number, data: Partial<CategoryData>): Promise<Category> {
    const response: ApiResponse<Category> = await httpClient.patch(
      `${this.baseUrl}/categories/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete category (admin only)
   */
  async deleteCategory(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/categories/${id}/`);
  }

  /**
   * Fetch jobs for a specific category
   */
  async getCategoryJobs(categoryId: number, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Job>> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/categories/${categoryId}/jobs/`,
      { page, page_size: pageSize },
      true,
      true,
      5 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get categories with job counts
   */
  async getCategoriesWithJobCounts(): Promise<Category[]> {
    const response = await this.getCategories({ include_job_count: true, page_size: 1000 });
    return response.results;
  }

  /**
   * Get top-level categories (no parent)
   */
  async getTopLevelCategories(): Promise<Category[]> {
    const response = await this.getCategories({ parent_id__isnull: true, page_size: 1000 });
    return response.results;
  }

  /**
   * Get subcategories for a parent category
   */
  async getSubcategories(parentId: number): Promise<Category[]> {
    const response = await this.getCategories({ parent_id: parentId, page_size: 1000 });
    return response.results;
  }

  /**
   * Search categories by name
   */
  async searchCategories(query: string): Promise<Category[]> {
    const response = await this.getCategories({ search: query, page_size: 1000 });
    return response.results;
  }

  /**
   * Get category hierarchy (categories with their children)
   */
  async getCategoryHierarchy(): Promise<Category[]> {
    const response = await this.getCategories({ include_children: true, page_size: 1000 });
    return response.results;
  }

  // Industries
  /**
   * Fetch all industries
   */
  async getIndustries(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}): Promise<PaginatedResponse<Industry>> {
    const response: ApiResponse<PaginatedResponse<Industry>> = await httpClient.get(
      `${this.baseUrl}/industries/`,
      params,
      true,
      true,
      15 * 60 * 1000 // 15 minutes cache
    );
    return response.data;
  }

  /**
   * Fetch all industries as array
   */
  async getAllIndustries(): Promise<Industry[]> {
    const response = await this.getIndustries({ page_size: 1000 });
    return response.results;
  }

  /**
   * Fetch a single industry by ID
   */
  async getIndustry(id: number): Promise<Industry> {
    const response: ApiResponse<Industry> = await httpClient.get(
      `${this.baseUrl}/industries/${id}/`,
      {},
      true,
      true,
      15 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Create new industry (admin only)
   */
  async createIndustry(data: IndustryData): Promise<Industry> {
    const response: ApiResponse<Industry> = await httpClient.post(
      `${this.baseUrl}/industries/`,
      data
    );
    return response.data;
  }

  /**
   * Update industry (admin only)
   */
  async updateIndustry(id: number, data: Partial<IndustryData>): Promise<Industry> {
    const response: ApiResponse<Industry> = await httpClient.put(
      `${this.baseUrl}/industries/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete industry (admin only)
   */
  async deleteIndustry(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/industries/${id}/`);
  }

  // Job Types
  /**
   * Fetch all job types
   */
  async getJobTypes(params: { search?: string; page?: number; page_size?: number; ordering?: string } = {}): Promise<PaginatedResponse<JobType>> {
    const response: ApiResponse<PaginatedResponse<JobType>> = await httpClient.get(
      `${this.baseUrl}/job-types/`,
      params,
      true,
      true,
      15 * 60 * 1000 // 15 minutes cache
    );
    return response.data;
  }

  /**
   * Fetch all job types as array
   */
  async getAllJobTypes(): Promise<JobType[]> {
    const response = await this.getJobTypes({ page_size: 1000 });
    return response.results;
  }

  /**
   * Fetch a single job type by ID
   */
  async getJobType(id: number): Promise<JobType> {
    const response: ApiResponse<JobType> = await httpClient.get(
      `${this.baseUrl}/job-types/${id}/`,
      {},
      true,
      true,
      15 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Create new job type (admin only)
   */
  async createJobType(data: JobTypeData): Promise<JobType> {
    const response: ApiResponse<JobType> = await httpClient.post(
      `${this.baseUrl}/job-types/`,
      data
    );
    return response.data;
  }

  /**
   * Update job type (admin only)
   */
  async updateJobType(id: number, data: Partial<JobTypeData>): Promise<JobType> {
    const response: ApiResponse<JobType> = await httpClient.put(
      `${this.baseUrl}/job-types/${id}/`,
      data
    );
    return response.data;
  }

  /**
   * Delete job type (admin only)
   */
  async deleteJobType(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/job-types/${id}/`);
  }

  // Bulk operations
  /**
   * Bulk update categories (admin only)
   */
  async bulkUpdateCategories(ids: number[], data: Partial<CategoryData>): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      ids.map(id => this.patchCategory(id, data))
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
   * Bulk delete categories (admin only)
   */
  async bulkDeleteCategories(ids: number[]): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      ids.map(id => this.deleteCategory(id))
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

  // Statistics
  /**
   * Get category statistics
   */
  async getCategoryStats(): Promise<{
    total_categories: number;
    active_categories: number;
    top_level_categories: number;
    total_industries: number;
    total_job_types: number;
  }> {
    try {
      const [categories, activeCategories, topLevelCategories, industries, jobTypes] = await Promise.allSettled([
        this.getCategories({ page_size: 1 }),
        this.getCategories({ is_active: true, page_size: 1 }),
        this.getCategories({ parent_id__isnull: true, page_size: 1 }),
        this.getIndustries({ page_size: 1 }),
        this.getJobTypes({ page_size: 1 })
      ]);

      return {
        total_categories: categories.status === 'fulfilled' ? categories.value.count : 0,
        active_categories: activeCategories.status === 'fulfilled' ? activeCategories.value.count : 0,
        top_level_categories: topLevelCategories.status === 'fulfilled' ? topLevelCategories.value.count : 0,
        total_industries: industries.status === 'fulfilled' ? industries.value.count : 0,
        total_job_types: jobTypes.status === 'fulfilled' ? jobTypes.value.count : 0
      };
    } catch (error) {
      console.warn('Failed to get category stats:', error);
      return {
        total_categories: 0,
        active_categories: 0,
        top_level_categories: 0,
        total_industries: 0,
        total_job_types: 0
      };
    }
  }
}

// Create and export service instance
export const categoryService = new CategoryService();