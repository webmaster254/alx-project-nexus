import { describe, it, expect, vi, beforeEach } from 'vitest';
import { jobService } from '../jobService';
import { httpClient } from '../index';
import { Job, PaginatedResponse } from '../../types';

// Mock the httpClient
vi.mock('../index', () => ({
  httpClient: {
    get: vi.fn(),
  },
}));

const mockHttpClient = vi.mocked(httpClient);

describe('JobService', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

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
    external_url: null,
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
    categories: [
      {
        id: 1,
        name: 'Engineering',
        description: 'Engineering jobs',
      },
    ],
    salary_display: '$80,000 - $120,000',
    days_since_posted: '1 day ago',
    is_new: true,
    is_urgent: false,
    can_apply: true,
  };

  const mockPaginatedResponse: PaginatedResponse<Job> = {
    count: 1,
    next: null,
    previous: null,
    results: [mockJob],
  };

  describe('getJobs', () => {
    it('should fetch jobs with default parameters', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getJobs();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {});
      expect(result).toEqual(mockPaginatedResponse);
    });

    it('should fetch jobs with parameters', async () => {
      const params = {
        page: 2,
        page_size: 10,
        category: [1, 2],
        location: ['New York'],
        experience_level: ['mid'],
        is_remote: true,
        search: 'engineer',
      };

      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getJobs(params);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        page: 2,
        page_size: 10,
        category: '1,2',
        location: 'New York',
        experience_level: 'mid',
        is_remote: true,
        search: 'engineer',
      });
      expect(result).toEqual(mockPaginatedResponse);
    });
  });

  describe('getJob', () => {
    it('should fetch a single job by ID', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockJob, status: 200 });

      const result = await jobService.getJob(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/1/');
      expect(result).toEqual(mockJob);
    });
  });

  describe('searchJobs', () => {
    it('should search jobs with query and filters', async () => {
      const query = 'software engineer';
      const filters = {
        categories: [1],
        locations: ['New York'],
        experience_levels: ['mid'],
        is_remote: false,
      };

      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.searchJobs(query, filters);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        search: query,
        category: '1',
        location: 'New York',
        experience_level: 'mid',
        is_remote: false,
      });
      expect(result).toEqual(mockPaginatedResponse);
    });

    it('should search jobs with query only', async () => {
      const query = 'developer';

      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.searchJobs(query);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        search: query,
      });
      expect(result).toEqual(mockPaginatedResponse);
    });
  });

  describe('getFeaturedJobs', () => {
    it('should fetch featured jobs', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getFeaturedJobs();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        is_featured: true,
        page_size: 10,
      });
      expect(result).toEqual([mockJob]);
    });
  });

  describe('getRecentJobs', () => {
    it('should fetch recent jobs with default limit', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getRecentJobs();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        ordering: '-created_at',
        page_size: 10,
      });
      expect(result).toEqual([mockJob]);
    });

    it('should fetch recent jobs with custom limit', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getRecentJobs(5);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        ordering: '-created_at',
        page_size: 5,
      });
      expect(result).toEqual([mockJob]);
    });
  });

  describe('getSimilarJobs', () => {
    it('should fetch similar jobs', async () => {
      mockHttpClient.get.mockResolvedValue({ data: [mockJob], status: 200 });

      const result = await jobService.getSimilarJobs(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/1/similar/', { limit: 5 });
      expect(result).toEqual([mockJob]);
    });

    it('should fetch similar jobs with custom limit', async () => {
      mockHttpClient.get.mockResolvedValue({ data: [mockJob], status: 200 });

      const result = await jobService.getSimilarJobs(1, 3);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/1/similar/', { limit: 3 });
      expect(result).toEqual([mockJob]);
    });
  });

  describe('getJobsByCategory', () => {
    it('should fetch jobs by category', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getJobsByCategory(1);

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        category: '1',
      });
      expect(result).toEqual(mockPaginatedResponse);
    });
  });

  describe('getJobsByLocation', () => {
    it('should fetch jobs by location', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getJobsByLocation('New York');

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        location: 'New York',
      });
      expect(result).toEqual(mockPaginatedResponse);
    });
  });

  describe('getRemoteJobs', () => {
    it('should fetch remote jobs', async () => {
      mockHttpClient.get.mockResolvedValue({ data: mockPaginatedResponse, status: 200 });

      const result = await jobService.getRemoteJobs();

      expect(mockHttpClient.get).toHaveBeenCalledWith('/jobs/', {
        is_remote: true,
      });
      expect(result).toEqual(mockPaginatedResponse);
    });
  });
});