# Event Scraper & Analyzer - Frontend

React TypeScript frontend for the Event Scraper & Analyzer application.

## Features

- **Search Form**: User-friendly form to search for events with filters:
  - Search phrase (required)
  - Location (optional)
  - Event type (optional)
  - Date range (optional)

- **Event Display**: Professional cards showing:
  - Event title with clickable links
  - Description
  - Date, location, and organizer
  - Relevance score
  - Source link

- **Sorting**: Sort results by relevance, date, or title

- **Excel Export**: Download search results as formatted Excel files

## Tech Stack

- **Vite**: Build tool and dev server
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Material-UI v7**: Component library
- **Axios**: HTTP client
- **date-fns**: Date formatting

## Getting Started

### Prerequisites

- Node.js 18+ (for Vite 4 compatibility)
- Backend server running on `http://localhost:8000`

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Development

The frontend runs on `http://localhost:5173` by default.

### Project Structure

```
src/
├── components/
│   ├── SearchForm.tsx     # Main search form
│   ├── EventList.tsx      # List of search results
│   └── EventCard.tsx      # Individual event card
├── services/
│   └── api.ts             # API client for backend
├── types/
│   └── events.ts          # TypeScript type definitions
├── App.tsx                # Main app component
└── main.tsx               # Entry point
```

### API Integration

The frontend communicates with the backend REST API:

- `POST /api/v1/search` - Execute search
- `GET /api/v1/search/session/{id}` - Get session results
- `POST /api/v1/export/excel` - Export to Excel

## Usage

1. Enter a search phrase (e.g., "AI", "Machine Learning")
2. Optionally filter by:
   - Location (city, country, or "Online")
   - Event type (conference, workshop, etc.)
   - Date range
3. Click "Search" to execute the search
4. View results with relevance scores
5. Sort results as needed
6. Click "Export to Excel" to download results

## Configuration

To change the backend API URL, edit `src/services/api.ts`:

```typescript
constructor(baseURL: string = 'http://localhost:8000') {
  // Change the default baseURL here
}
```

## Quick Start

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Development Server
```bash
npm run dev
```

### 3. Access Application
Open http://localhost:5173 in your browser

### 4. Ensure Backend is Running
The frontend requires the backend API running on http://127.0.0.1:8000

**For detailed setup instructions, see [SETUP.md](SETUP.md)**

## Documentation

### Setup & Configuration
- **[SETUP.md](SETUP.md)** - Complete installation and setup guide
  - Prerequisites and installation
  - Backend connection configuration
  - Running the application
  - Troubleshooting guide
  - Production build instructions

### Testing Documentation
- **[test/QUICKSTART_TEST.md](test/QUICKSTART_TEST.md)** - 5-minute quick test guide
- **[test/TESTING_GUIDE.md](test/TESTING_GUIDE.md)** - Comprehensive testing procedures
- **[test/TEST_RESULTS.md](test/TEST_RESULTS.md)** - Pre-test verification and results template

### Implementation Documentation
- **[doc/INCREMENT9_COMPLETE.md](doc/INCREMENT9_COMPLETE.md)** - Implementation summary
- **[doc/REVIEW_INCREMENT9.md](doc/REVIEW_INCREMENT9.md)** - Detailed code review

## Troubleshooting

For detailed troubleshooting, see [SETUP.md](SETUP.md#troubleshooting)

### Common Issues

**CORS Errors**: Backend must enable CORS for `http://localhost:5173`

**Connection Issues**: Ensure backend is running on http://127.0.0.1:8000
```bash
cd ../backend
uvicorn app.main:app --reload
```

**Build Issues**: Clear and reinstall dependencies
```bash
rm -rf node_modules package-lock.json
npm install
```

## Increment 9 Completion

This frontend implements **Increment 9: React Frontend - Search Form** with:

- ✅ Professional search form with validation
- ✅ Material-UI components for modern UI
- ✅ TypeScript for type safety
- ✅ API integration with backend
- ✅ Event display with cards
- ✅ Sorting and filtering
- ✅ Excel export functionality
- ✅ Responsive design
- ✅ Loading states and error handling

## Next Steps

- Increment 10: Event Details Modal (view full event information)
- Increment 11: Advanced Filters (multi-select, date ranges)
- Increment 12: User Preferences & History
