import { Box, LinearProgress, Typography, Button, Paper } from '@mui/material';
import { ProgressUpdate } from '../types/events';

interface ProgressBarProps {
  progress: ProgressUpdate;
  onCancel: () => void;
}

/**
 * Progress bar component showing real-time search progress
 */
export default function ProgressBar({ progress, onCancel }: ProgressBarProps) {
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        p: 3, 
        mb: 3, 
        borderLeft: 4, 
        borderColor: 'primary.main',
        backgroundColor: 'background.paper'
      }}
    >
      <Box sx={{ width: '100%' }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="h6" color="primary">
            🔄 Processing Search...
          </Typography>
          <Button 
            variant="outlined" 
            color="error" 
            size="small"
            onClick={onCancel}
            sx={{ minWidth: 120 }}
          >
            Cancel
          </Button>
        </Box>

        {/* Status Message */}
        <Typography variant="body1" color="text.secondary" gutterBottom>
          {progress.status}
        </Typography>

        {/* Progress Bar */}
        <Box sx={{ display: 'flex', alignItems: 'center', mt: 2 }}>
          <Box sx={{ width: '100%', mr: 2 }}>
            <LinearProgress 
              variant="determinate" 
              value={progress.percentage} 
              sx={{ 
                height: 10, 
                borderRadius: 5,
                backgroundColor: 'grey.200',
                '& .MuiLinearProgress-bar': {
                  borderRadius: 5,
                  background: 'linear-gradient(90deg, #1976d2 0%, #42a5f5 100%)',
                }
              }}
            />
          </Box>
          <Box sx={{ minWidth: 80, textAlign: 'right' }}>
            <Typography variant="body2" color="text.secondary" fontWeight="bold">
              {progress.percentage.toFixed(0)}%
            </Typography>
          </Box>
        </Box>

        {/* Footer Info */}
        <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
          💡 Events will appear below as soon as they are extracted
        </Typography>
      </Box>
    </Paper>
  );
}
