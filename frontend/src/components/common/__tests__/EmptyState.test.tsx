import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import EmptyState from '../EmptyState';

expect.extend(toHaveNoViolations);

describe('EmptyState', () => {
  it('renders with title and description', () => {
    render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
      />
    );

    expect(screen.getByText('No jobs found')).toBeInTheDocument();
    expect(screen.getByText('Try adjusting your search criteria')).toBeInTheDocument();
  });

  it('renders with action button', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
        actionText="Clear filters"
        onAction={handleAction}
      />
    );

    const actionButton = screen.getByRole('button', { name: 'Clear filters' });
    expect(actionButton).toBeInTheDocument();

    fireEvent.click(actionButton);
    expect(handleAction).toHaveBeenCalledTimes(1);
  });

  it('renders with custom icon', () => {
    const CustomIcon = () => <div data-testid="custom-icon">Custom Icon</div>;
    render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
        icon={<CustomIcon />}
      />
    );

    expect(screen.getByTestId('custom-icon')).toBeInTheDocument();
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper heading structure', () => {
    render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
      />
    );

    const heading = screen.getByRole('heading', { level: 2 });
    expect(heading).toHaveTextContent('No jobs found');
  });

  it('handles keyboard navigation for action button', () => {
    const handleAction = vi.fn();
    render(
      <EmptyState
        title="No jobs found"
        description="Try adjusting your search criteria"
        actionText="Clear filters"
        onAction={handleAction}
      />
    );

    const actionButton = screen.getByRole('button', { name: 'Clear filters' });
    fireEvent.keyDown(actionButton, { key: 'Enter' });
    expect(handleAction).toHaveBeenCalledTimes(1);

    fireEvent.keyDown(actionButton, { key: ' ' });
    expect(handleAction).toHaveBeenCalledTimes(2);
  });
});