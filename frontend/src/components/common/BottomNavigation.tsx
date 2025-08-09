import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useUser } from '../../contexts/UserContext';
import { useFilter } from '../../contexts/FilterContext';

const BottomNavigation: React.FC = () => {
  const location = useLocation();
  const { state: userState } = useUser();
  const { getActiveFiltersCount } = useFilter();

  const activeFiltersCount = getActiveFiltersCount();

  const navigationItems = [
    {
      name: 'Jobs',
      href: '/',
      icon: (active: boolean) => (
        <svg
          className={`w-6 h-6 ${active ? 'text-blue-600' : 'text-gray-400'}`}
          fill={active ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={active ? 0 : 2}
            d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2-2v2m8 0V6a2 2 0 012 2v6.5M16 6H8m0 0v-.5A2.5 2.5 0 0110.5 3h3A2.5 2.5 0 0116 5.5V6H8z"
          />
        </svg>
      ),
      current: location.pathname === '/',
      badge: null
    },
    {
      name: 'Search',
      href: '/?focus=search',
      icon: (active: boolean) => (
        <svg
          className={`w-6 h-6 ${active ? 'text-blue-600' : 'text-gray-400'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
      ),
      current: location.search.includes('focus=search'),
      badge: null
    },
    {
      name: 'Filters',
      href: '/?focus=filters',
      icon: (active: boolean) => (
        <svg
          className={`w-6 h-6 ${active ? 'text-blue-600' : 'text-gray-400'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.207A1 1 0 013 6.5V4z"
          />
        </svg>
      ),
      current: location.search.includes('focus=filters'),
      badge: activeFiltersCount > 0 ? activeFiltersCount : null
    }
  ];

  // Add profile/login item based on auth state
  if (userState.isAuthenticated) {
    navigationItems.push({
      name: 'Profile',
      href: '/profile',
      icon: (active: boolean) => (
        <svg
          className={`w-6 h-6 ${active ? 'text-blue-600' : 'text-gray-400'}`}
          fill={active ? 'currentColor' : 'none'}
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={active ? 0 : 2}
            d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"
          />
        </svg>
      ),
      current: location.pathname === '/profile',
      badge: null
    });
  } else {
    navigationItems.push({
      name: 'Login',
      href: '/login',
      icon: (active: boolean) => (
        <svg
          className={`w-6 h-6 ${active ? 'text-blue-600' : 'text-gray-400'}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"
          />
        </svg>
      ),
      current: location.pathname === '/login',
      badge: null
    });
  }

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 safe-area-bottom z-40">
      <div className="grid grid-cols-4 h-16">
        {navigationItems.map((item) => (
          <Link
            key={item.name}
            to={item.href}
            className={`flex flex-col items-center justify-center px-2 py-2 text-xs font-medium transition-colors duration-200 touch-manipulation relative ${
              item.current
                ? 'text-blue-600 bg-blue-50'
                : 'text-gray-500 hover:text-gray-700 active:text-blue-600 active:bg-blue-50'
            }`}
            aria-current={item.current ? 'page' : undefined}
          >
            <div className="relative">
              {item.icon(item.current)}
              {item.badge && (
                <span className="absolute -top-2 -right-2 inline-flex items-center justify-center px-1.5 py-0.5 text-xs font-bold leading-none text-white bg-red-600 rounded-full min-w-[18px] h-[18px]">
                  {item.badge > 99 ? '99+' : item.badge}
                </span>
              )}
            </div>
            <span className="mt-1 truncate max-w-full">{item.name}</span>
          </Link>
        ))}
      </div>
    </nav>
  );
};

export default BottomNavigation;