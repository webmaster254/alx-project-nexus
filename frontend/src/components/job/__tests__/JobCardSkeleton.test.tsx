import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import JobCardSkeleton from '../JobCardSkeleton';

describe('JobCardSkeleton', () => {
  it('renders skeleton loading state', () => {
    const { container } = render(<JobCardSkeleton />);

    // Check that the skeleton has the animate-pulse class
    const skeletonCard = container.querySelector('.animate-pulse');
    expect(skeletonCard).toBeInTheDocument();

    // Check that skeleton elements are present
    const skeletonElements = container.querySelectorAll('.bg-gray-200');
    expect(skeletonElements.length).toBeGreaterThan(0);
  });

  it('has proper structure matching JobCard layout', () => {
    const { container } = render(<JobCardSkeleton />);

    // Check for main card container
    const cardContainer = container.querySelector('.bg-white.rounded-lg.shadow-md');
    expect(cardContainer).toBeInTheDocument();

    // Check for skeleton elements in different sections
    const skeletonElements = container.querySelectorAll('.bg-gray-200');
    
    // Should have multiple skeleton elements for different parts of the card
    expect(skeletonElements.length).toBeGreaterThan(5);
  });
});