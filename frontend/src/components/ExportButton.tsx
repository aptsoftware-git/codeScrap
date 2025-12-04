import React, { useState } from 'react';
import { Button, CircularProgress } from '@mui/material';
import { FileDownload as DownloadIcon } from '@mui/icons-material';
import { EventData, SearchQuery } from '../types/events';
import apiService from '../services/api';

interface ExportButtonProps {
  sessionId?: string;
  events?: EventData[];
  query?: SearchQuery;
  selectedCount?: number;
  disabled?: boolean;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
}

/**
 * Reusable Export Button Component
 * Can export either from session ID or custom events
 */
const ExportButton: React.FC<ExportButtonProps> = ({
  sessionId,
  events = [],
  query,
  selectedCount = 0,
  disabled = false,
  onExportComplete,
  onExportError,
}) => {
  const [exporting, setExporting] = useState(false);

  const handleExport = async () => {
    try {
      setExporting(true);

      let blob: Blob;
      const timestamp = new Date().toISOString().split('T')[0];
      const queryPhrase = query?.phrase || 'events';
      const filename = `events_${queryPhrase.replace(/\s+/g, '_')}_${timestamp}.xlsx`;

      if (sessionId) {
        // Export from session
        blob = await apiService.exportExcelFromSession(sessionId);
      } else if (events.length > 0) {
        // Export custom events
        blob = await apiService.exportExcelCustom(events);
      } else {
        throw new Error('No data to export');
      }

      apiService.downloadBlob(blob, filename);
      
      if (onExportComplete) {
        onExportComplete();
      }
    } catch (error) {
      console.error('Export error:', error);
      const errorMessage = error instanceof Error ? error.message : 'Failed to export results';
      if (onExportError) {
        onExportError(errorMessage);
      }
    } finally {
      setExporting(false);
    }
  };

  const getButtonText = () => {
    if (exporting) return 'Exporting...';
    if (selectedCount > 0) return `Export ${selectedCount} Selected`;
    return 'Export to Excel';
  };

  return (
    <Button
      fullWidth
      variant="contained"
      color="success"
      startIcon={exporting ? <CircularProgress size={20} color="inherit" /> : <DownloadIcon />}
      onClick={handleExport}
      disabled={disabled || exporting}
    >
      {getButtonText()}
    </Button>
  );
};

export default ExportButton;
