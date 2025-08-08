import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import { BrowserRouter } from 'react-router-dom';
import { ProtectedRoute } from '../ProtectedRoute';

// Mock the UserContext
const mockUserState = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,
  token: null,
};

const mockUseUser = vi.fn(() => ({ state: mockUserState }));

vi.mock('../../../contexts/UserContext', () => ({
  useUser: () => mockUseUser(),
}));

// Mock react-router-dom Navigate component
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    Navigate: ({ to, state, replace }: any) => {
      mockNavigate(to, state, replace);
      return <div data-testid="navigate">Redirecting to {to}</div>;
    },
    useLocation: () => ({ pathname: '/protected' }),
  };
});

describe('ProtectedRoute', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderProtectedRoute = (props = {}) => {
    const defaultProps = {
      children: <div data-testid="protected-content">Protected Content</div>,
      ...props,
    };

    return render(
      <BrowserRouter>
        <ProtectedRoute {...defaultProps} />
      </BrowserRouter>
    );
  };

  it('shows loading state when authentication is being checked', () => {
    mockUseUser.mockReturnValue({
      state: { ...mockUserState, isLoading: true },
    });

    renderProtectedRoute();

    expect(screen.getByText(/loading/i)).toBeInTheDocument();
    expect(screen.queryByTestId('protected-content')).not.toBeInTheDocument();
  });

  it('redirects to login when user is not authenticated and auth is required', () => {
    mockUseUser.mockReturnValue({
      state: { ...mockUserState, isAuthenticated: false },
    });

    renderProtectedRoute({ requireAuth: true });

    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByText(/redirecting to \/login/i)).toBeInTheDocument();
    expect(mockNavigate).toHaveBeenCalledWith('/login', { from: { pathname: '/protected' } }, true);
  });

  it('redirects to custom path when specified', () => {
    mockUseUser.mockReturnValue({
      state: { ...mockUserState, isAuthenticated: false },
    });

    renderProtectedRoute({ requireAuth: true, redirectTo: '/custom-login' });

    expect(screen.getByText(/redirecting to \/custom-login/i)).toBeInTheDocument();
    expect(mockNavigate).toHaveBeenCalledWith('/custom-login', { from: { pathname: '/protected' } }, true);
  });

  it('renders children when user is authenticated and auth is required', () => {
    mockUseUser.mockReturnValue({
      state: { 
        ...mockUserState, 
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', first_name: 'John', last_name: 'Doe' }
      },
    });

    renderProtectedRoute({ requireAuth: true });

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.queryByTestId('navigate')).not.toBeInTheDocument();
  });

  it('redirects authenticated users when auth is not required', () => {
    mockUseUser.mockReturnValue({
      state: { 
        ...mockUserState, 
        isAuthenticated: true,
        user: { id: 1, email: 'test@example.com', first_name: 'John', last_name: 'Doe' }
      },
    });

    renderProtectedRoute({ requireAuth: false });

    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(screen.getByText(/redirecting to \//i)).toBeInTheDocument();
    expect(mockNavigate).toHaveBeenCalledWith('/', undefined, true);
  });

  it('renders children when user is not authenticated and auth is not required', () => {
    mockUseUser.mockReturnValue({
      state: { ...mockUserState, isAuthenticated: false },
    });

    renderProtectedRoute({ requireAuth: false });

    expect(screen.getByTestId('protected-content')).toBeInTheDocument();
    expect(screen.queryByTestId('navigate')).not.toBeInTheDocument();
  });

  it('uses default requireAuth value of true', () => {
    mockUseUser.mockReturnValue({
      state: { ...mockUserState, isAuthenticated: false },
    });

    renderProtectedRoute(); // No requireAuth prop

    expect(screen.getByTestId('navigate')).toBeInTheDocument();
    expect(mockNavigate).toHaveBeenCalledWith('/login', { from: { pathname: '/protected' } }, true);
  });
});