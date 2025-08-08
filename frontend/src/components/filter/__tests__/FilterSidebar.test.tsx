import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import FilterSidebar from '../FilterSidebar';
import { FilterProvider } from '../../../contexts/FilterContext';
import { categoryService } from '../../../services/categoryService';

// Mock the category service
vi.mock('../../../services/categoryService', () => ({
  categoryService: {
    getCategories: vi.fn().mockResolvedValue([
      { id: 1, name: 'Software Development' },
      { id: 2, name: 'Data Science' },
      { id: 3, name: 'Design' },
    ]),
  },
}));

// Mock the FilterContext
const mockFilterActions = {
  addCategory: vi.fn(),
  removeCategory: vi.fn(),
  addLocation: vi.fn(),
  removeLocation: vi.fn(),
  addExperienceLevel: vi.fn(),
  removeExperienceLevel: vi.fn(),
  setSalaryRange: vi.fn(),
  setIsRemote: vi.fn(),
  clearFilters: vi.fn(),
  getActiveFiltersCount: vi.fn().mockReturnValue(0),
};

const mockFilterState = {
  searchQuery: '',
  categories: [],
  locations: [],
  experienceLevels: [],
  salaryRange: [0, 200000] as [number, number],
  jobTypes: [],
  isRemote: null,
  isActive: false,
};

vi.mock('../../../contexts/FilterContext', async () => {
  const actual = await vi.importActual('../../../contexts/FilterContext');
  return {
    ...actual,
    useFilter: () => ({
      state: mockFilterState,
      ...mockFilterActions,
    }),
  };
});

const renderFilterSidebar = (props = {}) => {
  return render(
    <FilterProvider>
      <FilterSidebar {...props} />
    </FilterProvider>
  );
};

describe('FilterSidebar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders filter sections', async () => {
    renderFilterSidebar();
    
    expect(screen.getByText('Filters')).toBeInTheDocument();
    expect(screen.getByText('Category')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Experience Level')).toBeInTheDocument();
    expect(screen.getByText('Salary Range')).toBeInTheDocument();
    expect(screen.getByText('Work Type')).toBeInTheDocument();
  });

  it('loads and displays categories', async () => {
    renderFilterSidebar();
    
    await waitFor(() => {
      expect(screen.getByText('Software Development')).toBeInTheDocument();
      expect(screen.getByText('Data Science')).toBeInTheDocument();
      expect(screen.getByText('Design')).toBeInTheDocument();
    });
  });

  it('shows loading state for categories', () => {
    renderFilterSidebar();
    
    // Should show loading skeletons initially
    const loadingElements = screen.getAllByRole('generic').filter(el => 
      el.classList.contains('animate-pulse')
    );
    expect(loadingElements.length).toBeGreaterThan(0);
  });

  it('handles category selection', async () => {
    renderFilterSidebar();
    
    await waitFor(() => {
      const categoryCheckbox = screen.getByLabelText('Software Development');
      fireEvent.click(categoryCheckbox);
      expect(mockFilterActions.addCategory).toHaveBeenCalledWith(1);
    });
  });

  it('displays experience level options', () => {
    renderFilterSidebar();
    
    expect(screen.getByText('Entry Level')).toBeInTheDocument();
    expect(screen.getByText('Junior')).toBeInTheDocument();
    expect(screen.getByText('Mid Level')).toBeInTheDocument();
    expect(screen.getByText('Senior')).toBeInTheDocument();
    expect(screen.getByText('Lead')).toBeInTheDocument();
    expect(screen.getByText('Executive')).toBeInTheDocument();
  });

  it('handles experience level selection', () => {
    renderFilterSidebar();
    
    const seniorCheckbox = screen.getByLabelText('Senior');
    fireEvent.click(seniorCheckbox);
    expect(mockFilterActions.addExperienceLevel).toHaveBeenCalledWith('senior');
  });

  it('displays common locations', () => {
    renderFilterSidebar();
    
    expect(screen.getByText('New York, NY')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  it('handles location input and addition', () => {
    renderFilterSidebar();
    
    const locationInput = screen.getByPlaceholderText('Add location...');
    fireEvent.change(locationInput, { target: { value: 'Boston, MA' } });
    fireEvent.keyDown(locationInput, { key: 'Enter' });
    
    expect(mockFilterActions.addLocation).toHaveBeenCalledWith('Boston, MA');
  });

  it('displays work type options', () => {
    renderFilterSidebar();
    
    expect(screen.getByText('All jobs')).toBeInTheDocument();
    expect(screen.getByText('Remote only')).toBeInTheDocument();
    expect(screen.getByText('On-site only')).toBeInTheDocument();
  });

  it('handles remote work selection', () => {
    renderFilterSidebar();
    
    const remoteOnlyRadio = screen.getByLabelText('Remote only');
    fireEvent.click(remoteOnlyRadio);
    expect(mockFilterActions.setIsRemote).toHaveBeenCalledWith(true);
  });

  it('handles salary range input', () => {
    renderFilterSidebar();
    
    const minSalaryInput = screen.getByPlaceholderText('Min');
    const maxSalaryInput = screen.getByPlaceholderText('Max');
    
    fireEvent.change(minSalaryInput, { target: { value: '50000' } });
    expect(mockFilterActions.setSalaryRange).toHaveBeenCalledWith([50000, 200000]);
    
    fireEvent.change(maxSalaryInput, { target: { value: '100000' } });
    expect(mockFilterActions.setSalaryRange).toHaveBeenCalledWith([0, 100000]);
  });

  it('shows clear filters button when filters are active', () => {
    mockFilterActions.getActiveFiltersCount.mockReturnValue(3);
    renderFilterSidebar();
    
    const clearButton = screen.getByText('Clear all filters');
    expect(clearButton).toBeInTheDocument();
    
    fireEvent.click(clearButton);
    expect(mockFilterActions.clearFilters).toHaveBeenCalled();
  });

  it('displays active filters count badge', () => {
    mockFilterActions.getActiveFiltersCount.mockReturnValue(2);
    renderFilterSidebar();
    
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('renders as mobile drawer when isMobile is true', () => {
    renderFilterSidebar({ isMobile: true, isOpen: true, onClose: vi.fn() });
    
    // Should render with fixed positioning for mobile overlay
    const overlay = document.querySelector('.fixed.inset-0.z-50');
    expect(overlay).toBeInTheDocument();
  });

  it('calls onClose when close button is clicked in mobile mode', () => {
    const mockOnClose = vi.fn();
    renderFilterSidebar({ isMobile: true, isOpen: true, onClose: mockOnClose });
    
    const closeButton = screen.getByLabelText('Close filters');
    fireEvent.click(closeButton);
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('shows "Show more" button when there are many categories', async () => {
    // Mock more categories
    const manyCategories = Array.from({ length: 12 }, (_, i) => ({
      id: i + 1,
      name: `Category ${i + 1}`,
    }));
    
    vi.mocked(categoryService.getCategories)
      .mockResolvedValue(manyCategories);
    
    renderFilterSidebar();
    
    await waitFor(() => {
      expect(screen.getByText('Show 4 more')).toBeInTheDocument();
    });
  });
});