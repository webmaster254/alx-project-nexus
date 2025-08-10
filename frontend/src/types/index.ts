// TypeScript type definitions

// Core data models
export interface Company {
  id: number;
  name: string;
  description?: string;
  website?: string;
  logo?: string;
  size?: string;
  industry?: string;
  location?: string;
}

export interface Industry {
  id: number;
  name: string;
  description?: string;
}

export interface JobType {
  id: number;
  name: string;
  description?: string;
}

export interface Category {
  id: number;
  name: string;
  description?: string;
  parent_id?: number;
  children?: Category[];
}

export interface Job {
  id: number;
  title: string;
  description: string;
  summary: string;
  location: string;
  is_remote: boolean;
  salary_min?: number;
  salary_max?: number;
  salary_type: 'hourly' | 'monthly' | 'yearly';
  salary_currency: string;
  experience_level: 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'executive';
  required_skills: string;
  preferred_skills: string;
  application_deadline?: string;
  external_url?: string;
  is_active: boolean;
  is_featured: boolean;
  views_count: number;
  applications_count: number;
  created_at: string;
  updated_at: string;
  company: Company;
  industry: Industry;
  job_type: JobType;
  categories: Category[];
  salary_display: string;
  days_since_posted: string;
  is_new: boolean;
  is_urgent: boolean;
  can_apply: boolean;
  is_bookmarked?: boolean;
}

export interface Application {
  id: number;
  job: number;
  user: number;
  cover_letter: string;
  status: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  applied_at: string;
  updated_at: string;
  documents: ApplicationDocument[];
}

export interface ApplicationDocument {
  id: number;
  application: number;
  document_type: 'resume' | 'cover_letter' | 'portfolio';
  title: string;
  file_url: string;
  uploaded_at: string;
}

// API request/response types
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface JobListParams {
  page?: number;
  page_size?: number;
  category?: number[];
  location?: string[];
  experience_level?: string[];
  is_remote?: boolean;
  salary_min?: number;
  salary_max?: number;
  job_type?: number[];
  search?: string;
  ordering?: string;
  company?: string;
  skills?: string[];
  posted_within?: 'day' | 'week' | 'month' | 'all';
}

export interface FilterParams {
  categories?: number[];
  locations?: string[];
  experience_levels?: string[];
  salary_range?: [number, number];
  job_types?: number[];
  is_remote?: boolean;
  company?: string;
  skills?: string[];
  posted_within?: 'day' | 'week' | 'month' | 'all';
}

export interface SearchSuggestion {
  id: string;
  text: string;
  type: 'job_title' | 'company' | 'skill' | 'location';
  count?: number;
}

export interface BookmarkState {
  bookmarkedJobs: number[];
  isLoading: boolean;
  error: string | null;
}

export interface SortOption {
  value: string;
  label: string;
  description?: string;
}

export interface RecommendationReason {
  type: 'skill_match' | 'location_match' | 'experience_match' | 'company_match' | 'category_match';
  score: number;
  description: string;
}

export interface JobRecommendation {
  job: Job;
  score: number;
  reasons: RecommendationReason[];
  created_at: string;
}

export interface ApplicationData {
  job: number;
  cover_letter: string;
  documents: {
    document_type: 'resume' | 'cover_letter' | 'portfolio';
    title: string;
    file: File;
  }[];
}

// API Error types
export interface ApiError {
  message: string;
  status: number;
  details?: Record<string, string[]>;
}

// Enhanced API Error types
export interface EnhancedApiError extends ApiError {
  code?: string;
  retryable?: boolean;
  timestamp: number;
}

// HTTP client types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export type ExperienceLevel = 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'executive';

// Context State Types
export interface JobState {
  jobs: Job[];
  currentJob: Job | null;
  featuredJobs: Job[];
  recentJobs: Job[];
  similarJobs: Job[];
  totalCount: number;
  currentPage: number;
  hasNextPage: boolean;
  hasPreviousPage: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface FilterState {
  searchQuery: string;
  categories: number[];
  locations: string[];
  experienceLevels: ExperienceLevel[];
  salaryRange: [number, number];
  jobTypes: number[];
  isRemote: boolean | null;
  isActive: boolean;
}

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser?: boolean;
  date_joined: string;
  profile?: {
    phone?: string;
    location?: string;
    bio?: string;
    experience_years?: number;
    skills?: string[];
    resume_url?: string;
  };
}

export interface UserState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  token: string | null;
}

// Action Types for Reducers
export type JobAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_JOBS'; payload: { jobs: Job[]; totalCount: number; currentPage: number; hasNextPage: boolean; hasPreviousPage: boolean } }
  | { type: 'SET_CURRENT_JOB'; payload: Job | null }
  | { type: 'SET_FEATURED_JOBS'; payload: Job[] }
  | { type: 'SET_RECENT_JOBS'; payload: Job[] }
  | { type: 'SET_SIMILAR_JOBS'; payload: Job[] }
  | { type: 'APPEND_JOBS'; payload: Job[] }
  | { type: 'CLEAR_JOBS' }
  | { type: 'RESET_STATE' };

export type FilterAction =
  | { type: 'SET_SEARCH_QUERY'; payload: string }
  | { type: 'SET_CATEGORIES'; payload: number[] }
  | { type: 'SET_LOCATIONS'; payload: string[] }
  | { type: 'SET_EXPERIENCE_LEVELS'; payload: ExperienceLevel[] }
  | { type: 'SET_SALARY_RANGE'; payload: [number, number] }
  | { type: 'SET_JOB_TYPES'; payload: number[] }
  | { type: 'SET_IS_REMOTE'; payload: boolean | null }
  | { type: 'SET_IS_ACTIVE'; payload: boolean }
  | { type: 'CLEAR_FILTERS' }
  | { type: 'RESET_FILTERS' };

export type UserAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_USER'; payload: User | null }
  | { type: 'SET_AUTHENTICATED'; payload: boolean }
  | { type: 'SET_TOKEN'; payload: string | null }
  | { type: 'LOGOUT' }
  | { type: 'RESET_STATE' };
