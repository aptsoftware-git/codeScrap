import { useState } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import EventList from './components/EventList';
import ProgressBar from './components/ProgressBar';
import LLMConfigDropdown from './components/LLMConfigDropdown';
import { EventData, ProgressUpdate } from './types/events';
import { streamService } from './services/streamService';
import logoImage from './assets/logo.png';
import './App.css';

const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

function App() {
  const [events, setEvents] = useState<EventData[]>([]);
  const [progress, setProgress] = useState<ProgressUpdate | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [searchSummary, setSearchSummary] = useState<{ message: string; total_events: number } | null>(null);

  const handleSearchStart = () => {
    // Reset state
    setEvents([]);
    setProgress(null);
    setSearchSummary(null);
    setIsStreaming(true);
  };

  const handleProgress = (progressUpdate: ProgressUpdate) => {
    setProgress(progressUpdate);
  };

  const handleEventReceived = (event: EventData) => {
    // Add event to list immediately
    setEvents((prev) => [...prev, event]);
  };

  const handleSearchComplete = (summary: { message: string; total_events: number }) => {
    setIsStreaming(false);
    setProgress(null);
    setSearchSummary(summary);
  };

  const handleError = (error: string) => {
    console.error('Search error:', error);
    setIsStreaming(false);
    setProgress(null);
  };

  const handleCancel = async () => {
    if (window.confirm('Are you sure you want to cancel the search? Already extracted events will be kept.')) {
      try {
        await streamService.cancel();
        setIsStreaming(false);
        setProgress(null);
        
        // Reset SearchForm state
        handleSearchComplete({
          message: `Search cancelled. ${events.length} event(s) extracted.`,
          total_events: events.length,
          articles_processed: 0,
          processing_time: 0
        });
      } catch (error) {
        console.error('Cancel error:', error);
        setIsStreaming(false);
        setProgress(null);
        handleSearchComplete({
          message: `Search cancelled. ${events.length} event(s) extracted.`,
          total_events: events.length,
          articles_processed: 0,
          processing_time: 0
        });
      }
    }
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static">
          <Toolbar>
            <Box
              component="img"
              src={logoImage}
              alt="Logo"
              sx={{ height: 52, mr: 2 }}
            />
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Event Scraper & Analyzer
            </Typography>
            <LLMConfigDropdown />
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Box sx={{ mt: 4, mb: 4, flex: 1, width: '100%' }}>
          {/* Search Form - Centered */}
          <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
            <SearchForm 
              onSearchStart={handleSearchStart}
              onProgress={handleProgress}
              onEventReceived={handleEventReceived}
              onSearchComplete={handleSearchComplete}
              onError={handleError}
            />
          </Container>

          {/* Progress Bar */}
          {isStreaming && progress && (
            <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 } }}>
              <ProgressBar progress={progress} onCancel={handleCancel} />
            </Container>
          )}

          {/* Search Summary */}
          {searchSummary && (
            <Container maxWidth="lg" sx={{ px: { xs: 2, sm: 3, md: 4 }, mb: 2 }}>
              <Typography variant="body1" color="success.main">
                ✅ {searchSummary.message}
              </Typography>
            </Container>
          )}
          
          {/* Event List - Full Width - Shows events as they arrive */}
          <EventList events={events} />
        </Box>

        {/* Footer */}
        <Box component="footer" sx={{ py: 2, px: 1.5, mt: 'auto', backgroundColor: (theme) => theme.palette.grey[200] }}>
          <Container maxWidth="xl">
            <Typography variant="caption" color="text.secondary" align="center" display="block">
              Developed by Apt Software Avenues Pvt. Ltd. (a Defender Framework tool)
            </Typography>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;