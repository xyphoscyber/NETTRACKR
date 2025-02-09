#!/usr/bin/env python3
"""
NetTrackr - Professional Network Intelligence Tool
Version: 2.1.0
Developer: @xyphoscyber
Website: https://xyphoscyber.com
License: MIT
Copyright (c) 2025 XyphosCyber Security Solutions
"""

__version__ = "2.1.0"
__author__ = "@xyphoscyber"
__email__ = "support@xyphoscyber.com"
__license__ = "MIT"
__copyright__ = "Copyright (c) 2025 XyphosCyber Security Solutions"

import sys
import os
from pathlib import Path
import asyncio
import signal
from datetime import datetime

# Internal imports
from config import Config
from logger import Logger, LoggerDecorator
from monitor import SystemMonitor
from updater import UpdateChecker
from data_manager import DataManager
from report_generator import ReportGenerator
from utils import (
    setup_terminal,
    create_spinner,
    create_progress_bar,
    format_table,
    format_size,
    format_time
)

# External imports
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
import requests
import dns.resolver
import psutil
from termcolor import colored
import yaml

class NetTrackr:
    def __init__(self):
        self.config = Config()
        self.logger = Logger(self.config.config)
        self.log = self.logger.get_logger(__name__)
        self.monitor = SystemMonitor(self.config.config, self.logger)
        self.updater = UpdateChecker(self.config.config, self.logger)
        self.data_manager = DataManager(self.config.config, self.logger)
        self.report_generator = ReportGenerator(self.config.config, self.logger)
        self.console = Console()
        self.running = True
        self.setup_signal_handlers()

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

    def handle_shutdown(self, signum, frame):
        """Handle shutdown signals"""
        self.log.info("Shutdown signal received")
        self.cleanup()
        sys.exit(0)

    @LoggerDecorator(logging.getLogger(__name__))
    def cleanup(self):
        """Cleanup resources before shutdown"""
        self.running = False
        self.monitor.stop()
        self.log.info("Cleanup completed")

    def display_welcome_message(self):
        """Display welcome message with ASCII art"""
        welcome_text = """
███╗   ██╗███████╗████████╗████████╗██████╗  █████╗  ██████╗██╗  ██╗██████╗ 
████╗  ██║██╔════╝╚══██╔══╝╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔══██╗
██╔██╗ ██║█████╗     ██║      ██║   ██████╔╝███████║██║     █████╔╝ ██████╔╝
██║╚██╗██║██╔══╝     ██║      ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══██╗
██║ ╚████║███████╗   ██║      ██║   ██║  ██║██║  ██║╚██████╗██║  ██╗██║  ██║
╚═╝  ╚═══╝╚══════╝   ╚═╝      ╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝
        """
        self.console.print(Panel(Text(welcome_text, style="bold blue")))
        self.console.print(Panel(Text("Professional Network Intelligence Tool", style="cyan")))

    async def check_for_updates(self):
        """Check for available updates"""
        update_info = self.updater.check_for_updates()
        if update_info:
            self.console.print(Panel(
                Text(f"Update available: {update_info['latest_version']}\n"
                     f"Current version: {update_info['current_version']}\n"
                     f"Visit: {update_info['update_url']}", style="yellow")
            ))

    @LoggerDecorator(logging.getLogger(__name__))
    async def fetch_ip_address(self):
        """Fetch current IP address"""
        try:
            async with create_spinner("Fetching IP address..."):
                response = requests.get('https://api.ipify.org?format=json')
                ip_data = response.json()
                return ip_data['ip']
        except Exception as e:
            self.log.error(f"Error fetching IP address: {str(e)}")
            raise

    @LoggerDecorator(logging.getLogger(__name__))
    async def fetch_ip_details(self, ip_address):
        """Fetch detailed information about an IP address"""
        try:
            async with create_spinner("Fetching IP details..."):
                response = requests.get(f'http://ip-api.com/json/{ip_address}')
                details = response.json()
                
                # Save to database
                self.data_manager.save_ip_scan(ip_address, details)
                
                return details
        except Exception as e:
            self.log.error(f"Error fetching IP details: {str(e)}")
            raise

    @LoggerDecorator(logging.getLogger(__name__))
    async def scan_ports(self, target, ports=None):
        """Scan ports on target"""
        if ports is None:
            ports = self.config.get("features", {}).get("port_scan", {}).get("default_ports", [80, 443])
        
        results = []
        with create_progress_bar() as progress:
            task = progress.add_task("[cyan]Scanning ports...", total=len(ports))
            
            for port in ports:
                try:
                    reader, writer = await asyncio.wait_for(
                        asyncio.open_connection(target, port),
                        timeout=self.config.get("features", {}).get("port_scan", {}).get("timeout", 1)
                    )
                    writer.close()
                    await writer.wait_closed()
                    results.append({"port": port, "state": "open"})
                except:
                    results.append({"port": port, "state": "closed"})
                progress.update(task, advance=1)
        
        return results

    @LoggerDecorator(logging.getLogger(__name__))
    async def fetch_dns_info(self, domain):
        """Fetch DNS information for a domain"""
        results = {}
        record_types = self.config.get("features", {}).get("dns_lookup", {}).get("record_types", ["A"])
        
        async with create_spinner("Fetching DNS information..."):
            for record_type in record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    results[record_type] = [str(rdata) for rdata in answers]
                except Exception as e:
                    results[record_type] = [f"Error: {str(e)}"]
        
        return results

    @LoggerDecorator(logging.getLogger(__name__))
    def generate_report(self, data, format="json"):
        """Generate a report in the specified format"""
        try:
            return self.report_generator.generate_report(data, format)
        except Exception as e:
            self.log.error(f"Error generating report: {str(e)}")
            raise

    async def main_menu(self):
        """Display and handle main menu"""
        while self.running:
            self.console.clear()
            self.display_welcome_message()
            
            options = [
                "1. 🔍 Fetch IP Address",
                "2. 🌍 Fetch IP Details",
                "3. 📊 Network Analysis",
                "4. 🔒 Security Scan",
                "5. 📡 DNS Information",
                "6. 💾 Export Data",
                "7. ℹ️ System Information",
                "8. 📜 View History",
                "9. ⚙️ Configuration",
                "10. ❌ Exit"
            ]
            
            for option in options:
                self.console.print(Text(option, style="cyan"))
            
            choice = input("\nEnter your choice (1-10): ")
            
            try:
                if choice == "1":
                    ip = await self.fetch_ip_address()
                    self.console.print(Panel(Text(f"Your IP Address: {ip}", style="green")))
                
                elif choice == "2":
                    ip = await self.fetch_ip_address()
                    details = await self.fetch_ip_details(ip)
                    self.console.print(Panel(Text(yaml.dump(details), style="green")))
                
                elif choice == "3":
                    metrics = self.monitor.get_latest_metrics()
                    self.console.print(Panel(Text(yaml.dump(metrics), style="green")))
                
                elif choice == "4":
                    ip = await self.fetch_ip_address()
                    ports_input = input("Enter ports to scan (comma-separated) or press Enter for default: ")
                    ports = [int(p.strip()) for p in ports_input.split(",")] if ports_input else None
                    results = await self.scan_ports(ip, ports)
                    self.console.print(Panel(Text(yaml.dump(results), style="green")))
                
                elif choice == "5":
                    domain = input("Enter domain name: ")
                    dns_info = await self.fetch_dns_info(domain)
                    self.console.print(Panel(Text(yaml.dump(dns_info), style="green")))
                
                elif choice == "6":
                    formats = self.config.get("export", {}).get("available_formats", ["json"])
                    print("\nAvailable formats:")
                    for i, fmt in enumerate(formats, 1):
                        print(f"{i}. {fmt}")
                    fmt_choice = int(input("\nChoose format: ")) - 1
                    if 0 <= fmt_choice < len(formats):
                        data = self.data_manager.get_all_data()
                        report_path = self.generate_report(data, formats[fmt_choice])
                        self.console.print(Panel(Text(f"Report generated: {report_path}", style="green")))
                
                elif choice == "7":
                    system_info = {
                        "os": sys.platform,
                        "python_version": sys.version,
                        "cpu_count": psutil.cpu_count(),
                        "memory": format_size(psutil.virtual_memory().total),
                        "disk": format_size(psutil.disk_usage('/').total)
                    }
                    self.console.print(Panel(Text(yaml.dump(system_info), style="green")))
                
                elif choice == "8":
                    history = self.data_manager.get_scan_history()
                    self.console.print(Panel(Text(yaml.dump(history), style="green")))
                
                elif choice == "9":
                    self.console.print(Panel(Text(yaml.dump(self.config.config), style="green")))
                
                elif choice == "10":
                    self.cleanup()
                    break
                
                input("\nPress Enter to continue...")
            
            except Exception as e:
                self.log.error(f"Error in menu option {choice}: {str(e)}")
                self.console.print(Panel(Text(f"Error: {str(e)}", style="red")))
                input("\nPress Enter to continue...")

async def main():
    """Main entry point"""
    app = NetTrackr()
    await app.check_for_updates()
    app.monitor.start()
    await app.main_menu()

if __name__ == "__main__":
    setup_terminal()
    asyncio.run(main())
