import { httpClient } from './index';
import type { ApiResponse, PaginatedResponse } from '../types';

export interface Company {
  id: number;
  name: string;
  description?: string;
  website?: string;
  industry?: {
    id: number;
    name: string;
  };
  size?: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  founded_year?: number;
  location?: string;
  logo?: string;
  is_verified: boolean;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  jobs_count?: number;
  active_jobs_count?: number;
}

export interface CompanyCreateData {
  name: string;
  description?: string;
  website?: string;
  industry_id?: number;
  size?: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  founded_year?: number;
  location?: string;
  logo?: File;
  is_active?: boolean;
}

export interface CompanyUpdateData {
  name?: string;
  description?: string;
  website?: string;
  industry_id?: number;
  size?: 'startup' | 'small' | 'medium' | 'large' | 'enterprise';
  founded_year?: number;
  location?: string;
  logo?: File;
  is_verified?: boolean;
  is_active?: boolean;
}

export interface CompanyFilterParams {
  search?: string;
  industry_id?: number;
  size?: string;
  location?: string;
  is_verified?: boolean;
  is_active?: boolean;
  has_jobs?: boolean;
  founded_year_min?: number;
  founded_year_max?: number;
  ordering?: string;
  page?: number;
  page_size?: number;
}

export class CompanyService {
  private readonly baseUrl = '/jobs/companies';

  /**
   * Get all companies with pagination and filtering
   */
  async getCompanies(params: CompanyFilterParams = {}): Promise<PaginatedResponse<Company>> {
    const response: ApiResponse<PaginatedResponse<Company>> = await httpClient.get(
      `${this.baseUrl}/`,
      params,
      true, // enable retry
      true, // enable cache
      5 * 60 * 1000 // 5 minutes TTL
    );
    return response.data;
  }

  /**
   * Get all companies as array (for dropdowns)
   */
  async getAllCompanies(): Promise<Company[]> {
    const response = await this.getCompanies({ 
      page_size: 1000,
      is_active: true,
      ordering: 'name'
    });
    return response.results;
  }

  /**
   * Get company details by ID
   */
  async getCompany(id: number): Promise<Company> {
    const response: ApiResponse<Company> = await httpClient.get(
      `${this.baseUrl}/${id}/`,
      {},
      true,
      true,
      10 * 60 * 1000 // 10 minutes TTL
    );
    return response.data;
  }

  /**
   * Create new company (admin only)
   */
  async createCompany(data: CompanyCreateData): Promise<Company> {
    if (data.logo) {
      const formData = new FormData();
      
      // Add all fields to FormData
      formData.append('name', data.name);
      if (data.description) formData.append('description', data.description);
      if (data.website) formData.append('website', data.website);
      if (data.industry_id) formData.append('industry_id', data.industry_id.toString());
      if (data.size) formData.append('size', data.size);
      if (data.founded_year) formData.append('founded_year', data.founded_year.toString());
      if (data.location) formData.append('location', data.location);
      if (data.is_active !== undefined) formData.append('is_active', data.is_active.toString());
      formData.append('logo', data.logo);

      const response: ApiResponse<Company> = await httpClient.postFormData(
        `${this.baseUrl}/`,
        formData
      );
      return response.data;
    } else {
      const { logo, ...dataWithoutLogo } = data;
      const response: ApiResponse<Company> = await httpClient.post(
        `${this.baseUrl}/`,
        dataWithoutLogo
      );
      return response.data;
    }
  }

  /**
   * Update company (admin only)
   */
  async updateCompany(id: number, data: CompanyUpdateData): Promise<Company> {
    if (data.logo) {
      const formData = new FormData();
      
      // Add all fields to FormData
      if (data.name) formData.append('name', data.name);
      if (data.description) formData.append('description', data.description);
      if (data.website) formData.append('website', data.website);
      if (data.industry_id) formData.append('industry_id', data.industry_id.toString());
      if (data.size) formData.append('size', data.size);
      if (data.founded_year) formData.append('founded_year', data.founded_year.toString());
      if (data.location) formData.append('location', data.location);
      if (data.is_verified !== undefined) formData.append('is_verified', data.is_verified.toString());
      if (data.is_active !== undefined) formData.append('is_active', data.is_active.toString());
      formData.append('logo', data.logo);

      const response: ApiResponse<Company> = await httpClient.putFormData(
        `${this.baseUrl}/${id}/`,
        formData
      );
      return response.data;
    } else {
      const { logo, ...dataWithoutLogo } = data;
      const response: ApiResponse<Company> = await httpClient.put(
        `${this.baseUrl}/${id}/`,
        dataWithoutLogo
      );
      return response.data;
    }
  }

  /**
   * Partially update company (admin only)
   */
  async patchCompany(id: number, data: Partial<CompanyUpdateData>): Promise<Company> {
    if (data.logo) {
      const formData = new FormData();
      
      // Add only provided fields to FormData
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && key !== 'logo') {
          formData.append(key, typeof value === 'boolean' ? value.toString() : value as string);
        }
      });
      if (data.logo) formData.append('logo', data.logo);

      const response: ApiResponse<Company> = await httpClient.putFormData(
        `${this.baseUrl}/${id}/`,
        formData
      );
      return response.data;
    } else {
      const { logo, ...dataWithoutLogo } = data;
      const response: ApiResponse<Company> = await httpClient.patch(
        `${this.baseUrl}/${id}/`,
        dataWithoutLogo
      );
      return response.data;
    }
  }

  /**
   * Delete/deactivate company (admin only)
   */
  async deleteCompany(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Toggle company verification status (admin only)
   */
  async toggleVerification(id: number): Promise<Company> {
    const response: ApiResponse<Company> = await httpClient.post(
      `${this.baseUrl}/${id}/toggle-verification/`
    );
    return response.data;
  }

  /**
   * Get company jobs
   */
  async getCompanyJobs(id: number, params: { page?: number; page_size?: number; is_active?: boolean } = {}): Promise<PaginatedResponse<any>> {
    const response: ApiResponse<PaginatedResponse<any>> = await httpClient.get(
      `${this.baseUrl}/${id}/jobs/`,
      params,
      true,
      true,
      5 * 60 * 1000
    );
    return response.data;
  }

  /**
   * Get verified companies
   */
  async getVerifiedCompanies(params: Omit<CompanyFilterParams, 'is_verified'> = {}): Promise<PaginatedResponse<Company>> {
    return this.getCompanies({
      ...params,
      is_verified: true
    });
  }

  /**
   * Get companies by industry
   */
  async getCompaniesByIndustry(industryId: number, params: CompanyFilterParams = {}): Promise<PaginatedResponse<Company>> {
    return this.getCompanies({
      ...params,
      industry_id: industryId
    });
  }

  /**
   * Get companies by size
   */
  async getCompaniesBySize(size: string, params: CompanyFilterParams = {}): Promise<PaginatedResponse<Company>> {
    return this.getCompanies({
      ...params,
      size
    });
  }

  /**
   * Get companies by location
   */
  async getCompaniesByLocation(location: string, params: CompanyFilterParams = {}): Promise<PaginatedResponse<Company>> {
    return this.getCompanies({
      ...params,
      location
    });
  }

  /**
   * Search companies
   */
  async searchCompanies(query: string, params: CompanyFilterParams = {}): Promise<PaginatedResponse<Company>> {
    return this.getCompanies({
      ...params,
      search: query
    });
  }

  /**
   * Get company statistics for admin dashboard
   */
  async getCompanyStats(): Promise<{
    total_companies: number;
    verified_companies: number;
    active_companies: number;
    companies_with_jobs: number;
    companies_by_size: Record<string, number>;
    recent_companies: Company[];
  }> {
    try {
      const [
        totalCompanies,
        verifiedCompanies,
        activeCompanies,
        companiesWithJobs,
        recentCompanies
      ] = await Promise.allSettled([
        this.getCompanies({ page_size: 1 }),
        this.getCompanies({ is_verified: true, page_size: 1 }),
        this.getCompanies({ is_active: true, page_size: 1 }),
        this.getCompanies({ has_jobs: true, page_size: 1 }),
        this.getCompanies({ ordering: '-created_at', page_size: 5 })
      ]);

      // Get companies by size
      const sizeResults = await Promise.allSettled([
        this.getCompanies({ size: 'startup', page_size: 1 }),
        this.getCompanies({ size: 'small', page_size: 1 }),
        this.getCompanies({ size: 'medium', page_size: 1 }),
        this.getCompanies({ size: 'large', page_size: 1 }),
        this.getCompanies({ size: 'enterprise', page_size: 1 })
      ]);

      const companiesBySize: Record<string, number> = {
        startup: sizeResults[0].status === 'fulfilled' ? sizeResults[0].value.count : 0,
        small: sizeResults[1].status === 'fulfilled' ? sizeResults[1].value.count : 0,
        medium: sizeResults[2].status === 'fulfilled' ? sizeResults[2].value.count : 0,
        large: sizeResults[3].status === 'fulfilled' ? sizeResults[3].value.count : 0,
        enterprise: sizeResults[4].status === 'fulfilled' ? sizeResults[4].value.count : 0
      };

      return {
        total_companies: totalCompanies.status === 'fulfilled' ? totalCompanies.value.count : 0,
        verified_companies: verifiedCompanies.status === 'fulfilled' ? verifiedCompanies.value.count : 0,
        active_companies: activeCompanies.status === 'fulfilled' ? activeCompanies.value.count : 0,
        companies_with_jobs: companiesWithJobs.status === 'fulfilled' ? companiesWithJobs.value.count : 0,
        companies_by_size: companiesBySize,
        recent_companies: recentCompanies.status === 'fulfilled' ? recentCompanies.value.results : []
      };
    } catch (error) {
      console.warn('Failed to get company stats:', error);
      return {
        total_companies: 0,
        verified_companies: 0,
        active_companies: 0,
        companies_with_jobs: 0,
        companies_by_size: {
          startup: 0,
          small: 0,
          medium: 0,
          large: 0,
          enterprise: 0
        },
        recent_companies: []
      };
    }
  }

  /**
   * Get company locations for filtering
   */
  async getCompanyLocations(): Promise<string[]> {
    try {
      // This would ideally come from a dedicated API endpoint
      // For now, we'll get a sample of companies and extract locations
      const companies = await this.getCompanies({ 
        page_size: 100,
        ordering: 'location'
      });
      
      const locations = companies.results
        .map(company => company.location)
        .filter((location): location is string => location !== undefined && location !== null)
        .filter((location, index, arr) => arr.indexOf(location) === index)
        .sort();
      
      return locations;
    } catch (error) {
      console.warn('Failed to get company locations:', error);
      return [];
    }
  }

  /**
   * Bulk operations for admin
   */
  async bulkUpdateCompanies(ids: number[], data: Partial<CompanyUpdateData>): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      ids.map(id => this.patchCompany(id, data))
    );

    results.forEach(result => {
      if (result.status === 'fulfilled') {
        success++;
      } else {
        failed++;
      }
    });

    return { success, failed };
  }

  /**
   * Bulk delete companies (admin only)
   */
  async bulkDeleteCompanies(ids: number[]): Promise<{ success: number; failed: number }> {
    let success = 0;
    let failed = 0;

    const results = await Promise.allSettled(
      ids.map(id => this.deleteCompany(id))
    );

    results.forEach(result => {
      if (result.status === 'fulfilled') {
        success++;
      } else {
        failed++;
      }
    });

    return { success, failed };
  }

  /**
   * Bulk verify companies (admin only)
   */
  async bulkVerifyCompanies(ids: number[]): Promise<{ success: number; failed: number }> {
    return this.bulkUpdateCompanies(ids, { is_verified: true });
  }

  /**
   * Bulk activate/deactivate companies (admin only)
   */
  async bulkToggleActiveStatus(ids: number[], isActive: boolean): Promise<{ success: number; failed: number }> {
    return this.bulkUpdateCompanies(ids, { is_active: isActive });
  }
}

// Create and export service instance
export const companyService = new CompanyService();