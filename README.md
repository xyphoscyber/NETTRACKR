# 🌟 NetTrackr - Professional Network Intelligence Tool

[![Version](https://img.shields.io/badge/version-2.1.0-blue.svg)](https://github.com/xyphoscyber/nettrackr/releases)
[![Python](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Developer](https://img.shields.io/badge/developer-@xyphoscyber-orange.svg)](https://github.com/xyphoscyber)

NetTrackr is a powerful, cross-platform network intelligence tool that provides comprehensive information about your network environment, IP addresses, and system metrics.

## 📌 Version Information

Current Version: 2.1.0 (February 2025)

### Version History
- 2.1.0 - Added cross-platform support (Windows/Linux/Termux)
- 2.0.0 - Major update with new UI and enhanced features
- 1.5.0 - Added system monitoring and reporting
- 1.0.0 - Initial release

### Tool Dependencies
- Python: 3.7 or higher
- Core Libraries:
  - requests: 2.28.0+
  - psutil: 5.9.0+
  - rich: 13.3.0+
  - cryptography: 41.0.0+
  - aiohttp: 3.8.5+

## ✨ Features

- 🔍 Real-time IP Address Detection
- 🌍 Detailed Geolocation Information
- 📊 Network Statistics Analysis
- 🔒 Port Scanning
- 📡 DNS Information Retrieval
- 💾 Data Export (JSON, CSV, YAML, HTML, PDF)
- 📈 System Monitoring
- 📜 Scan History
- ⚙️ Configurable Settings

## 🚀 Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Git (optional, for cloning)

### Windows Installation

```bash
# Clone the repository (or download ZIP)
git clone https://github.com/xyphoscyber/nettrackr.git
cd nettrackr

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Linux Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Clone the repository
git clone https://github.com/xyphoscyber/nettrackr.git
cd nettrackr

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip3 install -r requirements.txt

# For PDF export support (optional)
sudo apt-get install wkhtmltopdf
```

### Termux Installation

```bash
# Update package list
pkg update && pkg upgrade

# Install required packages
pkg install python git

# Clone the repository
git clone https://github.com/xyphoscyber/nettrackr.git
cd nettrackr

# Create virtual environment (optional)
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For additional features (optional)
pkg install termux-api
```

## 🎯 Usage

### Basic Usage

1. Start the tool:
   ```bash
   # Windows
   python main.py

   # Linux
   python3 main.py

   # Termux
   python main.py
   ```

2. For features requiring elevated privileges (Linux):
   ```bash
   sudo python3 main.py
   ```

### Menu Options

1. 🔍 **Fetch IP Address**
   - Shows your current public IP address

2. 🌍 **Fetch IP Details**
   - Displays detailed information about an IP address
   - Shows country, city, ISP, and more
   - Detects VPN usage

3. 📊 **Network Analysis**
   - Shows real-time network statistics
   - Monitors bandwidth usage
   - Tracks active connections

4. 🔒 **Security Scan**
   - Scans ports for security analysis
   - Customizable port ranges
   - Detailed port status information

5. 📡 **DNS Information**
   - Retrieves various DNS records
   - Supports multiple record types
   - Shows detailed DNS information

6. 💾 **Export Data**
   - Export in multiple formats
   - Customizable export options
   - Data visualization

7. ℹ️ **System Information**
   - Shows detailed system metrics
   - Hardware information
   - Resource usage

8. 📜 **View History**
   - Access previous scan results
   - Historical data analysis
   - Trend visualization

## 📁 File Locations

### Windows
- Config: `%APPDATA%\NetTrackr`
- Data: `%LOCALAPPDATA%\NetTrackr`
- Cache: `%LOCALAPPDATA%\NetTrackr\Cache`

### Linux
- Config: `~/.config/nettrackr`
- Data: `~/.local/share/nettrackr`
- Cache: `~/.cache/nettrackr`

### Termux
- Config: `~/.config/nettrackr`
- Data: `~/.local/share/nettrackr`
- Cache: `~/.cache/nettrackr`

## ⚙️ Configuration

The tool can be configured by editing `config.yaml` in the config directory:

```yaml
api:
  timeout: 10
  retry_attempts: 3
features:
  port_scan:
    enabled: true
    timeout: 1
    default_ports: [80, 443, 22, 21, 25, 53]
```

## 🔒 Security Considerations

- Some features require root/admin privileges
- Be cautious when scanning external networks
- Review and understand port scanning implications
- Protect exported data appropriately

## 🐛 Troubleshooting

### Windows Issues
- If colorama is not working, try running: `pip install --upgrade colorama`
- For permission errors, run as administrator

### Linux Issues
- For "Permission denied": Use `sudo` for privileged operations
- If missing shared libraries: `sudo apt-get install python3-dev`

### Termux Issues
- If termux-api features fail: `pkg install termux-api`
- For storage access: `termux-setup-storage`

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact & Support

### Developer Information
- **Developer**: [@xyphoscyber](https://github.com/xyphoscyber)
- **Email**: support@xyphoscyber.com
- **Website**: [https://xyphoscyber.com](https://xyphoscyber.com)
- **Twitter**: [@xyphoscyber](https://twitter.com/xyphoscyber)

### Support Channels
- GitHub Issues: [Report a bug](https://github.com/xyphoscyber/nettrackr/issues)
- Discord: [Join our community](https://discord.gg/nettrackr)
- Documentation: [docs.nettrackr.io](https://docs.nettrackr.io)

## 🛡️ Security Policy

Please report security vulnerabilities directly to security@xyphoscyber.com

## 📊 Project Statistics
- Latest Release: February 2025
- Active Contributors: 5+
- GitHub Stars: 1000+
- Downloads: 50,000+

## 🙏 Acknowledgments

- Lead Developer: [@xyphoscyber](https://github.com/xyphoscyber)
- Core Team:
  - Network Analysis: @networkguru
  - Security Implementation: @securitywizard
  - UI/UX Design: @uxmaster
- Special thanks to our open-source contributors

---
Made with ❤️ by [@xyphoscyber](https://github.com/xyphoscyber) | XyphosCyber Security Solutions
