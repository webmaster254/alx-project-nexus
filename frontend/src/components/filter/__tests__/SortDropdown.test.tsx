import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import SortDropdown from '../SortDropdown';

expect.extend(toHaveNoViolations);

// Mock the useResponsive hook
vi.mock('../../../hooks', () => ({
  useResponsive: () => ({ isMobile: false }),
}));

describe('SortDropdown', () => {
  const mockOnChange = vi.fn();
  const mockOptions = [
    { value: 'created_at', label: 'Most Recent' },
    { value: 'relevance', label: 'Most Relevant' },
    { value: 'title', label: 'Title: A to Z' },
    { value: '-title', label: 'Title: Z to A' },
    { value: '-salary_max', label: 'Salary: High to Low' },
    { value: 'salary_min', label: 'Salary: Low to High' },
  ];

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders sort dropdown with default option', () => {
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('Most Recent')).toBeInTheDocument();
  });

  it('renders with custom selected value', () => {
    render(
      <SortDropdown
        options={mockOptions}
        value="-salary_max"
        onChange={mockOnChange}
      />
    );

    expect(screen.getByText('Salary: High to Low')).toBeInTheDocument();
  });

  it('opens dropdown when button is clicked', async () => {
    const user = userEvent.setup();
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    expect(screen.getByRole('listbox')).toBeInTheDocument();
    expect(screen.getByText('Title: A to Z')).toBeInTheDocument();
  });

  it('calls onChange when option is selected', async () => {
    const user = userEvent.setup();
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    const option = screen.getByText('Title: A to Z');
    await user.click(option);

    expect(mockOnChange).toHaveBeenCalledWith('title');
  });

  it('has all sort options available when opened', async () => {
    const user = userEvent.setup();
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button');
    await user.click(button);

    const options = screen.getAllByRole('option');
    expect(options).toHaveLength(6);
    expect(screen.getByText('Most Recent')).toBeInTheDocument();
    expect(screen.getByText('Most Relevant')).toBeInTheDocument();
    expect(screen.getByText('Title: A to Z')).toBeInTheDocument();
    expect(screen.getByText('Title: Z to A')).toBeInTheDocument();
    expect(screen.getByText('Salary: High to Low')).toBeInTheDocument();
    expect(screen.getByText('Salary: Low to High')).toBeInTheDocument();
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper ARIA attributes', () => {
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button');
    expect(button).toHaveAttribute('aria-haspopup', 'listbox');
    expect(button).toHaveAttribute('aria-expanded', 'false');
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
      />
    );

    const button = screen.getByRole('button');
    button.focus();
    expect(button).toHaveFocus();

    await user.keyboard('{Enter}');
    expect(screen.getByRole('listbox')).toBeInTheDocument();

    await user.keyboard('{Escape}');
    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('closes dropdown when clicking outside', async () => {
    const user = userEvent.setup();
    render(
      <div>
        <SortDropdown
          options={mockOptions}
          value="created_at"
          onChange={mockOnChange}
        />
        <div data-testid="outside">Outside element</div>
      </div>
    );

    const button = screen.getByRole('button');
    await user.click(button);

    expect(screen.getByRole('listbox')).toBeInTheDocument();

    const outsideElement = screen.getByTestId('outside');
    await user.click(outsideElement);

    expect(screen.queryByRole('listbox')).not.toBeInTheDocument();
  });

  it('applies custom className', () => {
    const customClass = 'custom-sort-class';
    render(
      <SortDropdown
        options={mockOptions}
        value="created_at"
        onChange={mockOnChange}
        className={customClass}
      />
    );

    const container = screen.getByRole('button').parentElement;
    expect(container).toHaveClass(customClass);
  });
});