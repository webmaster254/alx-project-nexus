import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import { ErrorBoundary, useErrorHandler } from '../ErrorBoundary';

// Mock component that throws an error
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = false }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that uses the error handler hook
const ComponentWithErrorHandler: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = false }) => {
  const handleError = useErrorHandler();
  
  if (shouldThrow) {
    handleError(new Error('Hook error'));
  }
  
  return <div>Component with error handler</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  const originalError = console.error;
  beforeAll(() => {
    console.error = vi.fn();
  });
  
  afterAll(() => {
    console.error = originalError;
  });

  it('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('renders error UI when child component throws', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
  });

  it('renders custom fallback when provided', () => {
    const customFallback = <div>Custom error message</div>;
    
    render(
      <ErrorBoundary fallback={customFallback}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
    expect(screen.queryByText('Something went wrong')).not.toBeInTheDocument();
  });

  it('calls onError callback when error occurs', () => {
    const onError = vi.fn();
    
    render(
      <ErrorBoundary onError={onError}>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String)
      })
    );
  });

  it('resets error state when retry button is clicked', () => {
    let shouldThrow = true;
    const DynamicComponent = () => {
      if (shouldThrow) {
        throw new Error('Test error');
      }
      return <div>No error</div>;
    };

    const { rerender } = render(
      <ErrorBoundary>
        <DynamicComponent />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
    
    // Change the condition and click retry
    shouldThrow = false;
    fireEvent.click(screen.getByText('Try Again'));
    
    // Re-render with the same component (error boundary should reset)
    rerender(
      <ErrorBoundary>
        <DynamicComponent />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  it('shows error details in development mode', () => {
    const originalEnv = import.meta.env.DEV;
    // @ts-ignore
    import.meta.env.DEV = true;
    
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Error Details (Development)')).toBeInTheDocument();
    
    // @ts-ignore
    import.meta.env.DEV = originalEnv;
  });
});

describe('useErrorHandler', () => {
  it('throws error when called', () => {
    expect(() => {
      render(
        <ErrorBoundary>
          <ComponentWithErrorHandler shouldThrow={true} />
        </ErrorBoundary>
      );
    }).not.toThrow(); // ErrorBoundary should catch it
    
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });
});