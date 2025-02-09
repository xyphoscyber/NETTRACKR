import requests
import json
from datetime import datetime, timedelta
from pathlib import Path
import pkg_resources
import subprocess
import sys

class UpdateChecker:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger.get_logger(__name__)
        self.version_file = Path("version.json")
        self.current_version = "1.0.0"
        self.last_check_file = Path("data/update_check.json")
        self._load_version()

    def _load_version(self):
        """Load current version information"""
        if self.version_file.exists():
            try:
                with open(self.version_file, 'r') as f:
                    data = json.load(f)
                    self.current_version = data.get('version', self.current_version)
            except Exception as e:
                self.logger.error(f"Error loading version file: {str(e)}")

    def _save_last_check(self):
        """Save the timestamp of the last update check"""
        if not self.last_check_file.parent.exists():
            self.last_check_file.parent.mkdir(parents=True)

        data = {
            'last_check': datetime.now().isoformat(),
            'version': self.current_version
        }
        
        with open(self.last_check_file, 'w') as f:
            json.dump(data, f)

    def _should_check_update(self):
        """Determine if we should check for updates"""
        if not self.config.get("updates", {}).get("auto_check", True):
            return False

        if not self.last_check_file.exists():
            return True

        try:
            with open(self.last_check_file, 'r') as f:
                data = json.load(f)
                last_check = datetime.fromisoformat(data['last_check'])
                check_interval = timedelta(
                    days=self.config.get("updates", {}).get("check_interval_days", 7)
                )
                return datetime.now() - last_check > check_interval
        except Exception:
            return True

    def check_for_updates(self):
        """Check for available updates"""
        if not self._should_check_update():
            return None

        try:
            # This is a placeholder URL - replace with actual update check endpoint
            response = requests.get(
                "https://api.github.com/repos/yourusername/nettrackr/releases/latest",
                timeout=5
            )
            if response.status_code == 200:
                latest_version = response.json().get('tag_name', '').lstrip('v')
                self._save_last_check()
                
                if self._compare_versions(latest_version, self.current_version) > 0:
                    return {
                        'current_version': self.current_version,
                        'latest_version': latest_version,
                        'update_url': response.json().get('html_url'),
                        'release_notes': response.json().get('body')
                    }
        except Exception as e:
            self.logger.error(f"Error checking for updates: {str(e)}")
        
        return None

    def _compare_versions(self, version1, version2):
        """Compare two version strings"""
        v1_parts = [int(x) for x in version1.split('.')]
        v2_parts = [int(x) for x in version2.split('.')]
        
        for i in range(max(len(v1_parts), len(v2_parts))):
            v1 = v1_parts[i] if i < len(v1_parts) else 0
            v2 = v2_parts[i] if i < len(v2_parts) else 0
            if v1 > v2:
                return 1
            elif v1 < v2:
                return -1
        return 0

    def update_dependencies(self):
        """Update project dependencies"""
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "-r", "requirements.txt"])
            return True
        except Exception as e:
            self.logger.error(f"Error updating dependencies: {str(e)}")
            return False
