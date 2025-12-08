/**
 * Type definitions matching the backend models
 */

export enum EventType {
  // Violence & Security Events
  PROTEST = "protest",
  DEMONSTRATION = "demonstration",
  ATTACK = "attack",
  EXPLOSION = "explosion",
  BOMBING = "bombing",
  SHOOTING = "shooting",
  THEFT = "theft",
  KIDNAPPING = "kidnapping",
  
  // Cyber Events
  CYBER_ATTACK = "cyber_attack",
  CYBER_INCIDENT = "cyber_incident",
  DATA_BREACH = "data_breach",
  
  // Meetings & Conferences
  CONFERENCE = "conference",
  MEETING = "meeting",
  SUMMIT = "summit",
  
  // Disasters & Accidents
  ACCIDENT = "accident",
  NATURAL_DISASTER = "natural_disaster",
  
  // Political & Military
  ELECTION = "election",
  POLITICAL_EVENT = "political_event",
  MILITARY_OPERATION = "military_operation",
  
  // Crisis Events
  TERRORIST_ACTIVITY = "terrorist_activity",
  CIVIL_UNREST = "civil_unrest",
  HUMANITARIAN_CRISIS = "humanitarian_crisis",
  
  // Other
  OTHER = "other"
}

export interface Location {
  city: string;
  state?: string;
  country?: string;
  venue?: string;
}

export interface Casualties {
  killed?: number;
  injured?: number;
}

export interface EventData {
  // Core event information
  event_type: EventType;
  event_sub_type?: string;  // Secondary classification (e.g., "suicide bombing")
  title: string;
  summary: string;
  
  // Perpetrator information
  perpetrator?: string;
  perpetrator_type?: string;  // Classification of perpetrator
  
  // Location details
  location: Location;
  
  // Temporal information
  event_date?: string;  // ISO datetime string
  event_time?: string;  // Time of day (HH:MM or text)
  
  // People and organizations
  participants?: string[];
  organizations?: string[];
  
  // Impact assessment
  casualties?: Casualties;
  impact?: string;
  
  // Source metadata
  source_name?: string;
  source_url?: string;
  article_published_date?: string;  // ISO datetime string
  collection_timestamp?: string;  // When system collected the content
  
  // Quality metrics
  confidence: number;
  
  // Raw content
  full_content?: string;
  
  // For compatibility (old fields)
  date?: string;  // Alias for event_date
  url?: string;   // Alias for source_url
  organizer?: string;  // Deprecated
  description?: string;  // Deprecated
  relevance_score?: number;  // Added by matcher
}

export interface SearchQuery {
  phrase: string;
  location?: string;
  event_type?: EventType;
  date_from?: string;
  date_to?: string;
}

export interface SearchResponse {
  session_id: string;
  query: SearchQuery;
  events: EventData[];
  total_events?: number;  // For backward compatibility
  total_scraped?: number;
  total_extracted?: number;
  total_matched?: number;
  processing_time?: number;
  processing_time_seconds?: number;  // New field from backend
  articles_scraped?: number;  // New field from backend
  sources_scraped?: number | string[];  // Can be count or array
  status?: string;  // Status: 'success', 'no_sources', 'no_articles', 'no_events'
  message?: string;  // Status message
}

export interface SessionResponse {
  session_id: string;
  query: SearchQuery;
  events: EventData[];
  total_scraped: number;
  total_extracted: number;
  total_matched: number;
  processing_time: number;
  sources_scraped: string[];
  timestamp: string;
}

// Streaming Types
export interface ProgressUpdate {
  current: number;
  total: number;
  status: string;
  percentage: number;
}

export interface StreamEvent {
  event_type: 'session' | 'progress' | 'event' | 'complete' | 'cancelled' | 'error';
  session_id?: string;
  data?: ProgressUpdate | EventData | { message: string; total_events?: number; articles_processed?: number; processing_time?: number };
}

export interface StreamCallbacks {
  onSession?: (sessionId: string) => void;
  onProgress?: (progress: ProgressUpdate) => void;
  onEvent?: (event: EventData, index: number) => void;
  onComplete?: (summary: { message: string; total_events: number; articles_processed: number; processing_time: number }) => void;
  onCancelled?: (summary: { message: string; total_events: number }) => void;
  onError?: (error: string) => void;
}
