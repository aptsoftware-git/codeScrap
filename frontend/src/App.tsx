import { useState } from 'react';
import { Container, CssBaseline, ThemeProvider, createTheme, AppBar, Toolbar, Typography, Box } from '@mui/material';
import SearchForm from './components/SearchForm';
import EventList from './components/EventList';
import { SearchResponse } from './types/events';
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
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);

  const handleSearchComplete = (results: SearchResponse) => {
    setSearchResults(results);
  };

  const handleSearchStart = () => {
    setSearchResults(null);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        {/* App Bar */}
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Event Scraper & Analyzer
            </Typography>
          </Toolbar>
        </AppBar>

        {/* Main Content */}
        <Container maxWidth="lg" sx={{ mt: 4, mb: 4, flex: 1 }}>
          <SearchForm 
            onSearchComplete={handleSearchComplete}
            onSearchStart={handleSearchStart}
          />
          <EventList searchResults={searchResults} />
        </Container>

        {/* Footer */}
        <Box component="footer" sx={{ py: 3, px: 2, mt: 'auto', backgroundColor: (theme) => theme.palette.grey[200] }}>
          <Container maxWidth="lg">
            <Typography variant="body2" color="text.secondary" align="center">
              Event Scraper & Analyzer - Powered by Ollama & spaCy
            </Typography>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;