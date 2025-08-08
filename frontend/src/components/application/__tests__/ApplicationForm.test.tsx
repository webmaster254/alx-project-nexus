import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import ApplicationForm from '../ApplicationForm';
import { useUser } from '../../../contexts/UserContext';
import { applicationService } from '../../../services';
import { Job, User, UserState } from '../../../types';

// Mock the application service
vi.mock('../../../services', () => ({
  applicationService: {
    submitApplication: vi.fn(),
  },
}));

// Mock the useUser hook
vi.mock('../../../contexts/UserContext', () => ({
  useUser: vi.fn(),
}));

// Mock the step components
vi.mock('../PersonalInfoStep', () => ({
  default: ({ onNext, onCancel }: { onNext: () => void; onCancel: () => void }) => (
    <div data-testid="personal-info-step">
      <button onClick={onNext}>Next</button>
      <button onClick={onCancel}>Cancel</button>
    </div>
  ),
}));

vi.mock('../DocumentsStep', () => ({
  default: ({ onNext, onBack }: { onNext: () => void; onBack: () => void }) => (
    <div data-testid="documents-step">
      <button onClick={onNext}>Next</button>
      <button onClick={onBack}>Back</button>
    </div>
  ),
}));

vi.mock('../ReviewStep', () => ({
  default: ({ onSubmit, onBack }: { onSubmit: () => void; onBack: () => void }) => (
    <div data-testid="review-step">
      <button onClick={onSubmit}>Submit</button>
      <button onClick={onBack}>Back</button>
    </div>
  ),
}));

vi.mock('../SuccessStep', () => ({
  default: ({ onClose }: { onClose: () => void }) => (
    <div data-testid="success-step">
      <button onClick={onClose}>Close</button>
    </div>
  ),
}));

const mockJob: Job = {
  id: 1,
  title: 'Software Engineer',
  description: 'Test job description',
  summary: 'Test summary',
  location: 'San Francisco, CA',
  is_remote: false,
  salary_min: 80000,
  salary_max: 120000,
  salary_type: 'yearly',
  salary_currency: '$',
  experience_level: 'mid',
  required_skills: 'JavaScript, React',
  preferred_skills: 'TypeScript',
  application_deadline: null,
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
    location: 'San Francisco, CA',
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
  salary_display: '$80,000 - $120,000 yearly',
  days_since_posted: '1 day ago',
  is_new: true,
  is_urgent: false,
  can_apply: true,
};

const mockUser: User = {
  id: 1,
  email: 'test@example.com',
  first_name: 'John',
  last_name: 'Doe',
  is_active: true,
  date_joined: '2024-01-01T00:00:00Z',
  profile: {
    phone: '+1234567890',
    location: 'San Francisco, CA',
    bio: 'Software engineer',
    experience_years: 5,
    skills: ['JavaScript', 'React'],
    resume_url: 'https://example.com/resume.pdf',
  },
};

const mockUserState: UserState = {
  user: mockUser,
  isAuthenticated: true,
  isLoading: false,
  error: null,
  token: 'mock-token',
};

const mockUserContextValue = {
  state: mockUserState,
  login: vi.fn(),
  logout: vi.fn(),
  register: vi.fn(),
  updateProfile: vi.fn(),
  clearError: vi.fn(),
};

const renderApplicationForm = (userState: UserState = mockUserState, props = {}) => {
  const mockUseUser = vi.mocked(useUser);
  mockUseUser.mockReturnValue({
    state: userState,
    ...mockUserContextValue,
  });

  return render(
    <ApplicationForm
      job={mockJob}
      onClose={vi.fn()}
      onSuccess={vi.fn()}
      {...props}
    />
  );
};

describe('ApplicationForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders the application form with job information', () => {
    renderApplicationForm();

    expect(screen.getByText('Apply for Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('Tech Corp • San Francisco, CA')).toBeInTheDocument();
    expect(screen.getByText('Personal Information')).toBeInTheDocument();
  });

  it('shows progress steps', () => {
    renderApplicationForm();

    // Check that step indicators are present
    expect(screen.getByText('1')).toBeInTheDocument();
    expect(screen.getByText('2')).toBeInTheDocument();
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('starts with personal info step', () => {
    renderApplicationForm();

    expect(screen.getByTestId('personal-info-step')).toBeInTheDocument();
    expect(screen.queryByTestId('documents-step')).not.toBeInTheDocument();
    expect(screen.queryByTestId('review-step')).not.toBeInTheDocument();
    expect(screen.queryByTestId('success-step')).not.toBeInTheDocument();
  });

  it('navigates through steps correctly', async () => {
    renderApplicationForm();

    // Start with personal info step
    expect(screen.getByTestId('personal-info-step')).toBeInTheDocument();

    // Click next to go to documents step
    fireEvent.click(screen.getByText('Next'));
    await waitFor(() => {
      expect(screen.getByTestId('documents-step')).toBeInTheDocument();
    });

    // Click next to go to review step
    fireEvent.click(screen.getByText('Next'));
    await waitFor(() => {
      expect(screen.getByTestId('review-step')).toBeInTheDocument();
    });

    // Click back to go to documents step
    fireEvent.click(screen.getByText('Back'));
    await waitFor(() => {
      expect(screen.getByTestId('documents-step')).toBeInTheDocument();
    });
  });

  it('handles application submission successfully', async () => {
    const mockSubmitApplication = vi.mocked(applicationService.submitApplication);
    mockSubmitApplication.mockResolvedValue({
      id: 1,
      job: 1,
      user: 1,
      cover_letter: 'Test cover letter',
      status: 'pending',
      applied_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      documents: [],
    });

    const onSuccess = vi.fn();
    renderApplicationForm(mockUserState, { onSuccess });

    // Navigate to review step
    fireEvent.click(screen.getByText('Next')); // Personal -> Documents
    await waitFor(() => screen.getByTestId('documents-step'));
    
    fireEvent.click(screen.getByText('Next')); // Documents -> Review
    await waitFor(() => screen.getByTestId('review-step'));

    // Submit application
    fireEvent.click(screen.getByText('Submit'));

    await waitFor(() => {
      expect(screen.getByTestId('success-step')).toBeInTheDocument();
    });

    expect(mockSubmitApplication).toHaveBeenCalledWith({
      job: 1,
      cover_letter: '',
      documents: [],
    });
    expect(onSuccess).toHaveBeenCalled();
  });

  it('handles application submission error', async () => {
    const mockSubmitApplication = vi.mocked(applicationService.submitApplication);
    mockSubmitApplication.mockRejectedValue(new Error('Submission failed'));

    renderApplicationForm();

    // Navigate to review step
    fireEvent.click(screen.getByText('Next')); // Personal -> Documents
    await waitFor(() => screen.getByTestId('documents-step'));
    
    fireEvent.click(screen.getByText('Next')); // Documents -> Review
    await waitFor(() => screen.getByTestId('review-step'));

    // Submit application
    fireEvent.click(screen.getByText('Submit'));

    // Should stay on review step and not show success step
    await waitFor(() => {
      expect(screen.getByTestId('review-step')).toBeInTheDocument();
    });
    expect(screen.queryByTestId('success-step')).not.toBeInTheDocument();
  });

  it('calls onClose when close button is clicked', () => {
    const onClose = vi.fn();
    renderApplicationForm(mockUserState, { onClose });

    fireEvent.click(screen.getByLabelText('Close application form'));
    expect(onClose).toHaveBeenCalled();
  });

  it('calls onClose when cancel is clicked in personal info step', () => {
    const onClose = vi.fn();
    renderApplicationForm(mockUserState, { onClose });

    fireEvent.click(screen.getByText('Cancel'));
    expect(onClose).toHaveBeenCalled();
  });

  it('hides progress steps on success step', async () => {
    const mockSubmitApplication = vi.mocked(applicationService.submitApplication);
    mockSubmitApplication.mockResolvedValue({
      id: 1,
      job: 1,
      user: 1,
      cover_letter: 'Test cover letter',
      status: 'pending',
      applied_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      documents: [],
    });

    renderApplicationForm();

    // Navigate to review and submit
    fireEvent.click(screen.getByText('Next')); // Personal -> Documents
    await waitFor(() => screen.getByTestId('documents-step'));
    
    fireEvent.click(screen.getByText('Next')); // Documents -> Review
    await waitFor(() => screen.getByTestId('review-step'));
    
    fireEvent.click(screen.getByText('Submit')); // Submit
    await waitFor(() => screen.getByTestId('success-step'));

    // Progress steps should not be visible
    expect(screen.queryByText('Personal Information')).not.toBeInTheDocument();
  });
});