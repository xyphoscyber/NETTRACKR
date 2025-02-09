import os
import yaml
from pathlib import Path
from utils import get_config_dir, get_data_dir, get_cache_dir

class Config:
    DEFAULT_CONFIG = {
        "api": {
            "timeout": 10,
            "retry_attempts": 3,
            "user_agent": "NetTrackr/1.0.0",
        },
        "database": {
            "path": str(Path(get_data_dir()) / "nettrackr.db"),
            "backup_enabled": True,
            "backup_interval_days": 7,
        },
        "security": {
            "ssl_verify": True,
            "allowed_ports": [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 3306, 3389, 5432, 8080],
            "max_concurrent_scans": 5,
        },
        "logging": {
            "level": "INFO",
            "file": str(Path(get_data_dir()) / "logs" / "nettrackr.log"),
            "max_size_mb": 10,
            "backup_count": 5,
        },
        "export": {
            "default_format": "json",
            "available_formats": ["json", "csv", "yaml", "html", "pdf"],
            "output_dir": str(Path(get_data_dir()) / "exports"),
        },
        "ui": {
            "theme": "dark",
            "colors": {
                "primary": "cyan",
                "secondary": "blue",
                "success": "green",
                "warning": "yellow",
                "error": "red",
                "info": "white",
            },
            "animations_enabled": True,
            "progress_bar_style": "ascii",
        },
        "network": {
            "default_timeout": 5,
            "max_retries": 3,
            "concurrent_requests": 3,
            "proxy_enabled": False,
            "proxy_settings": {
                "http": "",
                "https": "",
            },
        },
        "features": {
            "port_scan": {
                "enabled": True,
                "timeout": 1,
                "default_ports": [80, 443, 22, 21, 25, 53],
                "requires_root": True,  
            },
            "dns_lookup": {
                "enabled": True,
                "record_types": ["A", "AAAA", "MX", "NS", "TXT", "SOA"],
                "timeout": 2,
            },
            "geolocation": {
                "enabled": True,
                "providers": ["ip-api", "ipinfo"],
                "cache_results": True,
                "cache_duration_hours": 24,
            },
            "monitoring": {
                "enabled": True,
                "interval_seconds": 60,
                "metrics": ["cpu", "memory", "disk", "network"],
            },
        },
        "updates": {
            "auto_check": True,
            "check_interval_days": 7,
            "update_channel": "stable",
        },
    }

    def __init__(self):
        self.config_dir = Path(get_config_dir())
        self.config_file = self.config_dir / "config.yaml"
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file or create default"""
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)

        if not self.config_file.exists():
            return self._create_default_config()

        with open(self.config_file, 'r') as f:
            user_config = yaml.safe_load(f)
            return self._merge_configs(self.DEFAULT_CONFIG, user_config)

    def _create_default_config(self):
        """Create default configuration file"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.DEFAULT_CONFIG, f, default_flow_style=False)
        return self.DEFAULT_CONFIG

    def _merge_configs(self, default, user):
        """Recursively merge user config with default config"""
        merged = default.copy()
        
        if not user:
            return merged
            
        for key, value in user.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = self._merge_configs(merged[key], value)
            else:
                merged[key] = value
                
        return merged

    def get(self, section, key=None):
        """Get configuration value"""
        if key:
            return self.config.get(section, {}).get(key)
        return self.config.get(section)

    def set(self, section, key, value):
        """Set configuration value"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section][key] = value
        self._save_config()

    def _save_config(self):
        """Save configuration to file"""
        os.makedirs(self.config_dir, exist_ok=True)
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)

    def reset_to_default(self):
        """Reset configuration to default values"""
        self.config = self.DEFAULT_CONFIG.copy()
        self._save_config()
