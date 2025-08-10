import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
  requireAuth?: boolean;
  requireAdmin?: boolean;
}

/**
 * ProtectedRoute component that handles authentication-based routing
 * 
 * @param children - The component(s) to render if access is allowed
 * @param redirectTo - Where to redirect if access is denied (default: '/login')
 * @param requireAuth - Whether authentication is required (default: true)
 * @param requireAdmin - Whether admin role is required (default: false)
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/login',
  requireAuth = true,
  requireAdmin = false,
}) => {
  const { state } = useUser();
  const location = useLocation();

  // Show loading state while authentication is being checked
  if (state.isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Check authentication requirement
  if (requireAuth && !state.isAuthenticated) {
    // Save the attempted location for redirect after login
    return (
      <Navigate 
        to={redirectTo} 
        state={{ from: location }} 
        replace 
      />
    );
  }

  // Check admin role requirement
  if (requireAdmin && (!state.isAuthenticated || !state.user?.is_staff)) {
    // Debug logging for admin access issues
    console.log('Admin access check failed:', {
      requireAdmin,
      isAuthenticated: state.isAuthenticated,
      user: state.user,
      is_staff: state.user?.is_staff,
      userKeys: state.user ? Object.keys(state.user) : 'No user'
    });
    
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center max-w-md mx-auto p-8">
          <div className="mb-4">
            <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Access Denied</h1>
          <p className="text-gray-600 mb-6">
            You don't have permission to access this page. Admin privileges are required.
          </p>
          <div className="mb-4 text-xs text-gray-500 bg-gray-100 p-2 rounded">
            Debug: isAuthenticated={String(state.isAuthenticated)}, is_staff={String(state.user?.is_staff)}
          </div>
          <button
            onClick={() => window.history.back()}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  // If requireAuth is false and user is authenticated, redirect to dashboard/home
  if (!requireAuth && state.isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  // Render children if all checks pass
  return <>{children}</>;
};

/**
 * Hook to check if current route requires authentication
 */
export const useAuthRequired = () => {
  const { state } = useUser();
  return {
    isAuthenticated: state.isAuthenticated,
    isLoading: state.isLoading,
    user: state.user,
  };
};