import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import LoadingSpinner from '../LoadingSpinner';

expect.extend(toHaveNoViolations);

describe('LoadingSpinner', () => {
  it('renders loading spinner with default props', () => {
    render(<LoadingSpinner />);

    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Loading');
  });

  it('renders with custom size', () => {
    render(<LoadingSpinner size="large" />);

    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-12', 'h-12');
  });

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Loading jobs..." />);

    expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
  });

  it('renders with custom aria-label', () => {
    render(<LoadingSpinner ariaLabel="Loading job listings" />);

    const spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Loading job listings');
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(<LoadingSpinner />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper ARIA attributes for screen readers', () => {
    render(<LoadingSpinner />);

    const spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-live', 'polite');
    expect(spinner).toHaveAttribute('aria-busy', 'true');
  });
});