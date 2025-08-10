import React, { Suspense, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ProtectedRoute } from './components/auth';
import { JobProvider } from './contexts/JobContext';
import { FilterProvider } from './contexts/FilterContext';
import { BookmarkProvider } from './contexts/BookmarkContext';
import { UserProvider } from './contexts/UserContext';
import { Header, Footer, ErrorBoundary, OfflineIndicator, OfflineBanner, BottomNavigation, LoadingSpinner, PerformanceMonitor } from './components/common';
import { performanceService } from './services';

// Lazy load pages for code splitting
const HomePage = React.lazy(() => import('./pages/HomePage'));
const JobListingPage = React.lazy(() => import('./pages/JobListingPage'));
const JobDetailPage = React.lazy(() => import('./pages/JobDetailPage'));
const AboutPage = React.lazy(() => import('./pages/AboutPage'));
const ContactPage = React.lazy(() => import('./pages/ContactPage'));
const AuthPage = React.lazy(() => import('./pages/AuthPage'));
const ProfilePage = React.lazy(() => import('./pages/ProfilePage'));
const AdminDashboardPage = React.lazy(() => import('./pages/AdminDashboardPage'));
const ApplicationsPage = React.lazy(() => import('./pages/ApplicationsPage'));

const App: React.FC = () => {
  useEffect(() => {
    // Initialize performance tracking
    performanceService.trackUserTiming('app-start');
    
    // Track app initialization time
    const initStart = performance.now();
    
    const handleLoad = () => {
      const initTime = performance.now() - initStart;
      performanceService.trackCustomMetric('app-initialization', initTime);
      performanceService.measureUserTiming('app-ready', 'app-start');
    };

    // Track when the app is fully loaded
    if (document.readyState === 'complete') {
      handleLoad();
    } else {
      window.addEventListener('load', handleLoad);
      return () => window.removeEventListener('load', handleLoad);
    }
  }, []);

  return (
    <ErrorBoundary>
      <Router>
        <UserProvider>
          <BookmarkProvider>
            <FilterProvider>
              <JobProvider>
              <div className="min-h-screen bg-gray-50 pb-16 md:pb-0">
                <OfflineBanner />
                <OfflineIndicator />
                <Header />
                <Suspense fallback={
                  <div className="flex justify-center items-center min-h-[50vh]">
                    <LoadingSpinner size="lg" />
                  </div>
                }>
                  <Routes>
                    <Route path="/" element={<HomePage />} />
                    <Route path="/jobs" element={<JobListingPage />} />
                    <Route path="/jobs/:id" element={<JobDetailPage />} />
                    <Route path="/about" element={<AboutPage />} />
                    <Route path="/contact" element={<ContactPage />} />
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
                    <Route 
                      path="/applications" 
                      element={
                        <ProtectedRoute>
                          <ApplicationsPage />
                        </ProtectedRoute>
                      } 
                    />
                    <Route 
                      path="/admin" 
                      element={
                        <ProtectedRoute requireAdmin={true}>
                          <AdminDashboardPage />
                        </ProtectedRoute>
                      } 
                    />
                  </Routes>
                </Suspense>
                <Footer />
                <BottomNavigation />
                <PerformanceMonitor />
              </div>
              </JobProvider>
            </FilterProvider>
          </BookmarkProvider>
        </UserProvider>
      </Router>
    </ErrorBoundary>
  );
};

export default App;
