import React from 'react';
import { screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, createMockJob, createMockPaginatedResponse } from '../testUtils';
import JobListingPage from '../../pages/JobListingPage';
import * as jobService from '../../services/jobService';

// Mock the job service
vi.mock('../../services/jobService');
const mockJobService = vi.mocked(jobService);

describe('Job Search Integration', () => {
  const mockJobs = [
    createMockJob({
      id: 1,
      title: 'Frontend Developer',
      company: { name: 'TechCorp' },
      location: 'San Francisco, CA',
      is_remote: false,
    }),
    createMockJob({
      id: 2,
      title: 'Backend Engineer',
      company: { name: 'DataCorp' },
      location: 'New York, NY',
      is_remote: true,
    }),
    createMockJob({
      id: 3,
      title: 'Full Stack Developer',
      company: { name: 'StartupCorp' },
      location: 'Austin, TX',
      is_remote: false,
    }),
  ];

  beforeEach(() => {
    vi.clearAllMocks();
    mockJobService.getJobs.mockResolvedValue(
      createMockPaginatedResponse(mockJobs)
    );
  });

  it('should display jobs on initial load', async () => {
    render(<JobListingPage />);

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();
    });

    expect(mockJobService.getJobs).toHaveBeenCalledWith({});
  });

  it('should filter jobs by search query', async () => {
    const user = userEvent.setup();
    const filteredJobs = [mockJobs[0]]; // Only Frontend Developer

    mockJobService.searchJobs.mockResolvedValue(
      createMockPaginatedResponse(filteredJobs)
    );

    render(<JobListingPage />);

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Search for "frontend"
    const searchInput = screen.getByPlaceholderText(/search jobs/i);
    await user.type(searchInput, 'frontend');
    await user.click(screen.getByRole('button', { name: /search/i }));

    await waitFor(() => {
      expect(mockJobService.searchJobs).toHaveBeenCalledWith('frontend', expect.any(Object));
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.queryByText('Backend Engineer')).not.toBeInTheDocument();
    });
  });

  it('should filter jobs by location', async () => {
    const user = userEvent.setup();
    const filteredJobs = [mockJobs[1]]; // Only New York job

    mockJobService.getJobs.mockResolvedValue(
      createMockPaginatedResponse(filteredJobs)
    );

    render(<JobListingPage />);

    // Open location filter
    const locationFilter = screen.getByText(/location/i);
    await user.click(locationFilter);

    // Select New York
    const newYorkOption = screen.getByText('New York, NY');
    await user.click(newYorkOption);

    // Apply filters
    const applyButton = screen.getByRole('button', { name: /apply filters/i });
    await user.click(applyButton);

    await waitFor(() => {
      expect(mockJobService.getJobs).toHaveBeenCalledWith(
        expect.objectContaining({
          location: ['New York, NY'],
        })
      );
    });
  });

  it('should filter jobs by remote work', async () => {
    const user = userEvent.setup();
    const remoteJobs = [mockJobs[1]]; // Only remote job

    mockJobService.getJobs.mockResolvedValue(
      createMockPaginatedResponse(remoteJobs)
    );

    render(<JobListingPage />);

    // Toggle remote filter
    const remoteToggle = screen.getByLabelText(/remote only/i);
    await user.click(remoteToggle);

    await waitFor(() => {
      expect(mockJobService.getJobs).toHaveBeenCalledWith(
        expect.objectContaining({
          is_remote: true,
        })
      );
    });
  });

  it('should sort jobs correctly', async () => {
    const user = userEvent.setup();
    const sortedJobs = [...mockJobs].reverse(); // Reverse order

    mockJobService.getJobs.mockResolvedValue(
      createMockPaginatedResponse(sortedJobs)
    );

    render(<JobListingPage />);

    // Change sort order
    const sortDropdown = screen.getByLabelText(/sort by/i);
    await user.selectOptions(sortDropdown, 'title_asc');

    await waitFor(() => {
      expect(mockJobService.getJobs).toHaveBeenCalledWith(
        expect.objectContaining({
          ordering: 'title',
        })
      );
    });
  });

  it('should handle empty search results', async () => {
    const user = userEvent.setup();

    mockJobService.searchJobs.mockResolvedValue(
      createMockPaginatedResponse([])
    );

    render(<JobListingPage />);

    // Search for something that returns no results
    const searchInput = screen.getByPlaceholderText(/search jobs/i);
    await user.type(searchInput, 'nonexistent job');
    await user.click(screen.getByRole('button', { name: /search/i }));

    await waitFor(() => {
      expect(screen.getByText(/no jobs found/i)).toBeInTheDocument();
      expect(screen.getByText(/try adjusting your search criteria/i)).toBeInTheDocument();
    });
  });

  it('should clear filters correctly', async () => {
    const user = userEvent.setup();

    render(<JobListingPage />);

    // Apply some filters first
    const searchInput = screen.getByPlaceholderText(/search jobs/i);
    await user.type(searchInput, 'developer');

    const remoteToggle = screen.getByLabelText(/remote only/i);
    await user.click(remoteToggle);

    // Clear filters
    const clearButton = screen.getByRole('button', { name: /clear filters/i });
    await user.click(clearButton);

    await waitFor(() => {
      expect(searchInput).toHaveValue('');
      expect(remoteToggle).not.toBeChecked();
      expect(mockJobService.getJobs).toHaveBeenCalledWith({});
    });
  });

  it('should handle API errors gracefully', async () => {
    mockJobService.getJobs.mockRejectedValue(new Error('API Error'));

    render(<JobListingPage />);

    await waitFor(() => {
      expect(screen.getByText(/error loading jobs/i)).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });
  });

  it('should retry loading jobs after error', async () => {
    const user = userEvent.setup();

    // First call fails
    mockJobService.getJobs.mockRejectedValueOnce(new Error('API Error'));
    // Second call succeeds
    mockJobService.getJobs.mockResolvedValue(
      createMockPaginatedResponse(mockJobs)
    );

    render(<JobListingPage />);

    // Wait for error state
    await waitFor(() => {
      expect(screen.getByText(/error loading jobs/i)).toBeInTheDocument();
    });

    // Click retry
    const retryButton = screen.getByRole('button', { name: /try again/i });
    await user.click(retryButton);

    // Should show jobs after retry
    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    expect(mockJobService.getJobs).toHaveBeenCalledTimes(2);
  });

  it('should load more jobs with infinite scroll', async () => {
    const firstPageJobs = [mockJobs[0]];
    const secondPageJobs = [mockJobs[1]];

    // First call returns first page
    mockJobService.getJobs.mockResolvedValueOnce(
      createMockPaginatedResponse(firstPageJobs, {
        next: 'http://api.example.com/jobs/?page=2',
      })
    );

    // Second call returns second page
    mockJobService.getJobs.mockResolvedValueOnce(
      createMockPaginatedResponse(secondPageJobs, {
        previous: 'http://api.example.com/jobs/?page=1',
      })
    );

    render(<JobListingPage />);

    // Wait for first page to load
    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Simulate scrolling to bottom (trigger infinite scroll)
    const loadMoreTrigger = screen.getByTestId('load-more-trigger');
    fireEvent.scroll(loadMoreTrigger);

    // Wait for second page to load
    await waitFor(() => {
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });

    expect(mockJobService.getJobs).toHaveBeenCalledTimes(2);
  });
});