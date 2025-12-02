import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  Button,
  MenuItem,
  TextField,
  Grid,
} from '@mui/material';
import {
  FileDownload as DownloadIcon,
  SortByAlpha as SortIcon,
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
  const [exporting, setExporting] = useState(false);

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

  const handleExport = async () => {
    try {
      setExporting(true);
      const blob = await apiService.exportExcelFromSession(searchResults.session_id);
      
      // Generate filename with timestamp
      const timestamp = new Date().toISOString().split('T')[0];
      const filename = `events_${searchResults.query.phrase.replace(/\s+/g, '_')}_${timestamp}.xlsx`;
      
      apiService.downloadBlob(blob, filename);
    } catch (error) {
      console.error('Export error:', error);
      alert('Failed to export results. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const sortedEvents = sortEvents(searchResults.events);

  return (
    <Paper elevation={3} sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h5" gutterBottom>
          Search Results
        </Typography>
        <Typography variant="body2" color="text.secondary" paragraph>
          Found {searchResults.total_matched} matching events from {searchResults.total_extracted} extracted events 
          ({searchResults.total_scraped} total scraped). Processing time: {searchResults.processing_time.toFixed(2)}s
        </Typography>

        {/* Controls */}
        <Grid container spacing={2} sx={{ alignItems: 'center' }}>
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
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
          
          <Grid size={{ xs: 12, sm: 6, md: 4 }}>
            <Button
              fullWidth
              variant="contained"
              color="success"
              startIcon={<DownloadIcon />}
              onClick={handleExport}
              disabled={exporting || sortedEvents.length === 0}
            >
              {exporting ? 'Exporting...' : 'Export to Excel'}
            </Button>
          </Grid>
        </Grid>
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
          {sortedEvents.map((event, index) => (
            <EventCard key={`${event.title}-${index}`} event={event} />
          ))}
        </Box>
      )}
    </Paper>
  );
};

export default EventList;
