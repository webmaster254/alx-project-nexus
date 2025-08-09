import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { useResponsive, useSwipeGesture } from '../../hooks';

const Header: React.FC = () => {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { state: userState, logout } = useUser();
  const location = useLocation();
  const navigate = useNavigate();
  const { isMobile } = useResponsive();

  // Swipe gesture for mobile menu
  const { attachSwipeListeners } = useSwipeGesture({
    onSwipeLeft: () => {
      if (isMobile && isMobileMenuOpen) {
        setIsMobileMenuOpen(false);
      }
    },
    threshold: 50,
  });

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);

  // Close mobile menu on escape key and attach swipe listeners
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setIsMobileMenuOpen(false);
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('keydown', handleEscape);
      // Prevent body scroll when mobile menu is open
      document.body.style.overflow = 'hidden';
      
      // Attach swipe listeners to mobile menu
      const mobileMenu = document.getElementById('mobile-menu');
      if (mobileMenu && isMobile) {
        const cleanup = attachSwipeListeners(mobileMenu);
        return () => {
          document.removeEventListener('keydown', handleEscape);
          document.body.style.overflow = 'unset';
          cleanup?.();
        };
      }
    } else {
      document.body.style.overflow = 'unset';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isMobileMenuOpen, isMobile, attachSwipeListeners]);

  const handleLogout = async () => {
    try {
      await logout();
      navigate('/');
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const navigation = [
    { name: 'Jobs', href: '/', current: location.pathname === '/' },
    ...(userState.isAuthenticated 
      ? [{ name: 'Profile', href: '/profile', current: location.pathname === '/profile' }]
      : []
    ),
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <div className="flex items-center">
            <Link 
              to="/" 
              className="flex items-center space-x-2 text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors duration-200"
              aria-label="Job Board Home"
            >
              <svg 
                className="w-8 h-8 text-blue-600" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
                aria-hidden="true"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6.5M16 6H8m0 0v-.5A2.5 2.5 0 0110.5 3h3A2.5 2.5 0 0116 5.5V6H8z" 
                />
              </svg>
              <span>Job Board</span>
            </Link>
          </div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => (
              <Link
                key={item.name}
                to={item.href}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 ${
                  item.current
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
                }`}
                aria-current={item.current ? 'page' : undefined}
              >
                {item.name}
              </Link>
            ))}
          </nav>

          {/* Desktop Auth Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {userState.isAuthenticated ? (
              <div className="flex items-center space-x-4">
                <span className="text-sm text-gray-700">
                  Welcome, {userState.user?.first_name || 'User'}
                </span>
                <button
                  onClick={handleLogout}
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-colors duration-200"
              >
                Sign In
              </Link>
            )}
          </div>

          {/* Mobile menu button */}
          <div className="md:hidden">
            <button
              type="button"
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-700 hover:text-blue-600 hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200"
              aria-controls="mobile-menu"
              aria-expanded={isMobileMenuOpen}
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            >
              <span className="sr-only">Open main menu</span>
              {/* Hamburger icon */}
              <svg
                className={`${isMobileMenuOpen ? 'hidden' : 'block'} h-6 w-6`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 6h16M4 12h16M4 18h16"
                />
              </svg>
              {/* Close icon */}
              <svg
                className={`${isMobileMenuOpen ? 'block' : 'hidden'} h-6 w-6`}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M6 18L18 6M6 6l12 12"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div 
        className={`md:hidden transition-all duration-300 ease-in-out ${
          isMobileMenuOpen 
            ? 'max-h-screen opacity-100' 
            : 'max-h-0 opacity-0 overflow-hidden'
        }`}
        id="mobile-menu"
      >
        <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t border-gray-200 shadow-lg touch-manipulation">
          {/* Swipe indicator for mobile */}
          {isMobile && (
            <div className="swipe-indicator" aria-hidden="true" />
          )}
          {navigation.map((item) => (
            <Link
              key={item.name}
              to={item.href}
              className={`block px-3 py-3 rounded-md text-base font-medium transition-colors duration-200 ${
                item.current
                  ? 'text-blue-600 bg-blue-50'
                  : 'text-gray-700 hover:text-blue-600 hover:bg-gray-50'
              }`}
              aria-current={item.current ? 'page' : undefined}
            >
              {item.name}
            </Link>
          ))}
          
          {/* Mobile Auth Actions */}
          <div className="pt-4 border-t border-gray-200">
            {userState.isAuthenticated ? (
              <div className="space-y-3">
                <div className="px-3 py-2 text-sm text-gray-700">
                  Welcome, {userState.user?.first_name || 'User'}
                </div>
                <button
                  onClick={handleLogout}
                  className="block w-full text-left px-3 py-3 rounded-md text-base font-medium text-red-600 hover:text-red-700 hover:bg-red-50 transition-colors duration-200"
                >
                  Logout
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className="block px-3 py-3 rounded-md text-base font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 transition-colors duration-200"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>
      </div>

      {/* Mobile menu backdrop */}
      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-25 z-30 md:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
          aria-hidden="true"
        />
      )}
    </header>
  );
};

export default Header;