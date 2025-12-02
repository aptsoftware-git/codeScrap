"""
Configuration manager for loading and managing source configurations.
"""

import yaml
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger

from app.models import SourceConfig


class ConfigManager:
    """Manages source configurations from YAML files."""
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the sources.yaml file. If None, uses default location.
        """
        if config_path is None:
            # Default to config/sources.yaml relative to project root
            # Path structure: backend/app/services/config_manager.py -> need to go up 3 levels
            root_dir = Path(__file__).parent.parent.parent.parent
            config_path = root_dir / "config" / "sources.yaml"
        
        self.config_path = Path(config_path)
        self._sources: List[SourceConfig] = []
        self._sources_by_name: Dict[str, SourceConfig] = {}
        
        logger.info(f"ConfigManager initialized with config path: {self.config_path}")
    
    def load_sources(self) -> List[SourceConfig]:
        """
        Load source configurations from YAML file.
        
        Returns:
            List of SourceConfig objects.
        
        Raises:
            FileNotFoundError: If config file doesn't exist.
            ValueError: If config file is invalid.
        """
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            if not config_data or 'sources' not in config_data:
                logger.warning("No sources found in config file")
                return []
            
            sources = []
            for source_data in config_data['sources']:
                try:
                    source = SourceConfig(**source_data)
                    sources.append(source)
                    logger.debug(f"Loaded source: {source.name} (enabled: {source.enabled})")
                except Exception as e:
                    logger.error(f"Error loading source config: {e}")
                    logger.debug(f"Source data: {source_data}")
                    continue
            
            self._sources = sources
            self._sources_by_name = {s.name: s for s in sources}
            
            logger.info(f"Loaded {len(sources)} sources from config")
            return sources
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML config: {e}")
            raise ValueError(f"Invalid YAML configuration: {e}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            raise
    
    def get_sources(self, enabled_only: bool = True) -> List[SourceConfig]:
        """
        Get all configured sources.
        
        Args:
            enabled_only: If True, return only enabled sources.
        
        Returns:
            List of SourceConfig objects.
        """
        if not self._sources:
            logger.warning("No sources loaded, attempting to load from config")
            self.load_sources()
        
        if enabled_only:
            return [s for s in self._sources if s.enabled]
        return self._sources.copy()
    
    def get_source_by_name(self, name: str) -> Optional[SourceConfig]:
        """
        Get a specific source by name.
        
        Args:
            name: Source name.
        
        Returns:
            SourceConfig object or None if not found.
        """
        if not self._sources_by_name:
            self.load_sources()
        
        return self._sources_by_name.get(name)
    
    def get_enabled_count(self) -> int:
        """Get count of enabled sources."""
        return len([s for s in self._sources if s.enabled])
    
    def get_total_count(self) -> int:
        """Get total count of configured sources."""
        return len(self._sources)
    
    def validate_sources(self) -> Dict[str, List[str]]:
        """
        Validate all source configurations.
        
        Returns:
            Dict with 'valid' and 'invalid' lists of source names.
        """
        valid = []
        invalid = []
        
        for source in self._sources:
            try:
                # Check required fields
                if not source.name or not source.base_url:
                    invalid.append(source.name or "unnamed")
                    continue
                
                # Check URL format
                if not source.base_url.startswith(('http://', 'https://')):
                    invalid.append(source.name)
                    continue
                
                valid.append(source.name)
                
            except Exception as e:
                logger.error(f"Validation error for source {source.name}: {e}")
                invalid.append(source.name)
        
        return {"valid": valid, "invalid": invalid}
    
    def reload_sources(self) -> List[SourceConfig]:
        """
        Reload sources from config file.
        
        Returns:
            List of reloaded SourceConfig objects.
        """
        logger.info("Reloading sources from config")
        self._sources.clear()
        self._sources_by_name.clear()
        return self.load_sources()


# Global instance
config_manager = ConfigManager()
