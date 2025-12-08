import React from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  IconButton,
  Table,
  TableBody,
  TableRow,
  TableCell,
  Link,
  Chip,
  Box,
  Typography,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { EventData } from '../types/events';
import { format, parseISO } from 'date-fns';

interface EventDetailsModalProps {
  event: EventData;
  open: boolean;
  onClose: () => void;
}

export const EventDetailsModal: React.FC<EventDetailsModalProps> = ({ event, open, onClose }) => {
  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'N/A';
    try {
      const date = parseISO(dateString);
      return format(date, 'PPP p'); // Format with time
    } catch {
      return dateString;
    }
  };

  const formatPerpetratorType = (type: string | undefined): string => {
    if (!type) return '';
    // Convert snake_case to Title Case
    return type
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const formatLocation = (): string => {
    if (!event.location) return 'N/A';
    const parts = [
      event.location.venue,
      event.location.city,
      event.location.state,
      event.location.country,
    ].filter(Boolean);
    return parts.length > 0 ? parts.join(', ') : 'N/A';
  };

  const getEventTypeColor = (type: string): 'error' | 'warning' | 'info' | 'success' => {
    const lowerType = type.toLowerCase();
    if (lowerType.includes('attack') || lowerType.includes('shooting') || lowerType.includes('bombing')) return 'error';
    if (lowerType.includes('riot') || lowerType.includes('violence')) return 'warning';
    if (lowerType.includes('protest') || lowerType.includes('demonstration')) return 'info';
    return 'success';
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">Event Details</Typography>
        <IconButton onClick={onClose} size="small">
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      <DialogContent dividers>
        <Table size="small">
          <TableBody>
            {/* Event Time */}
            {event.event_time && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', width: '35%' }}>Event Time</TableCell>
                <TableCell>{event.event_time}</TableCell>
              </TableRow>
            )}

            {/* Event Type */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Event Type</TableCell>
              <TableCell>
                <Chip
                  label={event.event_type}
                  size="small"
                  color={getEventTypeColor(event.event_type)}
                />
              </TableCell>
            </TableRow>

            {/* Event Sub-Type */}
            {event.event_sub_type && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Event Sub-Type</TableCell>
                <TableCell>{event.event_sub_type}</TableCell>
              </TableRow>
            )}

            {/* Event Title */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Event Title</TableCell>
              <TableCell>{event.title}</TableCell>
            </TableRow>

            {/* Event Summary */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Event Summary</TableCell>
              <TableCell>{event.summary || 'N/A'}</TableCell>
            </TableRow>

            {/* Perpetrator */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Perpetrator</TableCell>
              <TableCell>{event.perpetrator || event.organizer || 'N/A'}</TableCell>
            </TableRow>

            {/* Perpetrator Type */}
            {event.perpetrator_type && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Perpetrator Type</TableCell>
                <TableCell>{formatPerpetratorType(event.perpetrator_type)}</TableCell>
              </TableRow>
            )}

            {/* Location (Full) */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Location (Full)</TableCell>
              <TableCell>{formatLocation()}</TableCell>
            </TableRow>

            {/* City/Town */}
            {event.location?.city && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>City/Town</TableCell>
                <TableCell>{event.location.city}</TableCell>
              </TableRow>
            )}

            {/* State/Province */}
            {event.location?.state && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>State/Province</TableCell>
                <TableCell>{event.location.state}</TableCell>
              </TableRow>
            )}

            {/* Country */}
            {event.location?.country && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Country</TableCell>
                <TableCell>{event.location.country}</TableCell>
              </TableRow>
            )}

            {/* Individuals Involved */}
            {event.participants && event.participants.length > 0 && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Individuals Involved</TableCell>
                <TableCell>{event.participants.join(', ')}</TableCell>
              </TableRow>
            )}

            {/* Organizations Involved */}
            {event.organizations && event.organizations.length > 0 && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Organizations Involved</TableCell>
                <TableCell>{event.organizations.join(', ')}</TableCell>
              </TableRow>
            )}

            {/* Casualties */}
            {event.casualties && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Casualties</TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 2 }}>
                    {event.casualties.killed !== undefined && (
                      <Chip label={`Killed: ${event.casualties.killed}`} size="small" color="error" />
                    )}
                    {event.casualties.injured !== undefined && (
                      <Chip label={`Injured: ${event.casualties.injured}`} size="small" color="warning" />
                    )}
                  </Box>
                </TableCell>
              </TableRow>
            )}

            {/* Source Name */}
            {event.source_name && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Source Name</TableCell>
                <TableCell>{event.source_name}</TableCell>
              </TableRow>
            )}

            {/* Source URL */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Source URL</TableCell>
              <TableCell>
                {(event.source_url || event.url) ? (
                  <Link href={event.source_url || event.url} target="_blank" rel="noopener noreferrer">
                    {event.source_url || event.url}
                  </Link>
                ) : (
                  'N/A'
                )}
              </TableCell>
            </TableRow>

            {/* Publication Date */}
            {event.article_published_date && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Publication Date</TableCell>
                <TableCell>{formatDate(event.article_published_date)}</TableCell>
              </TableRow>
            )}

            {/* Event Date */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Event Date</TableCell>
              <TableCell>{formatDate(event.event_date || event.date)}</TableCell>
            </TableRow>

            {/* Extraction Confidence */}
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold' }}>Extraction Confidence</TableCell>
              <TableCell>
                <Chip
                  label={`${(event.confidence * 100).toFixed(0)}%`}
                  size="small"
                  color={event.confidence >= 0.8 ? 'success' : event.confidence >= 0.6 ? 'warning' : 'error'}
                />
              </TableCell>
            </TableRow>

            {/* Collection Timestamp */}
            {event.collection_timestamp && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold' }}>Collection Timestamp</TableCell>
                <TableCell>{formatDate(event.collection_timestamp)}</TableCell>
              </TableRow>
            )}

            {/* Full Content */}
            {event.full_content && (
              <TableRow>
                <TableCell sx={{ fontWeight: 'bold', verticalAlign: 'top' }}>Full Content</TableCell>
                <TableCell>
                  <Box
                    sx={{
                      maxHeight: 200,
                      overflowY: 'auto',
                      bgcolor: 'grey.50',
                      p: 1,
                      borderRadius: 1,
                    }}
                  >
                    <Typography variant="body2" sx={{ whiteSpace: 'pre-wrap' }}>
                      {event.full_content}
                    </Typography>
                  </Box>
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </DialogContent>
    </Dialog>
  );
};
