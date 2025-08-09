import { describe, it, expect, vi, beforeEach } from 'vitest';
import { categoryService } from '../categoryService';
import { httpClient } from '../index';
import type { Category, PaginatedResponse } from '../../types';

// Mock the httpClient
vi.mock('../index', () => ({
  httpClient: {
    get: vi.fn(),
  },
}));

const mockHttpClient = vi.mocked(httpClient);

describe('CategoryService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const mockCategory: Category = {
    id: 1,
    name: 'Engineering',
    description: 'Software engineering and development roles',
  };

  const mockPaginatedResponse: PaginatedResponse<Category> = {
    count: 1,
    next: undefined,
    previous: undefined,
    results: [mockCategory],
  };

  describe('getCategories', () => {
    it('should fetch all categories', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await categoryService.getCategories();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/');
      expect(result).toEqual([mockCategory]);
    });

    it('should handle empty categories response', async () => {
      const emptyResponse: PaginatedResponse<Category> = {
        count: 0,
        next: undefined,
        previous: undefined,
        results: [],
      };

      mockHttpClient.get.mockResolvedValue({ data: emptyResponse, status: 200 });

      const result = await categoryService.getCategories();

      expect(result).toEqual([]);
    });

    it('should handle API errors', async () => {
      const error = new Error('Network error');
      mockHttpClient.get.mockRejectedValue(error);

      await expect(categoryService.getCategories()).rejects.toThrow('Network error');
    });
  });

  describe('getCategory', () => {
    it('should fetch a single category by ID', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockCategory, status: 200 });

      const result = await categoryService.getCategory(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/1/');
      expect(result).toEqual(mockCategory);
    });

    it('should handle category not found', async () => {
      const error = new Error('Category not found');
      mockHttpClient.get.mockRejectedValue(error);

      await expect(categoryService.getCategory(999)).rejects.toThrow('Category not found');
    });
  });

  describe('getCategoryJobs', () => {
    it('should fetch jobs for a specific category', async () => {
      const mockJobsResponse = {
        count: 2,
        next: null,
        previous: null,
        results: [
          { id: 1, title: 'Software Engineer', category: mockCategory },
          { id: 2, title: 'Frontend Developer', category: mockCategory },
        ],
      };

      mockHttpClient.get.mockResolvedValue({ data: mockJobsResponse, status: 200 });

      const result = await categoryService.getCategoryJobs(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        category: '1',
      });
      expect(result).toEqual(mockJobsResponse);
    });

    it('should fetch jobs with pagination parameters', async () => {
      const mockJobsResponse = {
        count: 10,
        next: 'http://api.example.com/jobs/?page=2',
        previous: null,
        results: [],
      };

      mockHttpClient.get.mockResolvedValue({ data: mockJobsResponse, status: 200 });

      const result = await categoryService.getCategoryJobs(1, { page: 1, page_size: 5 });

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        category: '1',
        page: 1,
        page_size: 5,
      });
      expect(result).toEqual(mockJobsResponse);
    });
  });

  describe('getPopularCategories', () => {
    it('should fetch popular categories with job counts', async () => {
      const mockPopularCategories = [
        { ...mockCategory, job_count: 150 },
        { id: 2, name: 'Design', description: 'UI/UX and graphic design', job_count: 75 },
      ];

      mockHttpClient.get.mockResolvedValue({ data: mockPopularCategories, status: 200 });

      const result = await categoryService.getPopularCategories();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/popular/');
      expect(result).toEqual(mockPopularCategories);
    });

    it('should fetch popular categories with custom limit', async () => {
      const mockPopularCategories = [mockCategory];

      mockHttpClient.get.mockResolvedValue({ data: mockPopularCategories, status: 200 });

      const result = await categoryService.getPopularCategories(5);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/popular/', {
        limit: 5,
      });
      expect(result).toEqual(mockPopularCategories);
    });
  });

  describe('searchCategories', () => {
    it('should search categories by query', async () => {
      const searchResults = [
        { id: 1, name: 'Software Engineering', description: 'Software development roles' },
        { id: 2, name: 'Engineering Management', description: 'Engineering leadership roles' },
      ];

      mockHttpClient.get.mockResolvedValue({ data: { results: searchResults }, status: 200 });

      const result = await categoryService.searchCategories('engineering');

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        search: 'engineering',
      });
      expect(result).toEqual(searchResults);
    });

    it('should handle empty search results', async () => {
      mockHttpClient.get.mockResolvedValue({ data: { results: [] }, status: 200 });

      const result = await categoryService.searchCategories('nonexistent');

      expect(result).toEqual([]);
    });
  });
});