import React, { useState } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { LoginForm } from '../components/auth/LoginForm';
import { RegisterForm } from '../components/auth/RegisterForm';
import { useUser } from '../contexts/UserContext';

export const AuthPage: React.FC = () => {
  const [isLogin, setIsLogin] = useState(true);
  const { state } = useUser();
  const location = useLocation();

  // Redirect authenticated users to their intended destination or home
  if (state.isAuthenticated) {
    const from = (location.state as any)?.from?.pathname || '/';
    return <Navigate to={from} replace />;
  }

  const handleAuthSuccess = () => {
    // Navigation will be handled by the redirect logic above
    // when the authentication state updates
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Job Board</h1>
          <p className="text-gray-600">Find your next opportunity</p>
        </div>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        {isLogin ? (
          <LoginForm
            onSuccess={handleAuthSuccess}
            onSwitchToRegister={() => setIsLogin(false)}
          />
        ) : (
          <RegisterForm
            onSuccess={handleAuthSuccess}
            onSwitchToLogin={() => setIsLogin(true)}
          />
        )}
      </div>

      <div className="mt-8 text-center">
        <p className="text-sm text-gray-600">
          By continuing, you agree to our{' '}
          <a href="/terms" className="text-blue-600 hover:text-blue-500">
            Terms of Service
          </a>{' '}
          and{' '}
          <a href="/privacy" className="text-blue-600 hover:text-blue-500">
            Privacy Policy
          </a>
        </p>
      </div>
    </div>
  );
};