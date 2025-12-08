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
import { EventData } from '../types/events';
import { apiService } from '../services/api';

interface EventListProps {
  events: EventData[];
}

type SortOption = 'relevance' | 'date' | 'title';

const EVENTS_PER_PAGE = 50;

const EventList: React.FC<EventListProps> = ({ events }) => {
  const [sortBy, setSortBy] = useState<SortOption>('relevance');
  const [selectedEvents, setSelectedEvents] = useState<Set<number>>(new Set());
  const [currentPage, setCurrentPage] = useState(1);
  const [exporting, setExporting] = useState(false);
  const [exportSuccess, setExportSuccess] = useState(false);
  const [exportError, setExportError] = useState<string | null>(null);

  // Show nothing if no events yet
  if (!events || events.length === 0) {
    return null;
  }

  const sortEvents = (eventsToSort: EventData[]): EventData[] => {
    const sorted = [...eventsToSort];
    
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
    const index = events.indexOf(event);
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
    const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
    const endIndex = Math.min(startIndex + EVENTS_PER_PAGE, events.length);
    const pageIndices = new Set<number>();
    
    for (let i = startIndex; i < endIndex; i++) {
      pageIndices.add(i);
    }
    
    setSelectedEvents((prev) => new Set([...prev, ...pageIndices]));
  };

  const handleSelectAllPages = () => {
    const allIndices = new Set(events.map((_event, index) => index));
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
      const filename = `events_export_${timestamp}.xlsx`;

      if (selectedEvents.size === 0) {
        // Export all events
        blob = await apiService.exportExcelCustom(events);
      } else {
        // Export selected events
        const selectedEventsArray = Array.from(selectedEvents)
          .map(index => events[index])
          .filter(Boolean);
        blob = await apiService.exportExcelCustom(selectedEventsArray);
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

  const sortedEvents = sortEvents(events);
  const totalPages = Math.ceil(sortedEvents.length / EVENTS_PER_PAGE);
  const startIndex = (currentPage - 1) * EVENTS_PER_PAGE;
  const endIndex = Math.min(startIndex + EVENTS_PER_PAGE, sortedEvents.length);
  const paginatedEvents = sortedEvents.slice(startIndex, endIndex);

  return (
    <Box sx={{ display: 'flex', justifyContent: 'center', width: '100%' }}>
      <Box sx={{ width: '100%', maxWidth: { xs: '100%', md: '66.666%' } }}>
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        {/* Header */}
        <Box sx={{ mb: 3 }}>
          <Typography variant="h5" gutterBottom>
            Events Found
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Found {events.length} events{totalPages > 1 && ` • Showing ${startIndex + 1}-${endIndex} of ${sortedEvents.length}`}
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
                  disabled={events.length === 0}
                  title="Select all events across all pages"
                >
                  All
                </Button>
                <Button
                  variant="outlined"
                  size="small"
                  startIcon={<DeselectIcon />}
                  onClick={handleDeselectAll}
                  disabled={selectedEvents.size === 0}
                  title="Deselect all"
                >
                  None
                </Button>
              </Box>
            </Grid>
            
            {/* Export Button */}
            <Grid size={{ xs: 12, sm: 12, md: 6 }}>
              <Box sx={{ display: 'flex', justifyContent: { xs: 'stretch', md: 'flex-end' } }}>
                <Button
                  variant="contained"
                  color="primary"
                  startIcon={<DownloadIcon />}
                  onClick={handleExport}
                  disabled={exporting || events.length === 0}
                  fullWidth={false}
                  sx={{ minWidth: 200 }}
                >
                  {exporting ? 'Exporting...' : 
                   selectedEvents.size === 0 ? `Export All (${events.length})` : 
                   `Export Selected (${selectedEvents.size})`}
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>

        {/* Event Cards */}
        <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {paginatedEvents.map((event) => {
            const originalIndex = events.indexOf(event);
            const isSelected = selectedEvents.has(originalIndex);
            
            return (
              <EventCard
                key={originalIndex}
                event={event}
                selected={isSelected}
                onToggleSelect={() => handleToggleEvent(event)}
              />
            );
          })}
        </Box>

        {/* Pagination */}
        {totalPages > 1 && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
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

        {/* Export Success Snackbar */}
        <Snackbar
          open={exportSuccess}
          autoHideDuration={3000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSnackbar} severity="success" sx={{ width: '100%' }}>
            Successfully exported {selectedEvents.size === 0 ? 'all' : selectedEvents.size} event(s) to Excel!
          </Alert>
        </Snackbar>

        {/* Export Error Snackbar */}
        <Snackbar
          open={!!exportError}
          autoHideDuration={5000}
          onClose={handleCloseSnackbar}
          anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
        >
          <Alert onClose={handleCloseSnackbar} severity="error" sx={{ width: '100%' }}>
            {exportError}
          </Alert>
        </Snackbar>
      </Paper>
      </Box>
    </Box>
  );
};

export default EventList;
