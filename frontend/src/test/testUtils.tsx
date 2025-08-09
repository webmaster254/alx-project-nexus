import React from 'react';
import { render, RenderOptions } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { UserProvider } from '../contexts/UserContext';
import { FilterProvider } from '../contexts/FilterContext';
import { JobProvider } from '../contexts/JobContext';
import { BookmarkProvider } from '../contexts/BookmarkContext';

// Custom render function that includes all providers
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  return (
    <BrowserRouter>
      <UserProvider>
        <FilterProvider>
          <JobProvider>
            <BookmarkProvider>
              {children}
            </BookmarkProvider>
          </JobProvider>
        </FilterProvider>
      </UserProvider>
    </BrowserRouter>
  );
};

const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'>
) => render(ui, { wrapper: AllTheProviders, ...options });

// Re-export everything
export * from '@testing-library/react';
export { customRender as render };

// Mock data factories
export const createMockJob = (overrides = {}) => ({
  id: 1,
  title: 'Software Engineer',
  description: 'We are looking for a software engineer...',
  summary: 'Software engineering role',
  location: 'San Francisco, CA',
  is_remote: false,
  salary_min: 80000,
  salary_max: 120000,
  salary_type: 'yearly' as const,
  salary_currency: 'USD',
  experience_level: 'mid' as const,
  required_skills: 'JavaScript, React',
  preferred_skills: 'TypeScript',
  application_deadline: '2024-12-31',
  external_url: null,
  is_active: true,
  is_featured: false,
  views_count: 100,
  applications_count: 5,
  created_at: '2024-01-01T00:00:00Z',
  updated_at: '2024-01-01T00:00:00Z',
  company: {
    id: 1,
    name: 'Tech Corp',
    description: 'A tech company',
    website: 'https://techcorp.com',
    logo: null,
    size: '100-500',
    industry: 'Technology',
    location: 'San Francisco, CA',
  },
  industry: {
    id: 1,
    name: 'Technology',
    description: 'Tech industry',
  },
  job_type: {
    id: 1,
    name: 'Full-time',
    description: 'Full-time position',
  },
  categories: [
    {
      id: 1,
      name: 'Engineering',
      description: 'Engineering jobs',
    },
  ],
  salary_display: '$80,000 - $120,000',
  days_since_posted: '1 day ago',
  is_new: true,
  is_urgent: false,
  can_apply: true,
  ...overrides,
});

export const createMockUser = (overrides = {}) => ({
  id: 1,
  email: 'test@example.com',
  first_name: 'John',
  last_name: 'Doe',
  is_active: true,
  date_joined: '2024-01-01T00:00:00Z',
  profile: {
    bio: 'Software developer',
    location: 'San Francisco, CA',
    website: 'https://johndoe.com',
    linkedin: 'https://linkedin.com/in/johndoe',
    github: 'https://github.com/johndoe',
    skills: ['JavaScript', 'React', 'Node.js'],
    experience_years: 5,
    resume: null,
    phone: '+1234567890',
  },
  ...overrides,
});

export const createMockCategory = (overrides = {}) => ({
  id: 1,
  name: 'Engineering',
  description: 'Software engineering roles',
  ...overrides,
});

export const createMockCompany = (overrides = {}) => ({
  id: 1,
  name: 'Tech Corp',
  description: 'A leading technology company',
  website: 'https://techcorp.com',
  logo: null,
  size: '100-500',
  industry: 'Technology',
  location: 'San Francisco, CA',
  ...overrides,
});

// Mock API responses
export const createMockPaginatedResponse = <T>(items: T[], overrides = {}) => ({
  count: items.length,
  next: null,
  previous: null,
  results: items,
  ...overrides,
});

// Test helpers
export const waitForLoadingToFinish = () => {
  return new Promise((resolve) => setTimeout(resolve, 0));
};

export const mockIntersectionObserver = () => {
  const mockIntersectionObserver = vi.fn();
  mockIntersectionObserver.mockReturnValue({
    observe: () => null,
    unobserve: () => null,
    disconnect: () => null,
  });
  window.IntersectionObserver = mockIntersectionObserver;
  window.IntersectionObserverEntry = vi.fn();
};

export const mockMatchMedia = () => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(), // deprecated
      removeListener: vi.fn(), // deprecated
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
};

export const mockLocalStorage = () => {
  const localStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock,
  });
  return localStorageMock;
};

export const mockSessionStorage = () => {
  const sessionStorageMock = {
    getItem: vi.fn(),
    setItem: vi.fn(),
    removeItem: vi.fn(),
    clear: vi.fn(),
  };
  Object.defineProperty(window, 'sessionStorage', {
    value: sessionStorageMock,
  });
  return sessionStorageMock;
};

// Accessibility testing helpers
export const checkAccessibility = async (container: HTMLElement) => {
  const { axe } = await import('jest-axe');
  const results = await axe(container);
  expect(results).toHaveNoViolations();
};

// Performance testing helpers
export const measureRenderTime = (renderFn: () => void) => {
  const start = performance.now();
  renderFn();
  const end = performance.now();
  return end - start;
};

// Mock service worker setup for API mocking
export const setupMockServiceWorker = () => {
  // This would be used with MSW (Mock Service Worker)
  // Implementation depends on specific MSW setup
};