import type { Job } from '../types';

export interface ShareOptions {
  title?: string;
  text?: string;
  url?: string;
}

export class ShareService {
  /**
   * Share a job using the Web Share API (if available) or fallback to clipboard
   */
  async shareJob(job: Job, baseUrl: string = window.location.origin): Promise<boolean> {
    const shareData: ShareOptions = {
      title: `${job.title} at ${job.company.name}`,
      text: `Check out this job opportunity: ${job.title} at ${job.company.name}`,
      url: `${baseUrl}/jobs/${job.id}`
    };

    // Try Web Share API first (mobile browsers)
    if (navigator.share && this.canUseWebShare()) {
      try {
        await navigator.share(shareData);
        return true;
      } catch (error) {
        // User cancelled or error occurred, fall back to clipboard
        console.warn('Web Share API failed:', error);
      }
    }

    // Fallback to clipboard
    return this.copyToClipboard(shareData.url || '');
  }

  /**
   * Copy job URL to clipboard
   */
  async copyToClipboard(url: string): Promise<boolean> {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(url);
        return true;
      } else {
        // Fallback for older browsers
        return this.fallbackCopyToClipboard(url);
      }
    } catch (error) {
      console.error('Failed to copy to clipboard:', error);
      return false;
    }
  }

  /**
   * Share job via email
   */
  shareViaEmail(job: Job, baseUrl: string = window.location.origin): void {
    const subject = encodeURIComponent(`Job Opportunity: ${job.title} at ${job.company.name}`);
    const body = encodeURIComponent(
      `I found this job opportunity that might interest you:\n\n` +
      `${job.title} at ${job.company.name}\n` +
      `Location: ${job.location}\n` +
      `Experience Level: ${job.experience_level}\n\n` +
      `View details: ${baseUrl}/jobs/${job.id}`
    );
    
    window.open(`mailto:?subject=${subject}&body=${body}`, '_blank');
  }

  /**
   * Share job on LinkedIn
   */
  shareOnLinkedIn(job: Job, baseUrl: string = window.location.origin): void {
    const url = encodeURIComponent(`${baseUrl}/jobs/${job.id}`);
    const title = encodeURIComponent(`${job.title} at ${job.company.name}`);
    const summary = encodeURIComponent(job.summary || job.description.substring(0, 200) + '...');
    
    window.open(
      `https://www.linkedin.com/sharing/share-offsite/?url=${url}&title=${title}&summary=${summary}`,
      '_blank',
      'width=600,height=400'
    );
  }

  /**
   * Share job on Twitter
   */
  shareOnTwitter(job: Job, baseUrl: string = window.location.origin): void {
    const text = encodeURIComponent(
      `Check out this job opportunity: ${job.title} at ${job.company.name} #jobs #hiring`
    );
    const url = encodeURIComponent(`${baseUrl}/jobs/${job.id}`);
    
    window.open(
      `https://twitter.com/intent/tweet?text=${text}&url=${url}`,
      '_blank',
      'width=600,height=400'
    );
  }

  /**
   * Generate shareable link with tracking parameters
   */
  generateShareableLink(job: Job, source: string = 'share', baseUrl: string = window.location.origin): string {
    const url = new URL(`${baseUrl}/jobs/${job.id}`);
    url.searchParams.set('utm_source', source);
    url.searchParams.set('utm_medium', 'social');
    url.searchParams.set('utm_campaign', 'job_share');
    return url.toString();
  }

  /**
   * Check if Web Share API is available and supported
   */
  private canUseWebShare(): boolean {
    return 'share' in navigator && typeof navigator.share === 'function';
  }

  /**
   * Fallback method for copying to clipboard in older browsers
   */
  private fallbackCopyToClipboard(text: string): boolean {
    try {
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      
      const successful = document.execCommand('copy');
      document.body.removeChild(textArea);
      
      return successful;
    } catch (error) {
      console.error('Fallback copy failed:', error);
      return false;
    }
  }
}

// Create and export service instance
export const shareService = new ShareService();