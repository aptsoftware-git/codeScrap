import React, { useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Chip,
  Box,
  Link,
  Checkbox,
  CardActionArea,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  IconButton,
} from '@mui/material';
import {
  Event as EventIcon,
  LocationOn as LocationIcon,
  CalendarToday as CalendarIcon,
  Business as BusinessIcon,
  Close as CloseIcon,
  Article as ArticleIcon,
  Info as InfoIcon,
  Link as LinkIcon,
} from '@mui/icons-material';
import { EventData } from '../types/events';
import { format, parseISO } from 'date-fns';
import { EventDetailsModal } from './EventDetailsModal';

interface EventCardProps {
  event: EventData;
  selected?: boolean;
  onToggleSelect?: (event: EventData) => void;
}

const EventCard: React.FC<EventCardProps> = ({ event, selected = false, onToggleSelect }) => {
  const [showFullDescription, setShowFullDescription] = useState(false);
  const [showFullTextModal, setShowFullTextModal] = useState(false);
  const [showDetailsModal, setShowDetailsModal] = useState(false);
  
  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Date TBD';
    try {
      const date = parseISO(dateString);
      return format(date, 'PPP'); // e.g., "April 29, 2023"
    } catch {
      return dateString;
    }
  };

  const formatLocation = (): string => {
    if (!event.location) return 'Location TBD';
    const { city, state, country, venue } = event.location;
    const parts = [venue, city, state, country].filter(Boolean);
    return parts.join(', ');
  };

  const getRelevanceColor = (score: number | undefined): 'success' | 'warning' | 'default' => {
    if (!score) return 'default';
    if (score >= 0.7) return 'success';
    if (score >= 0.5) return 'warning';
    return 'default';
  };

  const handleCardClick = () => {
    if (onToggleSelect) {
      onToggleSelect(event);
    }
  };

  return (
    <Card 
      sx={{ 
        mb: 2, 
        '&:hover': { boxShadow: 6 },
        border: selected ? '2px solid' : '1px solid',
        borderColor: selected ? 'primary.main' : 'divider',
        transition: 'all 0.2s ease-in-out',
      }}
    >
      <CardActionArea onClick={handleCardClick} disabled={!onToggleSelect}>
        <CardContent>
          {/* Checkbox and Title */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
            <Box sx={{ display: 'flex', alignItems: 'flex-start', flex: 1 }}>
              {onToggleSelect && (
                <Checkbox
                  checked={selected}
                  onChange={(e) => {
                    e.stopPropagation();
                    onToggleSelect(event);
                  }}
                  sx={{ mt: -1, ml: -1 }}
                />
              )}
              <Typography variant="h6" component="h3" sx={{ flex: 1 }}>
                {event.url ? (
                  <Link 
                    href={event.url} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                    underline="hover"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {event.title}
                  </Link>
                ) : (
                  event.title
                )}
              </Typography>
            </Box>
            {event.event_type && (
              <Chip
                icon={<EventIcon />}
                label={event.event_type}
                size="small"
                sx={{ ml: 1 }}
              />
            )}
          </Box>

        {/* Summary */}
        {event.summary && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-wrap' }}>
              {(() => {
                const lines = event.summary.split('\n');
                if (showFullDescription || lines.length <= 3) {
                  return event.summary;
                }
                return lines.slice(0, 3).join('\n') + '...';
              })()}
            </Typography>
            {event.summary.split('\n').length > 3 && (
              <Button
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowFullDescription(!showFullDescription);
                }}
                sx={{ mt: 0.5, textTransform: 'none' }}
              >
                {showFullDescription ? 'Show Less' : 'Show More'}
              </Button>
            )}
          </Box>
        )}

        {/* Event Details */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 2, mb: 1 }}>
          {/* Date */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <CalendarIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {formatDate(event.event_date || event.date)}
            </Typography>
          </Box>

          {/* Location */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <LocationIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {formatLocation()}
            </Typography>
          </Box>

          {/* Perpetrator */}
          {(event.perpetrator || event.organizer) && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <BusinessIcon fontSize="small" color="action" />
              <Typography variant="body2" color="text.secondary">
                {event.perpetrator || event.organizer}
              </Typography>
            </Box>
          )}
        </Box>

        {/* Relevance Score and Source */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 2, gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
            {event.relevance_score !== undefined && (
              <Chip
                label={`Relevance: ${(event.relevance_score * 100).toFixed(0)}%`}
                size="small"
                color={getRelevanceColor(event.relevance_score)}
              />
            )}
            {/* View Details Button */}
            <Button
              variant="outlined"
              size="small"
              startIcon={<InfoIcon />}
              onClick={(e) => {
                e.stopPropagation();
                setShowDetailsModal(true);
              }}
            >
              Details
            </Button>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            {event.full_content && (
              <Link
                component="button"
                variant="caption"
                underline="hover"
                onClick={(e) => {
                  e.stopPropagation();
                  setShowFullTextModal(true);
                }}
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                <ArticleIcon fontSize="small" />
                Full Text
              </Link>
            )}
            {event.source_url && (
              <Link
                href={event.source_url}
                target="_blank"
                rel="noopener noreferrer"
                variant="caption"
                underline="hover"
                onClick={(e) => e.stopPropagation()}
                sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}
              >
                <LinkIcon fontSize="small" />
                Source
              </Link>
            )}
          </Box>
        </Box>
      </CardContent>
      </CardActionArea>

      {/* Full Text Modal */}
      <Dialog
        open={showFullTextModal}
        onClose={() => setShowFullTextModal(false)}
        maxWidth="md"
        fullWidth
        scroll="paper"
      >
        <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Full Article Content</Typography>
          <IconButton onClick={() => setShowFullTextModal(false)} size="small">
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        <DialogContent dividers>
          <Typography variant="h6" gutterBottom>
            {event.title}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph sx={{ whiteSpace: 'pre-wrap' }}>
            {event.full_content}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowFullTextModal(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Event Details Modal */}
      <EventDetailsModal
        event={event}
        open={showDetailsModal}
        onClose={() => setShowDetailsModal(false)}
      />
    </Card>
  );
};

export default EventCard;
