import { httpClient } from './index';
import type { Job, ApiResponse } from '../types';

export interface BookmarkedJob {
  id: number;
  job: Job;
  bookmarked_at: string;
}

export class BookmarkService {
  private readonly baseUrl = '/bookmarks';

  /**
   * Get user's bookmarked jobs
   */
  async getBookmarkedJobs(): Promise<BookmarkedJob[]> {
    const response: ApiResponse<BookmarkedJob[]> = await httpClient.get(
      `${this.baseUrl}/`,
      undefined,
      true, // enable retry
      true, // enable cache
      5 * 60 * 1000 // 5 minutes TTL
    );
    return response.data;
  }

  /**
   * Bookmark a job
   */
  async bookmarkJob(jobId: number): Promise<BookmarkedJob> {
    const response: ApiResponse<BookmarkedJob> = await httpClient.post(
      `${this.baseUrl}/`,
      { job: jobId }
    );
    return response.data;
  }

  /**
   * Remove bookmark from a job
   */
  async removeBookmark(jobId: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${jobId}/`);
  }

  /**
   * Check if a job is bookmarked
   */
  async isJobBookmarked(jobId: number): Promise<boolean> {
    try {
      const response: ApiResponse<{ bookmarked: boolean }> = await httpClient.get(
        `${this.baseUrl}/check/${jobId}/`
      );
      return response.data.bookmarked;
    } catch (error) {
      return false;
    }
  }

  /**
   * Toggle bookmark status for a job
   */
  async toggleBookmark(jobId: number): Promise<{ bookmarked: boolean; bookmark?: BookmarkedJob }> {
    try {
      const isBookmarked = await this.isJobBookmarked(jobId);
      
      if (isBookmarked) {
        await this.removeBookmark(jobId);
        return { bookmarked: false };
      } else {
        const bookmark = await this.bookmarkJob(jobId);
        return { bookmarked: true, bookmark };
      }
    } catch (error) {
      throw new Error('Failed to toggle bookmark');
    }
  }
}

// Create and export service instance
export const bookmarkService = new BookmarkService();