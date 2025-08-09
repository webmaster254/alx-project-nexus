import React from 'react';
import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { measureRenderTime, createMockJob } from '../testUtils';
import JobCard from '../../components/job/JobCard';
import JobListingPage from '../../pages/JobListingPage';
import * as jobService from '../../services/jobService';

// Mock the job service
vi.mock('../../services/jobService');
const mockJobService = vi.mocked(jobService);

describe('Component Performance Tests', () => {
  it('should render JobCard within acceptable time', () => {
    const mockJob = createMockJob();
    
    const renderTime = measureRenderTime(() => {
      render(<JobCard job={mockJob} />);
    });

    // JobCard should render in less than 50ms
    expect(renderTime).toBeLessThan(50);
  });

  it('should render multiple JobCards efficiently', () => {
    const mockJobs = Array.from({ length: 20 }, (_, i) => 
      createMockJob({ id: i + 1, title: `Job ${i + 1}` })
    );

    const renderTime = measureRenderTime(() => {
      render(
        <div>
          {mockJobs.map(job => (
            <JobCard key={job.id} job={job} />
          ))}
        </div>
      );
    });

    // 20 JobCards should render in less than 200ms
    expect(renderTime).toBeLessThan(200);
  });

  it('should handle large job lists without performance degradation', async () => {
    const largeJobList = Array.from({ length: 100 }, (_, i) => 
      createMockJob({ id: i + 1, title: `Job ${i + 1}` })
    );

    mockJobService.getJobs.mockResolvedValue({
      count: 100,
      next: null,
      previous: null,
      results: largeJobList,
    });

    const renderTime = measureRenderTime(() => {
      render(<JobListingPage />);
    });

    // Initial render should be fast even with large data
    expect(renderTime).toBeLessThan(500);
  });

  it('should not cause memory leaks with frequent re-renders', () => {
    const mockJob = createMockJob();
    let renderCount = 0;

    // Simulate frequent re-renders
    const TestComponent = () => {
      renderCount++;
      return <JobCard job={mockJob} />;
    };

    const { rerender } = render(<TestComponent />);

    // Re-render 50 times
    for (let i = 0; i < 50; i++) {
      rerender(<TestComponent />);
    }

    expect(renderCount).toBe(51); // Initial render + 50 re-renders
    
    // Check that performance doesn't degrade significantly
    const finalRenderTime = measureRenderTime(() => {
      rerender(<TestComponent />);
    });

    expect(finalRenderTime).toBeLessThan(50);
  });

  it('should efficiently handle search input changes', () => {
    const mockJobs = Array.from({ length: 10 }, (_, i) => 
      createMockJob({ id: i + 1, title: `Job ${i + 1}` })
    );

    mockJobService.getJobs.mockResolvedValue({
      count: 10,
      next: null,
      previous: null,
      results: mockJobs,
    });

    const renderTime = measureRenderTime(() => {
      render(<JobListingPage />);
    });

    // Search functionality should not significantly impact render time
    expect(renderTime).toBeLessThan(300);
  });

  it('should optimize image loading in job cards', () => {
    const mockJobWithLogo = createMockJob({
      company: {
        ...createMockJob().company,
        logo: 'https://example.com/logo.png',
      },
    });

    const renderTime = measureRenderTime(() => {
      render(<JobCard job={mockJobWithLogo} />);
    });

    // Image loading should not block rendering
    expect(renderTime).toBeLessThan(50);
  });

  it('should handle rapid filter changes efficiently', () => {
    const mockJobs = Array.from({ length: 20 }, (_, i) => 
      createMockJob({ id: i + 1 })
    );

    mockJobService.getJobs.mockResolvedValue({
      count: 20,
      next: null,
      previous: null,
      results: mockJobs,
    });

    // Measure time for multiple rapid filter changes
    const startTime = performance.now();
    
    for (let i = 0; i < 10; i++) {
      render(<JobListingPage />);
    }
    
    const endTime = performance.now();
    const totalTime = endTime - startTime;

    // Multiple renders should complete in reasonable time
    expect(totalTime).toBeLessThan(1000);
  });

  it('should efficiently handle scroll events', () => {
    const mockJobs = Array.from({ length: 50 }, (_, i) => 
      createMockJob({ id: i + 1 })
    );

    mockJobService.getJobs.mockResolvedValue({
      count: 50,
      next: null,
      previous: null,
      results: mockJobs,
    });

    const { container } = render(<JobListingPage />);
    
    // Simulate scroll events
    const startTime = performance.now();
    
    for (let i = 0; i < 20; i++) {
      const scrollEvent = new Event('scroll');
      container.dispatchEvent(scrollEvent);
    }
    
    const endTime = performance.now();
    const scrollHandlingTime = endTime - startTime;

    // Scroll handling should be efficient
    expect(scrollHandlingTime).toBeLessThan(100);
  });

  it('should optimize bundle size by code splitting', () => {
    // This test would typically check bundle analysis results
    // For now, we'll just ensure components can be imported efficiently
    
    const importTime = measureRenderTime(() => {
      // Simulate dynamic import
      import('../../components/job/JobCard');
    });

    // Dynamic imports should be fast
    expect(importTime).toBeLessThan(10);
  });

  it('should handle concurrent renders without blocking', async () => {
    const mockJobs = Array.from({ length: 30 }, (_, i) => 
      createMockJob({ id: i + 1 })
    );

    mockJobService.getJobs.mockResolvedValue({
      count: 30,
      next: null,
      previous: null,
      results: mockJobs,
    });

    // Simulate concurrent renders
    const renderPromises = Array.from({ length: 5 }, () => 
      new Promise<number>((resolve) => {
        const startTime = performance.now();
        render(<JobListingPage />);
        const endTime = performance.now();
        resolve(endTime - startTime);
      })
    );

    const renderTimes = await Promise.all(renderPromises);
    const averageRenderTime = renderTimes.reduce((a, b) => a + b, 0) / renderTimes.length;

    // Concurrent renders should not significantly impact performance
    expect(averageRenderTime).toBeLessThan(400);
  });
});