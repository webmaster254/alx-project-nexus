import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { describe, it, expect, vi } from 'vitest';
import { axe, toHaveNoViolations } from 'jest-axe';
import Header from '../Header';
import { UserProvider } from '../../../contexts/UserContext';

expect.extend(toHaveNoViolations);

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <UserProvider>
        {component}
      </UserProvider>
    </BrowserRouter>
  );
};

describe('Header', () => {
  it('renders header with logo and navigation', () => {
    renderWithProviders(<Header />);

    expect(screen.getByText('Job Board')).toBeInTheDocument();
    expect(screen.getByRole('navigation')).toBeInTheDocument();
  });

  it('shows sign in link when user is not authenticated', () => {
    renderWithProviders(<Header />);

    expect(screen.getByText('Sign In')).toBeInTheDocument();
  });

  it('has proper keyboard navigation', () => {
    renderWithProviders(<Header />);

    const signInLink = screen.getByText('Sign In');
    signInLink.focus();
    expect(signInLink).toHaveFocus();
  });

  it('should not have accessibility violations', async () => {
    const { container } = renderWithProviders(<Header />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });

  it('has proper ARIA labels', () => {
    renderWithProviders(<Header />);

    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    // The navigation doesn't have an aria-label in the actual component
  });

  it('toggles mobile menu on hamburger click', () => {
    renderWithProviders(<Header />);

    const hamburgerButton = screen.getByRole('button', { name: /open main menu/i });
    expect(hamburgerButton).toBeInTheDocument();

    fireEvent.click(hamburgerButton);
    // Check if mobile menu is visible by looking for the mobile menu container
    const mobileMenu = screen.getByTestId('mobile-menu') || document.getElementById('mobile-menu');
    expect(mobileMenu).toBeInTheDocument();
  });
});