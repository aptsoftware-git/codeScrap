import React, { useState } from 'react';
import {
  Box,
  Button,
  TextField,
  MenuItem,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Alert,
  ListSubheader,
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { EventType, SearchQuery, ProgressUpdate, EventData } from '../types/events';

interface SearchFormProps {
  onSearchStart?: () => void;
  onProgress?: (progress: ProgressUpdate) => void;
  onEventReceived?: (event: EventData) => void;
  onSearchComplete?: (summary: { message: string; total_events: number }) => void;
  onError?: (error: string) => void;
}

// Helper function to get user-friendly event type labels
const getEventTypeLabel = (type: EventType): string => {
  const labels: Record<EventType, string> = {
    // Violence & Security Events
    [EventType.PROTEST]: 'Protest',
    [EventType.DEMONSTRATION]: 'Demonstration',
    [EventType.ATTACK]: 'Attack',
    [EventType.EXPLOSION]: 'Explosion',
    [EventType.BOMBING]: 'Bombing',
    [EventType.SHOOTING]: 'Shooting',
    [EventType.THEFT]: 'Theft',
    [EventType.KIDNAPPING]: 'Kidnapping',
    
    // Cyber Events
    [EventType.CYBER_ATTACK]: 'Cyber Attack',
    [EventType.CYBER_INCIDENT]: 'Cyber Incident',
    [EventType.DATA_BREACH]: 'Data Breach',
    
    // Meetings & Conferences
    [EventType.CONFERENCE]: 'Conference',
    [EventType.MEETING]: 'Meeting',
    [EventType.SUMMIT]: 'Summit',
    
    // Disasters & Accidents
    [EventType.ACCIDENT]: 'Accident',
    [EventType.NATURAL_DISASTER]: 'Natural Disaster',
    
    // Political & Military
    [EventType.ELECTION]: 'Election',
    [EventType.POLITICAL_EVENT]: 'Political Event',
    [EventType.MILITARY_OPERATION]: 'Military Operation',
    
    // Crisis Events
    [EventType.TERRORIST_ACTIVITY]: 'Terrorist Activity',
    [EventType.CIVIL_UNREST]: 'Civil Unrest',
    [EventType.HUMANITARIAN_CRISIS]: 'Humanitarian Crisis',
    
    // Other
    [EventType.OTHER]: 'Other',
  };
  return labels[type] || type;
};

// Organized event type categories
const eventTypeCategories = {
  'Violence & Security': [
    EventType.PROTEST,
    EventType.DEMONSTRATION,
    EventType.ATTACK,
    EventType.EXPLOSION,
    EventType.BOMBING,
    EventType.SHOOTING,
    EventType.THEFT,
    EventType.KIDNAPPING,
  ],
  'Cyber Events': [
    EventType.CYBER_ATTACK,
    EventType.CYBER_INCIDENT,
    EventType.DATA_BREACH,
  ],
  'Meetings & Conferences': [
    EventType.CONFERENCE,
    EventType.MEETING,
    EventType.SUMMIT,
  ],
  'Disasters & Accidents': [
    EventType.ACCIDENT,
    EventType.NATURAL_DISASTER,
  ],
  'Political & Military': [
    EventType.ELECTION,
    EventType.POLITICAL_EVENT,
    EventType.MILITARY_OPERATION,
  ],
  'Crisis Events': [
    EventType.TERRORIST_ACTIVITY,
    EventType.CIVIL_UNREST,
    EventType.HUMANITARIAN_CRISIS,
  ],
  'Other': [
    EventType.OTHER,
  ],
};

const SearchForm: React.FC<SearchFormProps> = ({ 
  onSearchStart, 
  onProgress, 
  onEventReceived, 
  onSearchComplete,
  onError 
}) => {
  const [formData, setFormData] = useState<SearchQuery>({
    phrase: '',
    location: '',
    event_type: undefined,
    date_from: '',
    date_to: '',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof SearchQuery) => (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const value = event.target.value;
    setFormData((prev) => ({
      ...prev,
      [field]: value || undefined,
    }));
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    // Validation
    if (!formData.phrase.trim()) {
      setError('Please enter a search phrase');
      return;
    }

    // Date validation
    if (formData.date_from && formData.date_to) {
      const fromDate = new Date(formData.date_from);
      const toDate = new Date(formData.date_to);
      if (fromDate > toDate) {
        setError('Start date must be before end date');
        return;
      }
    }

    try {
      setLoading(true);
      if (onSearchStart) {
        onSearchStart();
      }

      // Import streaming service
      const { streamService } = await import('../services/streamService');
      
      // Start streaming search
      streamService.startStreaming(formData, {
        onProgress: (progress) => {
          if (onProgress) {
            onProgress(progress);
          }
        },
        onEvent: (eventData) => {
          if (onEventReceived) {
            onEventReceived(eventData);
          }
        },
        onComplete: (summary) => {
          setLoading(false);
          if (onSearchComplete) {
            onSearchComplete(summary);
          }
        },
        onCancelled: (summary) => {
          setLoading(false);
          if (onSearchComplete) {
            onSearchComplete(summary);
          }
        },
        onError: (errorMsg) => {
          setLoading(false);
          setError(errorMsg);
          if (onError) {
            onError(errorMsg);
          }
        },
      });
    } catch (err) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while searching. Please try again.';
      setError(errorMessage);
      setLoading(false);
      if (onError) {
        onError(errorMessage);
      }
    }
  };

  const handleReset = () => {
    setFormData({
      phrase: '',
      location: '',
      event_type: undefined,
      date_from: '',
      date_to: '',
    });
    setError(null);
  };

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
      <Box sx={{ width: '100%', maxWidth: { xs: '100%', md: '66.666%' } }}>
        {/* Search Form */}
        <Paper elevation={3} sx={{ p: 3, mb: 3, width: '100%' }}>
          <Typography variant="h5" gutterBottom>
            Search for Events
          </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
            {error}
          </Alert>
        )}

        <Box component="form" onSubmit={handleSubmit}>
        <Grid container spacing={2}>
          {/* Search Phrase */}
          <Grid size={{ xs: 12 }}>
            <TextField
              fullWidth
              required
              label="Search Phrase"
              placeholder="e.g., AI, Machine Learning, Cybersecurity"
              value={formData.phrase}
              onChange={handleChange('phrase')}
              disabled={loading}
              helperText="Enter keywords to search for relevant events"
            />
          </Grid>

          {/* Location */}
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              label="Location (Optional)"
              placeholder="e.g., New York, London, Online"
              value={formData.location}
              onChange={handleChange('location')}
              disabled={loading}
              helperText="City, state, country, or 'Online'"
            />
          </Grid>

          {/* Event Type */}
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              select
              label="Event Type (Optional)"
              value={formData.event_type || ''}
              onChange={handleChange('event_type')}
              disabled={loading}
              helperText="Filter by event type"
            >
              <MenuItem value="">All Types</MenuItem>
              {Object.entries(eventTypeCategories).map(([category, types]) => [
                <ListSubheader key={category}>{category}</ListSubheader>,
                ...types.map((type) => (
                  <MenuItem key={type} value={type}>
                    {getEventTypeLabel(type)}
                  </MenuItem>
                ))
              ])}
            </TextField>
          </Grid>

          {/* Date From */}
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              type="date"
              label="Start Date (Optional)"
              value={formData.date_from}
              onChange={handleChange('date_from')}
              disabled={loading}
              InputLabelProps={{ shrink: true }}
              helperText="Filter events from this date"
            />
          </Grid>

          {/* Date To */}
          <Grid size={{ xs: 12, md: 6 }}>
            <TextField
              fullWidth
              type="date"
              label="End Date (Optional)"
              value={formData.date_to}
              onChange={handleChange('date_to')}
              disabled={loading}
              InputLabelProps={{ shrink: true }}
              helperText="Filter events until this date"
            />
          </Grid>

          {/* Action Buttons */}
          <Grid size={{ xs: 12 }}>
            <Box sx={{ display: 'flex', gap: 2, justifyContent: 'flex-end' }}>
              <Button
                type="button"
                variant="outlined"
                onClick={handleReset}
                disabled={loading}
              >
                Reset
              </Button>
              <Button
                type="submit"
                variant="contained"
                startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
                disabled={loading}
              >
                {loading ? 'Searching...' : 'Search'}
              </Button>
            </Box>
          </Grid>
        </Grid>
      </Box>

      {loading && (
        <Box sx={{ mt: 2, textAlign: 'center' }}>
          <Typography variant="body2" color="text.secondary">
            Searching and analyzing events... This may take a minute.
          </Typography>
        </Box>
      )}
        </Paper>
      </Box>
    </Box>
  );
};

export default SearchForm;
