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
} from '@mui/material';
import { Search as SearchIcon } from '@mui/icons-material';
import { EventType, SearchQuery, SearchResponse } from '../types/events';

interface SearchFormProps {
  onSearchComplete: (results: SearchResponse) => void;
  onSearchStart?: () => void;
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearchComplete, onSearchStart }) => {
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

      // Import API service dynamically to avoid circular dependencies
      const { apiService } = await import('../services/api');
      
      const results = await apiService.searchEvents(formData);
      onSearchComplete(results);
    } catch (err: unknown) {
      console.error('Search error:', err);
      const errorMessage = err instanceof Error 
        ? err.message 
        : 'An error occurred while searching. Please try again.';
      setError(errorMessage);
    } finally {
      setLoading(false);
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
    <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
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
              {Object.values(EventType).map((type) => (
                <MenuItem key={type} value={type}>
                  {type.charAt(0).toUpperCase() + type.slice(1)}
                </MenuItem>
              ))}
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
  );
};

export default SearchForm;
