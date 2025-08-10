# Job Board Frontend

A modern, responsive React frontend application for the Job Board platform, built with TypeScript, Vite, and Tailwind CSS.

## Project Overview

This frontend application provides a comprehensive user interface for a job board platform, enabling job seekers to discover opportunities and employers to manage job postings. The application features a clean, intuitive design with robust functionality for job searching, application management, and user authentication.

## Purpose and Features

### Core Functionality

- **Job Discovery**: Browse and search through job listings with advanced filtering capabilities
- **User Authentication**: Secure login/registration system with JWT token management
- **Application Management**: Submit and track job applications with document uploads
- **User Profiles**: Manage personal information and application history
- **Admin Dashboard**: Administrative interface for managing jobs, applications, and users
- **Responsive Design**: Optimized for desktop, tablet, and mobile devices

### Key Features

- **Advanced Search & Filtering**: Filter jobs by category, location, salary, job type, and more
- **Bookmarking System**: Save interesting job postings for later review
- **Real-time Updates**: Live updates for application status and new job postings
- **Offline Support**: Basic offline functionality with service worker integration
- **Performance Monitoring**: Built-in performance tracking and optimization
- **Accessibility**: WCAG compliant with comprehensive accessibility features
- **Progressive Web App**: PWA capabilities for mobile app-like experience

## Technology Stack

### Core Technologies

- **React 19.1.1** - Modern React with latest features and hooks
- **TypeScript** - Type-safe development with enhanced developer experience
- **Vite** - Fast build tool with hot module replacement
- **React Router DOM 7.8.0** - Client-side routing and navigation

### Styling & UI

- **Tailwind CSS 4.1.11** - Utility-first CSS framework for rapid UI development
- **Lucide React** - Beautiful, customizable SVG icons
- **Responsive Design** - Mobile-first approach with breakpoint optimization

### State Management & Data

- **React Context API** - Global state management for user, jobs, filters, and bookmarks
- **Axios** - HTTP client for API communication with interceptors and error handling
- **Custom Hooks** - Reusable logic for data fetching and state management

### Development & Testing

- **Vitest** - Fast unit testing framework
- **Testing Library** - Component testing utilities
- **ESLint & Prettier** - Code quality and formatting
- **TypeScript Strict Mode** - Enhanced type checking

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── auth/           # Authentication components
│   │   ├── common/         # Shared components (Header, Footer, etc.)
│   │   ├── filter/         # Job filtering components
│   │   └── job/            # Job-related components
│   ├── contexts/           # React Context providers
│   │   ├── UserContext.tsx
│   │   ├── JobContext.tsx
│   │   ├── FilterContext.tsx
│   │   └── BookmarkContext.tsx
│   ├── pages/              # Page components
│   │   ├── HomePage.tsx
│   │   ├── JobListingPage.tsx
│   │   ├── JobDetailPage.tsx
│   │   ├── AuthPage.tsx
│   │   ├── ProfilePage.tsx
│   │   └── AdminDashboardPage.tsx
│   ├── services/           # API services and utilities
│   ├── hooks/              # Custom React hooks
│   ├── types/              # TypeScript type definitions
│   ├── utils/              # Utility functions
│   └── test/               # Test utilities and setup
├── public/                 # Static assets
├── dist/                   # Build output
└── config files            # Vite, TypeScript, ESLint configs
```

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn package manager

### Installation

1. **Navigate to frontend directory:**

   ```bash
   cd frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Environment setup:**

   ```bash
   cp .env.example .env.development
   # Edit .env.development with your API endpoints
   ```

4. **Start development server:**
   ```bash
   npm run dev
   ```

The application will be available at `http://localhost:5173`

## Available Scripts

### Development

- `npm run dev` - Start development server with hot reload
- `npm run preview` - Preview production build locally

### Building

- `npm run build` - Build for production
- `npm run build:prod` - Production build with optimizations
- `npm run build:staging` - Staging environment build
- `npm run build:analyze` - Build with bundle analysis

### Code Quality

- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues automatically
- `npm run format` - Format code with Prettier
- `npm run format:check` - Check code formatting
- `npm run type-check` - Run TypeScript type checking

### Testing

- `npm run test` - Run tests in watch mode
- `npm run test:run` - Run tests once
- `npm run test:coverage` - Run tests with coverage report
- `npm run test:ui` - Run tests with UI interface

### Pre-commit

- `npm run pre-commit` - Run linting, type checking, and tests

## Environment Configuration

The application supports multiple environments:

- **Development** (`.env.development`) - Local development
- **Staging** (`.env.staging`) - Staging environment
- **Production** (`.env.production`) - Production deployment

### Environment Variables

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=Job Board
VITE_APP_VERSION=1.0.0
VITE_ENABLE_ANALYTICS=false
VITE_SENTRY_DSN=your_sentry_dsn
```

## Key Components

### Authentication System

- JWT token management with automatic refresh
- Protected routes with role-based access control
- Persistent login state across browser sessions

### Job Management

- Advanced search with multiple filter criteria
- Infinite scroll pagination for performance
- Real-time job status updates

### Application Tracking

- Document upload and management
- Application status tracking
- Email notifications for status changes

### Admin Features

- Job posting management
- User administration
- Application review system
- Analytics dashboard

## Performance Optimizations

- **Code Splitting** - Lazy loading of route components
- **Bundle Optimization** - Tree shaking and minification
- **Image Optimization** - Responsive images with lazy loading
- **Caching Strategy** - Service worker for offline functionality
- **Performance Monitoring** - Real-time performance metrics

## Accessibility Features

- WCAG 2.1 AA compliance
- Keyboard navigation support
- Screen reader compatibility
- High contrast mode support
- Focus management and indicators

## Browser Support

- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Deployment

The application is configured for deployment on:

- **Netlify** - Static site hosting with continuous deployment
- **Vercel** - Serverless deployment with edge functions
- **Docker** - Containerized deployment with Nginx



## API Integration

The frontend integrates with the Django REST Framework backend API:

- **Base URL**: Configurable via environment variables
- **Authentication**: JWT tokens with automatic refresh
- **Error Handling**: Comprehensive error boundaries and user feedback
- **Request Interceptors**: Automatic token attachment and refresh
- **Response Caching**: Intelligent caching for improved performance
