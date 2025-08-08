import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import JobCard from '../JobCard';
import { Job } from '../../../types';

// Helper function to render with Router
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

const mockJob: Job = {
  id: 1,
  title: 'Senior Software Engineer',
  description: 'We are looking for a senior software engineer...',
  summary: 'Senior role for experienced developer',
  location: 'San Francisco, CA',
  is_remote: true,
  salary_min: 120000,
  salary_max: 180000,
  salary_type: 'yearly',
  salary_currency: '$',
  experience_level: 'senior',
  required_skills: 'React, TypeScript, Node.js',
  preferred_skills: 'AWS, Docker',
  application_deadline: '2024-12-31',
  external_url: null,
  is_active: true,
  is_featured: true,
  views_count: 150,
  applications_count: 25,
  created_at: '2024-01-15T10:00:00Z',
  updated_at: '2024-01-15T10:00:00Z',
  company: {
    id: 1,
    name: 'TechCorp Inc.',
    description: 'Leading tech company',
    website: 'https://techcorp.com',
    logo: null,
    size: '100-500',
    industry: 'Technology',
    location: 'San Francisco, CA'
  },
  industry: {
    id: 1,
    name: 'Technology',
    description: 'Technology industry'
  },
  job_type: {
    id: 1,
    name: 'Full-time',
    description: 'Full-time position'
  },
  categories: [
    {
      id: 1,
      name: 'Engineering',
      description: 'Software engineering roles'
    },
    {
      id: 2,
      name: 'Frontend',
      description: 'Frontend development'
    }
  ],
  salary_display: '$120,000 - $180,000 yearly',
  days_since_posted: '2 days ago',
  is_new: true,
  is_urgent: false,
  can_apply: true
};

describe('JobCard', () => {
  it('renders job information correctly', () => {
    renderWithRouter(<JobCard job={mockJob} />);

    expect(screen.getByText('Senior Software Engineer')).toBeInTheDocument();
    expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    expect(screen.getByText('$120,000 - $180,000 yearly')).toBeInTheDocument();
    expect(screen.getByText('Senior')).toBeInTheDocument();
    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('Frontend')).toBeInTheDocument();
    expect(screen.getByText('2 days ago')).toBeInTheDocument();
    expect(screen.getByText('25 applications')).toBeInTheDocument();
  });

  it('displays badges correctly', () => {
    renderWithRouter(<JobCard job={mockJob} />);

    expect(screen.getByText('New')).toBeInTheDocument();
    expect(screen.getByText('Featured')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  it('handles click events', () => {
    const handleClick = vi.fn();
    renderWithRouter(<JobCard job={mockJob} onClick={handleClick} />);

    const card = screen.getByRole('button');
    fireEvent.click(card);

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('handles keyboard events', () => {
    const handleClick = vi.fn();
    renderWithRouter(<JobCard job={mockJob} onClick={handleClick} />);

    const card = screen.getByRole('button');
    fireEvent.keyDown(card, { key: 'Enter' });

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('displays company logo placeholder when no logo provided', () => {
    renderWithRouter(<JobCard job={mockJob} />);

    const logoPlaceholder = screen.getByText('T'); // First letter of TechCorp
    expect(logoPlaceholder).toBeInTheDocument();
  });

  it('handles job without salary information', () => {
    const jobWithoutSalary = {
      ...mockJob,
      salary_min: undefined,
      salary_max: undefined
    };

    renderWithRouter(<JobCard job={jobWithoutSalary} />);

    expect(screen.queryByText('$120,000 - $180,000 yearly')).not.toBeInTheDocument();
  });

  it('shows correct experience level display', () => {
    const entryLevelJob = {
      ...mockJob,
      experience_level: 'entry' as const
    };

    renderWithRouter(<JobCard job={entryLevelJob} />);

    expect(screen.getByText('Entry Level')).toBeInTheDocument();
  });

  it('limits category display and shows more indicator', () => {
    const jobWithManyCategories = {
      ...mockJob,
      categories: [
        { id: 1, name: 'Engineering' },
        { id: 2, name: 'Frontend' },
        { id: 3, name: 'React' },
        { id: 4, name: 'TypeScript' }
      ]
    };

    renderWithRouter(<JobCard job={jobWithManyCategories} />);

    expect(screen.getByText('Engineering')).toBeInTheDocument();
    expect(screen.getByText('Frontend')).toBeInTheDocument();
    expect(screen.getByText('+2 more')).toBeInTheDocument();
  });
});