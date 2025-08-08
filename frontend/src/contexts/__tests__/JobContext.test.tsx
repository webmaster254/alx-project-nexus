import { render, screen, act } from '@testing-library/react';
import { vi } from 'vitest';
import { JobProvider, useJob } from '../JobContext';
import type { Job, PaginatedResponse } from '../../types';

// Mock job data
const mockJob: Job = {
  id: 1,
  title: 'Software Engineer',
  description: 'A great job opportunity',
  summary: 'Software development role',
  location: 'New York, NY',
  is_remote: false,
  salary_min: 80000,
  salary_max: 120000,
  salary_type: 'yearly',
  salary_currency: 'USD',
  experience_level: 'mid',
  required_skills: 'JavaScript, React',
  preferred_skills: 'TypeScript, Node.js',
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
    logo: null,
    size: '100-500',
    industry: 'Technology',
    location: 'New York, NY',
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
      description: 'Engineering roles',
    },
  ],
  salary_display: '$80,000 - $120,000',
  days_since_posted: '1 day ago',
  is_new: true,
  is_urgent: false,
  can_apply: true,
};

const mockPaginatedResponse: PaginatedResponse<Job> = {
  count: 10,
  next: 'http://api.example.com/jobs/?page=2',
  previous: null,
  results: [mockJob],
};

// Test component that uses the JobContext
function TestComponent() {
  const {
    state,
    setLoading,
    setError,
    setJobs,
    setCurrentJob,
    setFeaturedJobs,
    setRecentJobs,
    setSimilarJobs,
    appendJobs,
    clearJobs,
    resetState,
  } = useJob();

  return (
    <div>
      <div data-testid="loading">{state.isLoading.toString()}</div>
      <div data-testid="error">{state.error || 'null'}</div>
      <div data-testid="jobs-count">{state.jobs.length}</div>
      <div data-testid="total-count">{state.totalCount}</div>
      <div data-testid="current-page">{state.currentPage}</div>
      <div data-testid="has-next">{state.hasNextPage.toString()}</div>
      <div data-testid="has-previous">{state.hasPreviousPage.toString()}</div>
      <div data-testid="current-job">{state.currentJob?.title || 'null'}</div>
      <div data-testid="featured-count">{state.featuredJobs.length}</div>
      <div data-testid="recent-count">{state.recentJobs.length}</div>
      <div data-testid="similar-count">{state.similarJobs.length}</div>

      <button onClick={() => setLoading(true)} data-testid="set-loading">
        Set Loading
      </button>
      <button onClick={() => setError('Test error')} data-testid="set-error">
        Set Error
      </button>
      <button onClick={() => setJobs(mockPaginatedResponse, 1)} data-testid="set-jobs">
        Set Jobs
      </button>
      <button onClick={() => setCurrentJob(mockJob)} data-testid="set-current-job">
        Set Current Job
      </button>
      <button onClick={() => setFeaturedJobs([mockJob])} data-testid="set-featured">
        Set Featured
      </button>
      <button onClick={() => setRecentJobs([mockJob])} data-testid="set-recent">
        Set Recent
      </button>
      <button onClick={() => setSimilarJobs([mockJob])} data-testid="set-similar">
        Set Similar
      </button>
      <button onClick={() => appendJobs([mockJob])} data-testid="append-jobs">
        Append Jobs
      </button>
      <button onClick={() => clearJobs()} data-testid="clear-jobs">
        Clear Jobs
      </button>
      <button onClick={() => resetState()} data-testid="reset-state">
        Reset State
      </button>
    </div>
  );
}

function renderWithProvider() {
  return render(
    <JobProvider>
      <TestComponent />
    </JobProvider>
  );
}

describe('JobContext', () => {
  beforeEach(() => {
    // Clear any previous state
    vi.clearAllMocks();
  });

  it('should provide initial state', () => {
    renderWithProvider();

    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
    expect(screen.getByTestId('jobs-count')).toHaveTextContent('0');
    expect(screen.getByTestId('total-count')).toHaveTextContent('0');
    expect(screen.getByTestId('current-page')).toHaveTextContent('1');
    expect(screen.getByTestId('has-next')).toHaveTextContent('false');
    expect(screen.getByTestId('has-previous')).toHaveTextContent('false');
    expect(screen.getByTestId('current-job')).toHaveTextContent('null');
    expect(screen.getByTestId('featured-count')).toHaveTextContent('0');
    expect(screen.getByTestId('recent-count')).toHaveTextContent('0');
    expect(screen.getByTestId('similar-count')).toHaveTextContent('0');
  });

  it('should handle loading state', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-loading').click();
    });

    expect(screen.getByTestId('loading')).toHaveTextContent('true');
    expect(screen.getByTestId('error')).toHaveTextContent('null'); // Error should be cleared when loading
  });

  it('should handle error state', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-error').click();
    });

    expect(screen.getByTestId('error')).toHaveTextContent('Test error');
    expect(screen.getByTestId('loading')).toHaveTextContent('false'); // Loading should be false when error is set
  });

  it('should handle setting jobs', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-jobs').click();
    });

    expect(screen.getByTestId('jobs-count')).toHaveTextContent('1');
    expect(screen.getByTestId('total-count')).toHaveTextContent('10');
    expect(screen.getByTestId('current-page')).toHaveTextContent('1');
    expect(screen.getByTestId('has-next')).toHaveTextContent('true');
    expect(screen.getByTestId('has-previous')).toHaveTextContent('false');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle setting current job', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-current-job').click();
    });

    expect(screen.getByTestId('current-job')).toHaveTextContent('Software Engineer');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle setting featured jobs', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-featured').click();
    });

    expect(screen.getByTestId('featured-count')).toHaveTextContent('1');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle setting recent jobs', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-recent').click();
    });

    expect(screen.getByTestId('recent-count')).toHaveTextContent('1');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle setting similar jobs', () => {
    renderWithProvider();

    act(() => {
      screen.getByTestId('set-similar').click();
    });

    expect(screen.getByTestId('similar-count')).toHaveTextContent('1');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle appending jobs', () => {
    renderWithProvider();

    // First set some jobs
    act(() => {
      screen.getByTestId('set-jobs').click();
    });

    expect(screen.getByTestId('jobs-count')).toHaveTextContent('1');

    // Then append more jobs
    act(() => {
      screen.getByTestId('append-jobs').click();
    });

    expect(screen.getByTestId('jobs-count')).toHaveTextContent('2');
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
  });

  it('should handle clearing jobs', () => {
    renderWithProvider();

    // First set some jobs
    act(() => {
      screen.getByTestId('set-jobs').click();
    });

    expect(screen.getByTestId('jobs-count')).toHaveTextContent('1');
    expect(screen.getByTestId('total-count')).toHaveTextContent('10');

    // Then clear jobs
    act(() => {
      screen.getByTestId('clear-jobs').click();
    });

    expect(screen.getByTestId('jobs-count')).toHaveTextContent('0');
    expect(screen.getByTestId('total-count')).toHaveTextContent('0');
    expect(screen.getByTestId('current-page')).toHaveTextContent('1');
    expect(screen.getByTestId('has-next')).toHaveTextContent('false');
    expect(screen.getByTestId('has-previous')).toHaveTextContent('false');
  });

  it('should handle resetting state', () => {
    renderWithProvider();

    // Set some state - note that setting error will clear loading, and setting jobs will clear error
    act(() => {
      screen.getByTestId('set-error').click();
    });
    act(() => {
      screen.getByTestId('set-jobs').click();
    });

    // Verify state is changed (error should be null after setting jobs, but jobs should be set)
    expect(screen.getByTestId('jobs-count')).toHaveTextContent('1');
    expect(screen.getByTestId('total-count')).toHaveTextContent('10');

    // Reset state
    act(() => {
      screen.getByTestId('reset-state').click();
    });

    // Verify state is back to initial
    expect(screen.getByTestId('loading')).toHaveTextContent('false');
    expect(screen.getByTestId('error')).toHaveTextContent('null');
    expect(screen.getByTestId('jobs-count')).toHaveTextContent('0');
    expect(screen.getByTestId('total-count')).toHaveTextContent('0');
    expect(screen.getByTestId('current-page')).toHaveTextContent('1');
    expect(screen.getByTestId('has-next')).toHaveTextContent('false');
    expect(screen.getByTestId('has-previous')).toHaveTextContent('false');
    expect(screen.getByTestId('current-job')).toHaveTextContent('null');
    expect(screen.getByTestId('featured-count')).toHaveTextContent('0');
    expect(screen.getByTestId('recent-count')).toHaveTextContent('0');
    expect(screen.getByTestId('similar-count')).toHaveTextContent('0');
  });

  it('should throw error when useJob is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useJob must be used within a JobProvider');

    consoleSpy.mockRestore();
  });
});