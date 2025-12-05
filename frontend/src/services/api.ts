import axios, { AxiosInstance } from 'axios';
import { SearchQuery, SearchResponse, SessionResponse, EventData } from '../types/events';

/**
 * API Service for communicating with the backend
 */
class ApiService {
  private client: AxiosInstance;

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 600000, // 10 minutes for scraping + LLM processing
    });
  }

  /**
   * Execute a search with the given query parameters
   */
  async searchEvents(query: SearchQuery): Promise<SearchResponse> {
    // Clean the query - remove empty strings and undefined values
    // Backend expects null/undefined for optional fields, not empty strings
    const cleanedQuery: Partial<SearchQuery> = {
      phrase: query.phrase.trim(),
    };
    
    if (query.location?.trim()) {
      cleanedQuery.location = query.location.trim();
    }
    
    if (query.event_type) {
      cleanedQuery.event_type = query.event_type;
    }
    
    if (query.date_from) {
      cleanedQuery.date_from = query.date_from;
    }
    
    if (query.date_to) {
      cleanedQuery.date_to = query.date_to;
    }

    console.log('Sending search request:', cleanedQuery);

    const response = await this.client.post<SearchResponse>('/api/v1/search', cleanedQuery);
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
      `/api/v1/export/excel?session_id=${sessionId}`,
      {},
      { responseType: 'blob' }
    );
    return response.data;
  }

  /**
   * Export custom events to Excel
   */
  async exportExcelCustom(events: EventData[]): Promise<Blob> {
    const response = await this.client.post(
      '/api/v1/export/excel/custom',
      events,  // Send events array directly, not wrapped in object
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
