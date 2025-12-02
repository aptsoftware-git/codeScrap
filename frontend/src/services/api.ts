import axios, { AxiosInstance } from 'axios';
import { SearchQuery, SearchResponse, SessionResponse, EventData } from '../types/events';

/**
 * API Service for communicating with the backend
 */
class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 120000, // 2 minutes for scraping operations
    });
  }

  /**
   * Execute a search with the given query parameters
   */
  async searchEvents(query: SearchQuery): Promise<SearchResponse> {
    const response = await this.client.post<SearchResponse>('/api/v1/search', query);
    return response.data;
  }

  /**
   * Get results from a previous search session
   */
  async getSession(sessionId: string): Promise<SessionResponse> {
    const response = await this.client.get<SessionResponse>(`/api/v1/search/session/${sessionId}`);
    return response.data;
  }

  /**
   * Export events to Excel from a session
   */
  async exportExcelFromSession(sessionId: string): Promise<Blob> {
    const response = await this.client.post(
      '/api/v1/export/excel',
      { session_id: sessionId },
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Export custom events to Excel
   */
  async exportExcelCustom(events: EventData[], query: SearchQuery): Promise<Blob> {
    const response = await this.client.post(
      '/api/v1/export/excel/custom',
      { events, query },
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Download a blob as a file
   */
  downloadBlob(blob: Blob, filename: string): void {
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default apiService;
