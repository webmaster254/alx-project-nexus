import { httpClient } from './index';
import type { Job, PaginatedResponse, ApiResponse } from '../types';

export interface RecommendationParams {
  user_id?: number;
  job_id?: number;
  limit?: number;
  exclude_applied?: boolean;
  exclude_viewed?: boolean;
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

export class RecommendationService {
  private readonly baseUrl = '/recommendations';

  /**
   * Get personalized job recommendations for the user
   */
  async getPersonalizedRecommendations(params: RecommendationParams = {}): Promise<JobRecommendation[]> {
    try {
      const response: ApiResponse<JobRecommendation[]> = await httpClient.get(
        `${this.baseUrl}/personalized/`,
        {
          limit: params.limit || 10,
          exclude_applied: params.exclude_applied !== false,
          exclude_viewed: params.exclude_viewed !== false,
        },
        true, // enable retry
        true, // enable cache
        10 * 60 * 1000 // 10 minutes TTL
      );
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch personalized recommendations:', error);
      return [];
    }
  }

  /**
   * Get similar jobs based on a specific job
   */
  async getSimilarJobs(jobId: number, limit: number = 5): Promise<Job[]> {
    try {
      const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
        `${this.baseUrl}/similar/${jobId}/`,
        { limit },
        true, // enable retry
        true, // enable cache
        15 * 60 * 1000 // 15 minutes TTL
      );
      return response.data.results;
    } catch (error) {
      console.warn('Failed to fetch similar jobs:', error);
      return [];
    }
  }

  /**
   * Get trending jobs based on user activity and market trends
   */
  async getTrendingJobs(limit: number = 10): Promise<Job[]> {
    try {
      const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
        `${this.baseUrl}/trending/`,
        { limit },
        true, // enable retry
        true, // enable cache
        30 * 60 * 1000 // 30 minutes TTL
      );
      return response.data.results;
    } catch (error) {
      console.warn('Failed to fetch trending jobs:', error);
      return [];
    }
  }

  /**
   * Get jobs recommended based on user's skills
   */
  async getSkillBasedRecommendations(skills: string[], limit: number = 10): Promise<Job[]> {
    try {
      const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
        `${this.baseUrl}/skills/`,
        { 
          skills: skills.join(','),
          limit 
        },
        true, // enable retry
        true, // enable cache
        20 * 60 * 1000 // 20 minutes TTL
      );
      return response.data.results;
    } catch (error) {
      console.warn('Failed to fetch skill-based recommendations:', error);
      return [];
    }
  }

  /**
   * Get jobs from companies the user has shown interest in
   */
  async getCompanyBasedRecommendations(limit: number = 10): Promise<Job[]> {
    try {
      const response: ApiResponse<PaginatedResponse<Job>> = await httpClient.get(
        `${this.baseUrl}/companies/`,
        { limit },
        true, // enable retry
        true, // enable cache
        20 * 60 * 1000 // 20 minutes TTL
      );
      return response.data.results;
    } catch (error) {
      console.warn('Failed to fetch company-based recommendations:', error);
      return [];
    }
  }

  /**
   * Record user interaction with a job for better recommendations
   */
  async recordJobInteraction(jobId: number, interactionType: 'view' | 'click' | 'apply' | 'bookmark' | 'share'): Promise<void> {
    try {
      await httpClient.post(`${this.baseUrl}/interactions/`, {
        job_id: jobId,
        interaction_type: interactionType,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      // Don't throw error for tracking failures
      console.warn('Failed to record job interaction:', error);
    }
  }

  /**
   * Get recommendation explanation for a specific job
   */
  async getRecommendationExplanation(jobId: number): Promise<RecommendationReason[]> {
    try {
      const response: ApiResponse<{ reasons: RecommendationReason[] }> = await httpClient.get(
        `${this.baseUrl}/explain/${jobId}/`
      );
      return response.data.reasons;
    } catch (error) {
      console.warn('Failed to get recommendation explanation:', error);
      return [];
    }
  }

  /**
   * Provide feedback on recommendation quality
   */
  async provideFeedback(jobId: number, feedback: 'helpful' | 'not_helpful' | 'not_relevant', reason?: string): Promise<void> {
    try {
      await httpClient.post(`${this.baseUrl}/feedback/`, {
        job_id: jobId,
        feedback,
        reason,
        timestamp: new Date().toISOString()
      });
    } catch (error) {
      console.warn('Failed to provide recommendation feedback:', error);
    }
  }

  /**
   * Get mixed recommendations combining different strategies
   */
  async getMixedRecommendations(limit: number = 20): Promise<{
    personalized: JobRecommendation[];
    trending: Job[];
    skillBased: Job[];
    companyBased: Job[];
  }> {
    try {
      const [personalized, trending, skillBased, companyBased] = await Promise.allSettled([
        this.getPersonalizedRecommendations({ limit: Math.ceil(limit * 0.4) }),
        this.getTrendingJobs(Math.ceil(limit * 0.3)),
        this.getSkillBasedRecommendations([], Math.ceil(limit * 0.2)),
        this.getCompanyBasedRecommendations(Math.ceil(limit * 0.1))
      ]);

      return {
        personalized: personalized.status === 'fulfilled' ? personalized.value : [],
        trending: trending.status === 'fulfilled' ? trending.value : [],
        skillBased: skillBased.status === 'fulfilled' ? skillBased.value : [],
        companyBased: companyBased.status === 'fulfilled' ? companyBased.value : []
      };
    } catch (error) {
      console.warn('Failed to fetch mixed recommendations:', error);
      return {
        personalized: [],
        trending: [],
        skillBased: [],
        companyBased: []
      };
    }
  }
}

// Create and export service instance
export const recommendationService = new RecommendationService();