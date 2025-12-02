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
  date?: string;
  location?: Location;
  description?: string;
  url?: string;
  event_type?: EventType;
  organizer?: string;
  relevance_score?: number;
  source_url?: string;
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
  total_scraped: number;
  total_extracted: number;
  total_matched: number;
  processing_time: number;
  sources_scraped: string[];
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
