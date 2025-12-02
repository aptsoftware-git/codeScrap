/**
 * Type definitions matching the backend models
 */

export enum EventType {
  CONFERENCE = "conference",
  MEETING = "meeting",
  WORKSHOP = "workshop",
  SEMINAR = "seminar",
  WEBINAR = "webinar",
  TRAINING = "training",
  SUMMIT = "summit",
  FORUM = "forum",
  SYMPOSIUM = "symposium",
  HACKATHON = "hackathon",
  COMPETITION = "competition",
  EXHIBITION = "exhibition",
  NETWORKING = "networking",
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
