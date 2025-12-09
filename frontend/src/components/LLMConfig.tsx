import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Collapse,
  Divider,
  Chip,
  Alert,
  SelectChangeEvent,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';

interface LLMModel {
  id: string;
  name: string;
  description?: string;
  pricing?: {
    input: number;
    output: number;
    cache_discount?: number;
  };
}

interface LLMUsage {
  total_requests: number;
  total_input_tokens: number;
  total_output_tokens: number;
  total_cached_tokens: number;
  total_cost: number;
  cache_savings: number;
}

interface LLMConfig {
  provider: 'ollama' | 'claude';
  model: string;
}

const STORAGE_KEY = 'llm_config';

const LLMConfigPanel: React.FC = () => {
  const [config, setConfig] = useState<LLMConfig>(() => {
    // Load from localStorage
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error('Failed to parse saved LLM config:', e);
      }
    }
    return { provider: 'claude', model: 'claude-4.5-haiku' };
  });

  const [expanded, setExpanded] = useState(false);
  const [models, setModels] = useState<{ ollama: LLMModel[]; claude: LLMModel[] }>({
    ollama: [],
    claude: [],
  });
  const [usage, setUsage] = useState<LLMUsage | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Fetch available models
  const fetchModels = async () => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/v1/llm/models`);
      const data = await response.json();

      if (data.models) {
        setModels({
          ollama: data.models.ollama?.models || [],
          claude: data.models.claude?.models || [],
        });
      }
    } catch (err) {
      console.error('Failed to fetch models:', err);
      setError('Failed to load models');
    }
  };

  // Fetch usage stats
  const fetchUsage = async () => {
    try {
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      const response = await fetch(`${baseUrl}/api/v1/llm/usage`);
      const data = await response.json();

      if (data.usage) {
        setUsage(data.usage);
      }
    } catch (err) {
      console.error('Failed to fetch usage:', err);
    }
  };

  // Reset usage stats
  const resetStats = async () => {
    try {
      setLoading(true);
      const baseUrl = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
      await fetch(`${baseUrl}/api/v1/llm/reset-stats`, { method: 'POST' });
      await fetchUsage(); // Refresh
      setLoading(false);
    } catch (err) {
      console.error('Failed to reset stats:', err);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchModels();
    fetchUsage();
    // Refresh usage every 30 seconds if expanded
    const interval = expanded
      ? setInterval(fetchUsage, 30000)
      : undefined;
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [expanded]);

  // Save to localStorage when config changes
  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  }, [config]);

  const handleProviderChange = (event: SelectChangeEvent<'ollama' | 'claude'>) => {
    const newProvider = event.target.value as 'ollama' | 'claude';
    setConfig((prev) => ({
      provider: newProvider,
      model: newProvider === 'claude' ? 'claude-4.5-haiku' : models.ollama[0]?.id || '',
    }));
  };

  const handleModelChange = (event: SelectChangeEvent<string>) => {
    setConfig((prev) => ({
      ...prev,
      model: event.target.value,
    }));
  };

  return (
    <Paper elevation={2} sx={{ mb: 2, overflow: 'hidden' }}>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          cursor: 'pointer',
          '&:hover': { bgcolor: 'action.hover' },
        }}
        onClick={() => setExpanded(!expanded)}
      >
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <SettingsIcon />
          <Typography variant="subtitle1" fontWeight="medium">
            LLM Configuration
          </Typography>
          <Chip
            label={config.provider === 'claude' ? 'Cloud (Claude)' : 'Local (Ollama)'}
            size="small"
            color={config.provider === 'claude' ? 'primary' : 'default'}
          />
        </Box>
        {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
      </Box>

      <Collapse in={expanded}>
        <Divider />
        <Box sx={{ p: 2 }}>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            {/* Provider Selection */}
            <FormControl fullWidth>
              <InputLabel>Provider</InputLabel>
              <Select
                value={config.provider}
                label="Provider"
                onChange={handleProviderChange}
              >
                <MenuItem value="ollama">Local (Ollama)</MenuItem>
                <MenuItem value="claude">Cloud (Claude API)</MenuItem>
              </Select>
            </FormControl>

            {/* Model Selection */}
            <FormControl fullWidth>
              <InputLabel>Model</InputLabel>
              <Select
                value={config.model}
                label="Model"
                onChange={handleModelChange}
              >
                {config.provider === 'claude'
                  ? models.claude.map((model) => (
                      <MenuItem key={model.id} value={model.id}>
                        {model.name}
                      </MenuItem>
                    ))
                  : models.ollama.map((model) => (
                      <MenuItem key={model.id} value={model.id}>
                        {model.name}
                      </MenuItem>
                    ))}
              </Select>
            </FormControl>
          </Box>

          {/* Usage Stats for Claude */}
          {config.provider === 'claude' && usage && (
            <>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Box
                  sx={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    mb: 1,
                  }}
                >
                  <Typography variant="subtitle2" color="text.secondary">
                    Usage Statistics
                  </Typography>
                  <IconButton size="small" onClick={resetStats} disabled={loading}>
                    <RefreshIcon fontSize="small" />
                  </IconButton>
                </Box>

                <Box sx={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 1 }}>
                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Requests
                    </Typography>
                    <Typography variant="body2">{usage.total_requests}</Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Total Cost
                    </Typography>
                    <Typography variant="body2" fontWeight="medium" color="primary">
                      ${usage.total_cost.toFixed(4)}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Input Tokens
                    </Typography>
                    <Typography variant="body2">
                      {usage.total_input_tokens.toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Output Tokens
                    </Typography>
                    <Typography variant="body2">
                      {usage.total_output_tokens.toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Cached Tokens
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      {usage.total_cached_tokens.toLocaleString()}
                    </Typography>
                  </Box>

                  <Box>
                    <Typography variant="caption" color="text.secondary">
                      Cache Savings
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      ${usage.cache_savings.toFixed(4)}
                    </Typography>
                  </Box>
                </Box>
              </Box>
            </>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

// Export config getter for use in other components
export const getLLMConfig = (): LLMConfig => {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (saved) {
    try {
      return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to parse saved LLM config:', e);
    }
  }
  return { provider: 'claude', model: 'claude-4.5-haiku' };
};

export default LLMConfigPanel;
