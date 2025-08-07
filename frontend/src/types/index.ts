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
}

export interface FilterParams {
  categories?: number[];
  locations?: string[];
  experience_levels?: string[];
  salary_range?: [number, number];
  job_types?: number[];
  is_remote?: boolean;
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

// HTTP client types
export interface ApiResponse<T> {
  data: T;
  status: number;
  message?: string;
}

export type ExperienceLevel = 'entry' | 'junior' | 'mid' | 'senior' | 'lead' | 'executive';
