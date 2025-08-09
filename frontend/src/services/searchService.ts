import { httpClient } from './index';
import type { SearchSuggestion, ApiResponse } from '../types';

export class SearchService {
  private readonly baseUrl = '/search';

  /**
   * Get search suggestions based on query
   */
  async getSearchSuggestions(query: string, limit: number = 10): Promise<SearchSuggestion[]> {
    if (!query.trim() || query.length < 2) {
      return [];
    }

    try {
      const response: ApiResponse<SearchSuggestion[]> = await httpClient.get(
        `${this.baseUrl}/suggestions/`,
        { q: query, limit },
        true, // enable retry
        true, // enable cache
        5 * 60 * 1000 // 5 minutes TTL
      );
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch search suggestions:', error);
      return [];
    }
  }

  /**
   * Get popular search terms
   */
  async getPopularSearches(limit: number = 10): Promise<SearchSuggestion[]> {
    try {
      const response: ApiResponse<SearchSuggestion[]> = await httpClient.get(
        `${this.baseUrl}/popular/`,
        { limit },
        true, // enable retry
        true, // enable cache
        30 * 60 * 1000 // 30 minutes TTL
      );
      return response.data;
    } catch (error) {
      console.warn('Failed to fetch popular searches:', error);
      return [];
    }
  }

  /**
   * Get recent searches for the user (from localStorage)
   */
  getRecentSearches(limit: number = 5): SearchSuggestion[] {
    try {
      const recentSearches = localStorage.getItem('recentSearches');
      if (!recentSearches) return [];

      const searches: string[] = JSON.parse(recentSearches);
      return searches.slice(0, limit).map((search, index) => ({
        id: `recent-${index}`,
        text: search,
        type: 'job_title' as const
      }));
    } catch (error) {
      console.warn('Failed to get recent searches:', error);
      return [];
    }
  }

  /**
   * Save search term to recent searches
   */
  saveRecentSearch(query: string): void {
    if (!query.trim()) return;

    try {
      const recentSearches = this.getRecentSearches(10).map(s => s.text);
      
      // Remove if already exists
      const filteredSearches = recentSearches.filter(search => search !== query);
      
      // Add to beginning
      const updatedSearches = [query, ...filteredSearches].slice(0, 10);
      
      localStorage.setItem('recentSearches', JSON.stringify(updatedSearches));
    } catch (error) {
      console.warn('Failed to save recent search:', error);
    }
  }

  /**
   * Clear recent searches
   */
  clearRecentSearches(): void {
    try {
      localStorage.removeItem('recentSearches');
    } catch (error) {
      console.warn('Failed to clear recent searches:', error);
    }
  }

  /**
   * Get search suggestions with mixed sources (recent, popular, API)
   */
  async getMixedSuggestions(query: string): Promise<SearchSuggestion[]> {
    const suggestions: SearchSuggestion[] = [];

    if (!query.trim()) {
      // Show recent and popular searches when no query
      const recentSearches = this.getRecentSearches(3);
      const popularSearches = await this.getPopularSearches(5);
      
      suggestions.push(...recentSearches);
      suggestions.push(...popularSearches);
    } else {
      // Show API suggestions when there's a query
      const apiSuggestions = await this.getSearchSuggestions(query, 8);
      suggestions.push(...apiSuggestions);
      
      // Add recent searches that match the query
      const recentSearches = this.getRecentSearches(10);
      const matchingRecent = recentSearches.filter(search => 
        search.text.toLowerCase().includes(query.toLowerCase())
      ).slice(0, 2);
      
      suggestions.push(...matchingRecent);
    }

    // Remove duplicates and limit results
    const uniqueSuggestions = suggestions.filter((suggestion, index, self) => 
      index === self.findIndex(s => s.text === suggestion.text)
    );

    return uniqueSuggestions.slice(0, 10);
  }
}

// Create and export service instance
export const searchService = new SearchService();