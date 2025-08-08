import React from 'react';
import { UserProfile } from '../components/auth/UserProfile';
import { useUser } from '../contexts/UserContext';

export const ProfilePage: React.FC = () => {
  const { state, logout } = useUser();

  const handleLogout = async () => {
    await logout();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Profile</h1>
              {state.user && (
                <p className="text-gray-600 mt-1">
                  Welcome back, {state.user.first_name} {state.user.last_name}
                </p>
              )}
            </div>
            <div className="flex items-center space-x-4">
              <a
                href="/"
                className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
              >
                Back to Jobs
              </a>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
              >
                Sign Out
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="py-8">
        <UserProfile />
      </main>
    </div>
  );
};