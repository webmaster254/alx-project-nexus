import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage, JobDetailPage, AuthPage, ProfilePage } from './pages';
import { ProtectedRoute } from './components/auth';
import { JobProvider } from './contexts/JobContext';
import { FilterProvider } from './contexts/FilterContext';
import { UserProvider } from './contexts/UserContext';

const App: React.FC = () => {
  return (
    <Router>
      <UserProvider>
        <FilterProvider>
          <JobProvider>
            <div className="min-h-screen bg-gray-50">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/jobs/:id" element={<JobDetailPage />} />
                <Route 
                  path="/login" 
                  element={
                    <ProtectedRoute requireAuth={false}>
                      <AuthPage />
                    </ProtectedRoute>
                  } 
                />
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute>
                      <ProfilePage />
                    </ProtectedRoute>
                  } 
                />
              </Routes>
            </div>
          </JobProvider>
        </FilterProvider>
      </UserProvider>
    </Router>
  );
};

export default App;
