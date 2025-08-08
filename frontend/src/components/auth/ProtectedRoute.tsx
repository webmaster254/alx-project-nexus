import React, { ReactNode } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';

interface ProtectedRouteProps {
  children: ReactNode;
  redirectTo?: string;
  requireAuth?: boolean;
}

/**
 * ProtectedRoute component that handles authentication-based routing
 * 
 * @param children - The component(s) to render if access is allowed
 * @param redirectTo - Where to redirect if access is denied (default: '/login')
 * @param requireAuth - Whether authentication is required (default: true)
 */
export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  redirectTo = '/login',
  requireAuth = true,
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