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

export interface EventData {
  title: string;
  summary?: string;  // Event summary from LLM extraction
  date?: string;
  location?: Location;
  description?: string;
  url?: string;
  event_type?: EventType;
  organizer?: string;
  relevance_score?: number;
  source_url?: string;
  full_content?: string;  // Complete article text
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
