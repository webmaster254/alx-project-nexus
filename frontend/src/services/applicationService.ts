import { httpClient } from './index';
import type { Application, ApplicationData, ApplicationDocument } from '../types';

export class ApplicationService {
  private baseUrl = '/applications';

  /**
   * Submit a job application
   */
  async submitApplication(data: ApplicationData): Promise<Application> {
    const formData = new FormData();
    
    // Add basic application data
    formData.append('job', data.job.toString());
    formData.append('cover_letter', data.cover_letter);

    // Add documents
    data.documents.forEach((doc, index) => {
      formData.append(`documents[${index}][document_type]`, doc.document_type);
      formData.append(`documents[${index}][title]`, doc.title);
      formData.append(`documents[${index}][file]`, doc.file);
    });

    const response = await httpClient.postMultipart<Application>(`${this.baseUrl}/`, formData);
    return response.data;
  }

  /**
   * Get user's applications
   */
  async getMyApplications(): Promise<Application[]> {
    const response = await httpClient.get<Application[]>(`${this.baseUrl}/my/`);
    return response.data;
  }

  /**
   * Get a specific application
   */
  async getApplication(id: number): Promise<Application> {
    const response = await httpClient.get<Application>(`${this.baseUrl}/${id}/`);
    return response.data;
  }

  /**
   * Withdraw an application
   */
  async withdrawApplication(id: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${id}/`);
  }

  /**
   * Upload a document for an application
   */
  async uploadDocument(
    applicationId: number,
    file: File,
    documentType: 'resume' | 'cover_letter' | 'portfolio',
    title: string
  ): Promise<ApplicationDocument> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);
    formData.append('title', title);

    const response = await httpClient.postMultipart<ApplicationDocument>(
      `${this.baseUrl}/${applicationId}/documents/`,
      formData
    );

    return response.data;
  }

  /**
   * Delete a document
   */
  async deleteDocument(applicationId: number, documentId: number): Promise<void> {
    await httpClient.delete(`${this.baseUrl}/${applicationId}/documents/${documentId}/`);
  }

  /**
   * Check if user can apply to a job
   */
  async canApplyToJob(jobId: number): Promise<{ can_apply: boolean; reason?: string }> {
    const response = await httpClient.get<{ can_apply: boolean; reason?: string }>(
      `/jobs/${jobId}/can-apply/`
    );
    return response.data;
  }
}

// Create and export service instance
export const applicationService = new ApplicationService();