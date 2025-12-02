import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  MenuItem,
  TextField,
  Grid,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  FileDownload as DownloadIcon,
  SortByAlpha as SortIcon,
  SelectAll as SelectAllIcon,
  Deselect as DeselectIcon,
} from '@mui/icons-material';
import EventCard from './EventCard';
import { EventData, SearchResponse } from '../types/events';
import apiService from '../services/api';

interface EventListProps {
  searchResults: SearchResponse | null;
}

type SortOption = 'relevance' | 'date' | 'title';

const EventList: React.FC<EventListProps> = ({ searchResults }) => {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set());
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  if (!searchResults) {
    return null;
  }

  const sortEvents = (events: EventData[]): EventData[] => {
    const sorted = [...events];
    
    switch (sortBy) {
      case 'relevance':
        return sorted.sort((a, b) => 
          (b.relevance_score || 0) - (a.relevance_score || 0)
        );
      case 'date':
        return sorted.sort((a, b) => {
          if (!a.date) return 1;
          if (!b.date) return -1;
          return new Date(a.date).getTime() - new Date(b.date).getTime();
        });
      case 'title':
        return sorted.sort((a, b) => 
          a.title.localeCompare(b.title)
        );
      default:
        return sorted;
    }
  };

  const handleToggleEvent = (event: EventData) => {
    const index = searchResults.events.indexOf(event);
    if (index === -1) return;

    setSelectedEvents((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  const handleSelectAll = () => {
    const allIndices = new Set(searchResults.events.map((_, index) => index));
    setSelectedEvents(allIndices);
  };

  const handleDeselectAll = () => {
    setSelectedEvents(new Set());
  };

  const handleExport = async () => {
    try {
      setExporting(true);
      setExportError(null);

      let blob: Blob;
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `events_${searchResults.query.phrase.replace(/\s+/g, '_')}_${timestamp}.xlsx`;

      if (selectedEvents.size === 0) {
        // Export all events from session
        blob = await apiService.exportExcelFromSession(searchResults.session_id);
      } else {
        // Export selected events
        const selectedEventsArray = Array.from(selectedEvents)
          .map(index => searchResults.events[index])
          .filter(Boolean);
        blob = await apiService.exportExcelCustom(selectedEventsArray, searchResults.query);
      }
      
      apiService.downloadBlob(blob, filename);
      setExportSuccess(true);
    } catch (error) {
      console.error('Export error:', error);
      setExportError('Failed to export results. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const handleCloseSnackbar = () => {
    setExportSuccess(false);
    setExportError(null);
  };

  const sortedEvents = sortEvents(searchResults.events);

  return (
    <>
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Search Results
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Found {searchResults.total_matched} matching events from {searchResults.total_extracted} extracted events 
            ({searchResults.total_scraped} articles scraped). Processing time: {searchResults.processing_time.toFixed(2)}s
          </Typography>

          {/* Controls */}
          <Grid container spacing={2} sx={{ alignItems: 'center' }}>
            {/* Sort Controls */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <TextField
                fullWidth
                select
                size="small"
                label="Sort By"
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as SortOption)}
                InputProps={{
                  startAdornment: <SortIcon sx={{ mr: 1 }} />,
                }}
              >
                <MenuItem value="relevance">Relevance</MenuItem>
                <MenuItem value="date">Date</MenuItem>
                <MenuItem value="title">Title</MenuItem>
              </TextField>
            </Grid>
            
            {/* Selection Controls */}
            <Grid size={{ xs: 12, sm: 6, md: 3 }}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<SelectAllIcon />}
                  onClick={handleSelectAll}
                  disabled={sortedEvents.length === 0}
                >
                  Select All
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DeselectIcon />}
                  onClick={handleDeselectAll}
                  disabled={selectedEvents.size === 0}
                >
                  Clear
                </Button>
              </Box>
            </Grid>

            {/* Export Button */}
            <Grid size={{ xs: 12, sm: 12, md: 6 }}>
              <Button
                fullWidth
                variant="contained"
                color="success"
                startIcon={<DownloadIcon />}
                onClick={handleExport}
                disabled={exporting || sortedEvents.length === 0}
              >
                {exporting 
                  ? 'Exporting...' 
                  : selectedEvents.size > 0 
                    ? `Export ${selectedEvents.size} Selected to Excel`
                    : 'Export All to Excel'
                }
              </Button>
            </Grid>
          </Grid>

          {/* Selection Info */}
          {selectedEvents.size > 0 && (
            <Alert severity="info" sx={{ mt: 2 }}>
              {selectedEvents.size} event{selectedEvents.size !== 1 ? 's' : ''} selected for export
            </Alert>
          )}
        </Box>

        {/* Events */}
        {sortedEvents.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <Typography variant="h6" color="text.secondary">
              No events found matching your criteria
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Try adjusting your search filters or using different keywords
            </Typography>
          </Box>
        ) : (
          <Box>
            {sortedEvents.map((event, index) => {
              const originalIndex = searchResults.events.indexOf(event);
              return (
                <EventCard 
                  key={`${event.title}-${index}`} 
                  event={event}
                  selected={selectedEvents.has(originalIndex)}
                  onToggleSelect={handleToggleEvent}
                />
              );
            })}
          </Box>
        )}
      </Paper>

      {/* Success/Error Snackbars */}
      <Snackbar
        open={exportSuccess}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
          Excel file exported successfully!
        </Alert>
      </Snackbar>

      <Snackbar
        open={!!exportError}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
          {exportError}
        </Alert>
      </Snackbar>
    </>
  );
};

export default EventList;
