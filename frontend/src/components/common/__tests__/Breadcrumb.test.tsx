import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect } from 'vitest';
import Breadcrumb, { BreadcrumbItem } from '../Breadcrumb';

// Helper function to render with Router
const renderWithRouter = (component: React.ReactElement) => {
  return render(<BrowserRouter>{component}</BrowserRouter>);
};

describe('Breadcrumb', () => {
  it('renders breadcrumb items correctly', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'Jobs', href: '/jobs' },
      { label: 'Job Details', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.getByText('Jobs')).toBeInTheDocument();
    expect(screen.getByText('Job Details')).toBeInTheDocument();
  });

  it('renders links for non-current items', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'Jobs', href: '/jobs' },
      { label: 'Job Details', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    const homeLink = screen.getByRole('link', { name: 'Home' });
    const jobsLink = screen.getByRole('link', { name: 'Jobs' });

    expect(homeLink).toHaveAttribute('href', '/');
    expect(jobsLink).toHaveAttribute('href', '/jobs');
  });

  it('does not render link for current item', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'Job Details', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    const homeLink = screen.getByRole('link', { name: 'Home' });
    expect(homeLink).toBeInTheDocument();

    // Current item should not be a link
    expect(screen.queryByRole('link', { name: 'Job Details' })).not.toBeInTheDocument();
    expect(screen.getByText('Job Details')).toBeInTheDocument();
  });

  it('renders separators between items', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'Jobs', href: '/jobs' },
      { label: 'Job Details', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    const separators = screen.getAllByText('/');
    expect(separators).toHaveLength(2); // Two separators for three items
  });

  it('applies custom className', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' }
    ];

    const { container } = renderWithRouter(<Breadcrumb items={items} className="custom-class" />);

    const nav = container.querySelector('nav');
    expect(nav).toHaveClass('custom-class');
  });

  it('sets aria-current for current item', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'Job Details', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    const currentItem = screen.getByText('Job Details');
    expect(currentItem).toHaveAttribute('aria-current', 'page');
  });

  it('truncates long labels with title attribute', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', href: '/' },
      { label: 'This is a very long job title that should be truncated', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    const longLabel = screen.getByText('This is a very long job title that should be truncated');
    expect(longLabel).toHaveAttribute('title', 'This is a very long job title that should be truncated');
    expect(longLabel).toHaveClass('truncate', 'max-w-xs');
  });

  it('handles single item breadcrumb', () => {
    const items: BreadcrumbItem[] = [
      { label: 'Home', current: true }
    ];

    renderWithRouter(<Breadcrumb items={items} />);

    expect(screen.getByText('Home')).toBeInTheDocument();
    expect(screen.queryByText('/')).not.toBeInTheDocument(); // No separator for single item
  });

  it('handles empty items array', () => {
    const items: BreadcrumbItem[] = [];

    renderWithRouter(<Breadcrumb items={items} />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    expect(nav.querySelector('ol')).toBeEmptyDOMElement();
  });
});