import { httpClient } from './index';
import type { Category, PaginatedResponse, Job, ApiResponse } from '../types';

export class CategoryService {
  private readonly baseUrl = '/categories';

  /**
   * Fetch all categories
   */
  async getCategories(): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`
    );
    return response.data.results;
  }

  /**
   * Fetch a single category by ID
   */
  async getCategory(id: number): Promise<Category> {
    const response: ApiResponse<Category> = await httpClient.get(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  /**
   * Fetch jobs for a specific category
   */
  async getCategoryJobs(categoryId: number, page: number = 1, pageSize: number = 20): Promise<PaginatedResponse<Job>> {
    const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
      `${this.baseUrl}/${categoryId}/jobs/`,
      { page, page_size: pageSize }
    );
    return response.data;
  }

  /**
   * Get categories with job counts
   */
  async getCategoriesWithJobCounts(): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`,
      { include_job_count: true }
    );
    return response.data.results;
  }

  /**
   * Get top-level categories (no parent)
   */
  async getTopLevelCategories(): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`,
      { parent_id__isnull: true }
    );
    return response.data.results;
  }

  /**
   * Get subcategories for a parent category
   */
  async getSubcategories(parentId: number): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`,
      { parent_id: parentId }
    );
    return response.data.results;
  }

  /**
   * Search categories by name
   */
  async searchCategories(query: string): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`,
      { search: query }
    );
    return response.data.results;
  }

  /**
   * Get category hierarchy (categories with their children)
   */
  async getCategoryHierarchy(): Promise<Category[]> {
    const response: ApiResponse<PaginatedResponse<Category>> = await httpClient.get(
      `${this.baseUrl}/`,
      { include_children: true }
    );
    return response.data.results;
  }
}

// Create and export service instance
export const categoryService = new CategoryService();