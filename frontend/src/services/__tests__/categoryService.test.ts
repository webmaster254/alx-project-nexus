import { describe, it, expect, vi, beforeEach } from 'vitest';
import { categoryService } from '../categoryService';
import { httpClient } from '../index';
import type { Category, PaginatedResponse, Job } from '../../types';

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
    description: 'Engineering jobs',
    parent_id: undefined,
    children: [],
  };

  const mockPaginatedCategoryResponse: PaginatedResponse<Category> = {
    count: 1,
    next: undefined,
    previous: undefined,
    results: [mockCategory],
  };

  const mockJob: Job = {
    id: 1,
    title: 'Software Engineer',
    description: 'Job description',
    summary: 'Job summary',
    location: 'New York',
    is_remote: false,
    salary_min: 80000,
    salary_max: 120000,
    salary_type: 'yearly',
    salary_currency: 'USD',
    experience_level: 'mid',
    required_skills: 'JavaScript, React',
    preferred_skills: 'TypeScript',
    application_deadline: '2024-12-31',
    external_url: undefined,
    is_active: true,
    is_featured: false,
    views_count: 100,
    applications_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
    company: {
      id: 1,
      name: 'Tech Corp',
      description: 'A tech company',
      website: 'https://techcorp.com',
      logo: 'logo.png',
      size: '100-500',
      industry: 'Technology',
      location: 'New York',
    },
    industry: {
      id: 1,
      name: 'Technology',
      description: 'Tech industry',
    },
    job_type: {
      id: 1,
      name: 'Full-time',
      description: 'Full-time position',
    },
    categories: [mockCategory],
    salary_display: '$80,000 - $120,000',
    days_since_posted: '1 day ago',
    is_new: true,
    is_urgent: false,
    can_apply: true,
  };

  const mockPaginatedJobResponse: PaginatedResponse<Job> = {
    count: 1,
    next: undefined,
    previous: undefined,
    results: [mockJob],
  };

  describe('getCategories', () => {
    it('should fetch all categories', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedCategoryResponse, status: 200 });

      const result = await categoryService.getCategories();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/');
      expect(result).toEqual([mockCategory]);
    });
  });

  describe('getCategory', () => {
    it('should fetch a single category by ID', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockCategory, status: 200 });

      const result = await categoryService.getCategory(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/1/');
      expect(result).toEqual(mockCategory);
    });
  });

  describe('getCategoryJobs', () => {
    it('should fetch jobs for a category with default parameters', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedJobResponse, status: 200 });

      const result = await categoryService.getCategoryJobs(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/1/jobs/', {
        page: 1,
        page_size: 20,
      });
      expect(result).toEqual(mockPaginatedJobResponse);
    });

    it('should fetch jobs for a category with custom parameters', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedJobResponse, status: 200 });

      const result = await categoryService.getCategoryJobs(1, 2, 10);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/1/jobs/', {
        page: 2,
        page_size: 10,
      });
      expect(result).toEqual(mockPaginatedJobResponse);
    });
  });

  describe('getCategoriesWithJobCounts', () => {
    it('should fetch categories with job counts', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedCategoryResponse, status: 200 });

      const result = await categoryService.getCategoriesWithJobCounts();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        include_job_count: true,
      });
      expect(result).toEqual([mockCategory]);
    });
  });

  describe('getTopLevelCategories', () => {
    it('should fetch top-level categories', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedCategoryResponse, status: 200 });

      const result = await categoryService.getTopLevelCategories();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        parent_id__isnull: true,
      });
      expect(result).toEqual([mockCategory]);
    });
  });

  describe('getSubcategories', () => {
    it('should fetch subcategories for a parent category', async () => {
      const subcategory: Category = {
        id: 2,
        name: 'Frontend',
        description: 'Frontend engineering',
        parent_id: 1,
      };
      const subcategoryResponse: PaginatedResponse<Category> = {
        count: 1,
        next: undefined,
        previous: undefined,
        results: [subcategory],
      };

      mockHttpClient.get.mockResolvedValue({ data: subcategoryResponse, status: 200 });

      const result = await categoryService.getSubcategories(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        parent_id: 1,
      });
      expect(result).toEqual([subcategory]);
    });
  });

  describe('searchCategories', () => {
    it('should search categories by name', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedCategoryResponse, status: 200 });

      const result = await categoryService.searchCategories('engineering');

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        search: 'engineering',
      });
      expect(result).toEqual([mockCategory]);
    });
  });

  describe('getCategoryHierarchy', () => {
    it('should fetch category hierarchy with children', async () => {
      const categoryWithChildren: Category = {
        ...mockCategory,
        children: [
          {
            id: 2,
            name: 'Frontend',
            description: 'Frontend engineering',
            parent_id: 1,
          },
        ],
      };
      const hierarchyResponse: PaginatedResponse<Category> = {
        count: 1,
        next: undefined,
        previous: undefined,
        results: [categoryWithChildren],
      };

      mockHttpClient.get.mockResolvedValue({ data: hierarchyResponse, status: 200 });

      const result = await categoryService.getCategoryHierarchy();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/categories/', {
        include_children: true,
      });
      expect(result).toEqual([categoryWithChildren]);
    });
  });
});