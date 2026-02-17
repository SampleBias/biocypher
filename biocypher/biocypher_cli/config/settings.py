"""
Configuration settings for BioCypher CLI
"""

import os
from pathlib import Path
from typing import Dict, Any

# Default configuration values
DEFAULT_CONFIG = {
    # Processing limits
    'max_message_length': int(os.environ.get('BIOCYPHER_MAX_MESSAGE_LENGTH', 1000)),
    'max_dna_sequence_length': int(os.environ.get('BIOCYPHER_MAX_DNA_LENGTH', 10000)),
    
    # Default modes
    'default_encoding_mode': os.environ.get('BIOCYPHER_DEFAULT_MODE', 'basic'),
    'default_output_format': os.environ.get('BIOCYPHER_OUTPUT_FORMAT', 'text'),
    
    # Security settings
    'password_min_length': 8,
    'require_strong_passwords': True,
    'pbkdf2_iterations': 100000,
    
    # Display settings
    'colors_enabled': True,
    'progress_bars': True,
    'line_length': 60,  # For DNA sequence display
    
    # File processing
    'auto_detect_format': True,
    'backup_files': False,
    'default_file_extension': '.dna',
    
    # Performance
    'batch_size': 100,
    'parallel_processing': False,
}

# Configuration file locations (in order of preference)
CONFIG_LOCATIONS = [
    Path.home() / '.biocypher.yaml',
    Path.home() / '.biocypher.yml', 
    Path.home() / '.config' / 'biocypher' / 'config.yaml',
    Path.cwd() / 'biocypher.yaml',
    Path.cwd() / 'biocypher.yml',
]

def get_config_path() -> Path:
    """Get the default configuration file path"""
    return CONFIG_LOCATIONS[0]

def get_cache_dir() -> Path:
    """Get the cache directory path"""
    if os.name == 'nt':  # Windows
        cache_dir = Path.home() / 'AppData' / 'Local' / 'BioCypher'
    else:  # Unix-like
        cache_dir = Path.home() / '.cache' / 'biocypher'
    
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir

def get_data_dir() -> Path:
    """Get the data directory path"""
    if os.name == 'nt':  # Windows
        data_dir = Path.home() / 'AppData' / 'Roaming' / 'BioCypher'
    else:  # Unix-like
        data_dir = Path.home() / '.local' / 'share' / 'biocypher'
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir

class ConfigManager:
    """Manage BioCypher CLI configuration"""
    
    def __init__(self):
        self.config = DEFAULT_CONFIG.copy()
        self._config_path = None
    
    def load(self, config_path: Path = None) -> Dict[str, Any]:
        """Load configuration from file"""
        if config_path:
            self._config_path = config_path
        else:
            # Find existing config file
            for path in CONFIG_LOCATIONS:
                if path.exists():
                    self._config_path = path
                    break
        
        if self._config_path and self._config_path.exists():
            try:
                try:
                    import yaml
                except ImportError:
                    print("Warning: PyYAML not installed. Configuration file support disabled.")
                    return self.config
                    
                with open(self._config_path, 'r') as f:
                    file_config = yaml.safe_load(f) or {}
                
                # Merge with defaults
                self.config.update(file_config)
                
            except Exception as e:
                print(f"Warning: Failed to load config from {self._config_path}: {e}")
        
        return self.config
    
    def save(self, config_path: Path = None) -> None:
        """Save configuration to file"""
        if config_path:
            self._config_path = config_path
        elif not self._config_path:
            self._config_path = get_config_path()
        
        # Create parent directory if needed
        self._config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            try:
                import yaml
            except ImportError:
                print("Error: PyYAML not installed. Cannot save configuration file.")
                return
                
            with open(self._config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=True)
                
        except Exception as e:
            print(f"Error: Failed to save config to {self._config_path}: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def reset(self) -> None:
        """Reset configuration to defaults"""
        self.config = DEFAULT_CONFIG.copy()

# Global configuration instance
config_manager = ConfigManager()