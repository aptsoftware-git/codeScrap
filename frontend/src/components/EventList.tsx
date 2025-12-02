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
  Pagination,
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

const EVENTS_PER_PAGE = 50; // Configurable pagination size

const EventList: React.FC<EventListProps> = ({ searchResults }) => {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Show message if no search has been performed yet
  if (!searchResults) {
    return null;
  }

  // Handle error states with user-friendly messages
  if (searchResults.status === 'no_sources') {
    return (
      <Paper elevation={3} sx={{ p: 4, mt: 3, textAlign: 'center' }}>
        <Alert severity="error" sx={{ mb: 2 }}>
          <Typography variant="h6">No Sources Configured</Typography>
        </Alert>
        <Typography variant="body1" color="text.secondary">
          No news sources are enabled. Please configure sources in the backend settings.
        </Typography>
      </Paper>
    );
  }

  if (searchResults.status === 'no_articles') {
    return (
      <Paper elevation={3} sx={{ p: 4, mt: 3, textAlign: 'center' }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="h6">No Articles Scraped</Typography>
        </Alert>
        <Typography variant="body1" color="text.secondary" paragraph>
          Could not scrape articles from {searchResults.sources_scraped} source(s).
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          This might be due to:
        </Typography>
        <Box component="ul" sx={{ textAlign: 'left', maxWidth: 500, mx: 'auto', color: 'text.secondary' }}>
          <li>Network connectivity issues</li>
          <li>Website blocking the requests</li>
          <li>Invalid source configurations</li>
          <li>Backend server issues</li>
        </Box>
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
          <strong>Tip:</strong> Check the backend logs for detailed error messages.
        </Typography>
      </Paper>
    );
  }

  if (searchResults.status === 'no_events') {
    return (
      <Paper elevation={3} sx={{ p: 4, mt: 3, textAlign: 'center' }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          <Typography variant="h6">No Events Extracted</Typography>
        </Alert>
        <Typography variant="body1" color="text.secondary" paragraph>
          Scraped {searchResults.articles_scraped} article(s), but no events could be extracted.
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Try a different search phrase or adjust your filters.
        </Typography>
      </Paper>
    );
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
    // Select all events on current page
    const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
    const endIndex = Math.min(startIndex + EVENTS_PER_PAGE, searchResults.events.length);
    const pageIndices = new Set<number>();
    
    for (let i = startIndex; i < endIndex; i++) {
      pageIndices.add(i);
    }
    
    setSelectedEvents((prev) => new Set([...prev, ...pageIndices]));
  };

  const handleSelectAllPages = () => {
    // Select all events across all pages
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

  const handlePageChange = (_event: React.ChangeEvent<unknown>, page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const sortedEvents = sortEvents(searchResults.events);
  const totalPages = Math.ceil(sortedEvents.length / EVENTS_PER_PAGE);
  const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
  const endIndex = Math.min(startIndex + EVENTS_PER_PAGE, sortedEvents.length);
  const paginatedEvents = sortedEvents.slice(startIndex, endIndex);

  return (
    <>
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Search Results
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Found {searchResults.events.length} events. 
            Processing time: {(searchResults.processing_time_seconds || searchResults.processing_time || 0).toFixed(2)}s
            {totalPages > 1 && ` • Showing ${startIndex + 1}-${endIndex} of ${sortedEvents.length}`}
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
                  disabled={paginatedEvents.length === 0}
                  title="Select all on this page"
                >
                  Page
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<SelectAllIcon />}
                  onClick={handleSelectAllPages}
                  disabled={sortedEvents.length === 0}
                  title="Select all across all pages"
                >
                  All
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
          <>
            <Box>
              {paginatedEvents.map((event) => {
                const originalIndex = searchResults.events.indexOf(event);
                return (
                  <EventCard 
                    key={`${event.title}-${originalIndex}`} 
                    event={event}
                    selected={selectedEvents.has(originalIndex)}
                    onToggleSelect={handleToggleEvent}
                  />
                );
              })}
            </Box>

            {/* Pagination */}
            {totalPages > 1 && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 3 }}>
                <Pagination 
                  count={totalPages}
                  page={currentPage}
                  onChange={handlePageChange}
                  color="primary"
                  size="large"
                  showFirstButton
                  showLastButton
                />
              </Box>
            )}
          </>
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
