import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import PersonalInfoStep from '../PersonalInfoStep';

expect.extend(toHaveNoViolations);

describe('PersonalInfoStep', () => {
  const mockOnNext = vi.fn();
  const mockOnDataChange = vi.fn();

  const defaultData = {
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    coverLetter: '',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders personal info form fields', () => {
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    expect(screen.getByLabelText(/first name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/last name/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/cover letter/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /next/i })).toBeInTheDocument();
  });

  it('displays pre-filled data', () => {
    const filledData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      phone: '+1234567890',
      coverLetter: 'I am interested in this position...',
    };

    render(
      <PersonalInfoStep
        data={filledData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    expect(screen.getByDisplayValue('John')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Doe')).toBeInTheDocument();
    expect(screen.getByDisplayValue('john.doe@example.com')).toBeInTheDocument();
    expect(screen.getByDisplayValue('+1234567890')).toBeInTheDocument();
    expect(screen.getByDisplayValue('I am interested in this position...')).toBeInTheDocument();
  });

  it('validates required fields', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/first name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/last name is required/i)).toBeInTheDocument();
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
    });

    expect(mockOnNext).not.toHaveBeenCalled();
  });

  it('validates email format', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const emailInput = screen.getByLabelText(/email/i);
    await user.type(emailInput, 'invalid-email');

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid email/i)).toBeInTheDocument();
    });
  });

  it('validates phone number format', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const phoneInput = screen.getByLabelText(/phone/i);
    await user.type(phoneInput, '123');

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/please enter a valid phone number/i)).toBeInTheDocument();
    });
  });

  it('calls onDataChange when fields are updated', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const firstNameInput = screen.getByLabelText(/first name/i);
    await user.type(firstNameInput, 'John');

    expect(mockOnDataChange).toHaveBeenCalledWith({
      ...defaultData,
      firstName: 'John',
    });
  });

  it('calls onNext with valid data', async () => {
    const user = userEvent.setup();
    const validData = {
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@example.com',
      phone: '+1234567890',
      coverLetter: 'I am interested in this position...',
    };

    render(
      <PersonalInfoStep
        data={validData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(mockOnNext).toHaveBeenCalledWith(validData);
    });
  });

  it('should not have accessibility violations', async () => {
    const { container } = render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper form labels and associations', () => {
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const firstNameInput = screen.getByLabelText(/first name/i);
    const lastNameInput = screen.getByLabelText(/last name/i);
    const emailInput = screen.getByLabelText(/email/i);
    const phoneInput = screen.getByLabelText(/phone/i);
    const coverLetterInput = screen.getByLabelText(/cover letter/i);

    expect(firstNameInput).toHaveAttribute('type', 'text');
    expect(lastNameInput).toHaveAttribute('type', 'text');
    expect(emailInput).toHaveAttribute('type', 'email');
    expect(phoneInput).toHaveAttribute('type', 'tel');
    expect(coverLetterInput.tagName).toBe('TEXTAREA');
  });

  it('handles keyboard navigation', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    await user.tab();
    expect(screen.getByLabelText(/first name/i)).toHaveFocus();

    await user.tab();
    expect(screen.getByLabelText(/last name/i)).toHaveFocus();

    await user.tab();
    expect(screen.getByLabelText(/email/i)).toHaveFocus();
  });

  it('shows character count for cover letter', () => {
    const dataWithCoverLetter = {
      ...defaultData,
      coverLetter: 'This is a test cover letter.',
    };

    render(
      <PersonalInfoStep
        data={dataWithCoverLetter}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    expect(screen.getByText(/28 \/ 1000 characters/i)).toBeInTheDocument();
  });

  it('announces validation errors to screen readers', async () => {
    const user = userEvent.setup();
    render(
      <PersonalInfoStep
        data={defaultData}
        onNext={mockOnNext}
        onDataChange={mockOnDataChange}
      />
    );

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      const errorMessages = screen.getAllByRole('alert');
      expect(errorMessages.length).toBeGreaterThan(0);
    });
  });
});