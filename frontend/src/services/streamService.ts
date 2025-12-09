import { SearchQuery, StreamCallbacks, ProgressUpdate, EventData } from '../types/events';
import { getLLMConfig } from '../components/LLMConfig';

/**
 * Service for handling Server-Sent Events (SSE) streaming from backend
 */
export class StreamService {
  private eventSource: EventSource | null = null;
  private baseURL: string;
  private currentSessionId: string | null = null;
  private currentCallbacks: StreamCallbacks | null = null; // Store callbacks for cancel

  constructor(baseURL: string = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000') {
    this.baseURL = baseURL;
  }

  /**
   * Start streaming search with real-time updates
   */
  startStreaming(query: SearchQuery, callbacks: StreamCallbacks): void {
    // Close any existing connection
    this.close();

    // Store callbacks for later use (e.g., in cancel method)
    this.currentCallbacks = callbacks;

    // Get LLM configuration
    const llmConfig = getLLMConfig();

    // Build query parameters
    const params = new URLSearchParams();
    params.append('phrase', query.phrase);
    if (query.location) params.append('location', query.location);
    if (query.event_type) params.append('event_type', query.event_type);
    if (query.date_from) params.append('date_from', query.date_from);
    if (query.date_to) params.append('date_to', query.date_to);
    
    // Add LLM configuration
    params.append('llm_provider', llmConfig.provider);
    params.append('llm_model', llmConfig.model);

    const url = `${this.baseURL}/api/v1/search/stream?${params.toString()}`;
    console.log('[STREAM] Opening SSE connection:', url);

    this.eventSource = new EventSource(url);

    // Handle 'session' event - get session ID
    this.eventSource.addEventListener('session', (event) => {
      try {
        const data = JSON.parse(event.data);
        this.currentSessionId = data.session_id;
        if (callbacks.onSession && this.currentSessionId) {
          callbacks.onSession(this.currentSessionId);
        }
      } catch (error) {
        console.error('[SESSION] Error parsing session event:', error);
      }
    });

    // Handle 'progress' events
    this.eventSource.addEventListener('progress', (event) => {
      try {
        const progress: ProgressUpdate = JSON.parse(event.data);
        if (callbacks.onProgress) {
          callbacks.onProgress(progress);
        }
      } catch (error) {
        console.error('[PROGRESS] Error parsing progress event:', error);
      }
    });

    // Handle 'event' events - new event extracted
    this.eventSource.addEventListener('event', (event) => {
      try {
        const data = JSON.parse(event.data);
        const eventData: EventData = data.event;
        const index: number = data.index || 0;
        if (callbacks.onEvent) {
          callbacks.onEvent(eventData, index);
        }
      } catch (error) {
        console.error('[EVENT] Error parsing event:', error);
      }
    });

    // Handle 'complete' event
    this.eventSource.addEventListener('complete', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (callbacks.onComplete) {
          callbacks.onComplete({
            message: data.message || 'Search completed',
            total_events: data.total_events || 0,
            articles_processed: data.articles_processed || 0,
            processing_time: data.processing_time || 0,
          });
        }
        this.close();
      } catch (error) {
        console.error('[COMPLETE] Error parsing complete event:', error);
      }
    });

    // Handle 'cancelled' event
    this.eventSource.addEventListener('cancelled', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (callbacks.onCancelled) {
          callbacks.onCancelled({
            message: data.message || 'Search cancelled',
            total_events: data.total_events || 0,
          });
        }
        this.close();
      } catch (error) {
        console.error('[CANCELLED] Error parsing cancelled event:', error);
      }
    });

    // Handle 'error' events
    this.eventSource.addEventListener('error', (event) => {
      try {
        const data = JSON.parse((event as MessageEvent).data);
        console.error('[ERROR] Stream error:', data);
        if (callbacks.onError) {
          callbacks.onError(data.message || 'Unknown error');
        }
      } catch {
        // Connection error (not a message error)
        console.error('[ERROR] SSE connection error');
        if (callbacks.onError) {
          callbacks.onError('Connection to server lost');
        }
      }
      this.close();
    });

    // Handle connection errors
    this.eventSource.onerror = () => {
      console.error('[ERROR] EventSource connection error');
      if (callbacks.onError && this.eventSource?.readyState === EventSource.CLOSED) {
        callbacks.onError('Connection to server lost');
      }
      this.close();
    };
  }

  /**
   * Cancel the current search session
   */
  async cancel(): Promise<void> {
    if (!this.currentSessionId) {
      console.warn('No active session to cancel');
      
      // Trigger onCancelled callback BEFORE closing
      if (this.currentCallbacks?.onCancelled) {
        this.currentCallbacks.onCancelled({
          message: 'Search cancelled',
          total_events: 0,
        });
      }
      
      this.close();
      return;
    }

    const sessionId = this.currentSessionId;

    try {
      const url = `${this.baseURL}/api/v1/search/cancel/${sessionId}`;
      
      const response = await fetch(url, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`Cancel request failed: ${response.statusText}`);
      }

      const result = await response.json();
      
      // Trigger onCancelled callback BEFORE closing
      if (this.currentCallbacks?.onCancelled) {
        this.currentCallbacks.onCancelled({
          message: result.message || 'Search cancelled',
          total_events: result.events_extracted || 0,
        });
      }
      
      this.close();
    } catch (error) {
      console.error('Error cancelling search:', error);
      
      // Trigger callback BEFORE closing
      if (this.currentCallbacks?.onCancelled) {
        this.currentCallbacks.onCancelled({
          message: 'Search cancelled',
          total_events: 0,
        });
      }
      
      this.close();
      throw error;
    }
  }

  /**
   * Close the SSE connection
   */
  close(): void {
    if (this.eventSource) {
      this.eventSource.close();
      this.eventSource = null;
      this.currentSessionId = null;
      this.currentCallbacks = null;
    }
  }
}

// Singleton instance
export const streamService = new StreamService();
