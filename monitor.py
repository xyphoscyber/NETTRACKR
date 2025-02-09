import psutil
import time
import threading
from datetime import datetime, timedelta
import json
from pathlib import Path
import platform
import os
from utils import get_data_dir, format_size

class SystemMonitor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger.get_logger(__name__)
        self.monitoring_enabled = config.get("features", {}).get("monitoring", {}).get("enabled", True)
        self.interval = config.get("features", {}).get("monitoring", {}).get("interval_seconds", 60)
        self.metrics = config.get("features", {}).get("monitoring", {}).get("metrics", [])
        self.data_dir = Path(get_data_dir()) / "monitoring"
        self.running = False
        self._setup_data_directory()

    def _setup_data_directory(self):
        """Set up the monitoring data directory"""
        if not self.data_dir.exists():
            self.data_dir.mkdir(parents=True)

    def start(self):
        """Start the monitoring thread"""
        if self.monitoring_enabled and not self.running:
            self.running = True
            self.monitor_thread = threading.Thread(target=self._monitor_loop)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
            self.logger.info("System monitoring started")

    def stop(self):
        """Stop the monitoring thread"""
        self.running = False
        self.logger.info("System monitoring stopped")

    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self._save_metrics(metrics)
                time.sleep(self.interval)
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {str(e)}")
                time.sleep(5)  # Wait before retrying

    def _collect_metrics(self):
        """Collect system metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "system": platform.system(),
            "metrics": {}
        }

        try:
            if "cpu" in self.metrics:
                cpu_metrics = {
                    "percent": psutil.cpu_percent(interval=1),
                    "count": {
                        "physical": psutil.cpu_count(logical=False),
                        "logical": psutil.cpu_count(logical=True)
                    }
                }
                
                # CPU frequency might not be available on all systems
                try:
                    cpu_freq = psutil.cpu_freq()
                    if cpu_freq:
                        cpu_metrics["frequency"] = {
                            "current": cpu_freq.current,
                            "min": cpu_freq.min,
                            "max": cpu_freq.max
                        }
                except Exception as e:
                    self.logger.debug(f"CPU frequency not available: {str(e)}")
                
                metrics["metrics"]["cpu"] = cpu_metrics

            if "memory" in self.metrics:
                memory = psutil.virtual_memory()
                metrics["metrics"]["memory"] = {
                    "total": format_size(memory.total),
                    "available": format_size(memory.available),
                    "used": format_size(memory.used),
                    "free": format_size(memory.free),
                    "percent": memory.percent
                }

                # Add swap memory if available
                try:
                    swap = psutil.swap_memory()
                    metrics["metrics"]["swap"] = {
                        "total": format_size(swap.total),
                        "used": format_size(swap.used),
                        "free": format_size(swap.free),
                        "percent": swap.percent
                    }
                except Exception as e:
                    self.logger.debug(f"Swap memory info not available: {str(e)}")

            if "disk" in self.metrics:
                disk_metrics = {}
                for partition in psutil.disk_partitions(all=False):
                    try:
                        usage = psutil.disk_usage(partition.mountpoint)
                        disk_metrics[partition.mountpoint] = {
                            "device": partition.device,
                            "fstype": partition.fstype,
                            "total": format_size(usage.total),
                            "used": format_size(usage.used),
                            "free": format_size(usage.free),
                            "percent": usage.percent
                        }
                    except Exception as e:
                        self.logger.debug(f"Could not get disk usage for {partition.mountpoint}: {str(e)}")
                metrics["metrics"]["disk"] = disk_metrics

            if "network" in self.metrics:
                # Get network interfaces
                net_if_addrs = psutil.net_if_addrs()
                net_if_stats = psutil.net_if_stats()
                net_io = psutil.net_io_counters(pernic=True)
                
                network_metrics = {}
                for interface, addrs in net_if_addrs.items():
                    interface_metrics = {
                        "addresses": [],
                        "stats": {},
                        "io": {}
                    }
                    
                    # Add addresses
                    for addr in addrs:
                        addr_info = {
                            "family": str(addr.family),
                            "address": addr.address
                        }
                        if addr.netmask:
                            addr_info["netmask"] = addr.netmask
                        if hasattr(addr, "broadcast") and addr.broadcast:
                            addr_info["broadcast"] = addr.broadcast
                        interface_metrics["addresses"].append(addr_info)
                    
                    # Add interface stats
                    if interface in net_if_stats:
                        stats = net_if_stats[interface]
                        interface_metrics["stats"] = {
                            "speed": stats.speed,
                            "mtu": stats.mtu,
                            "up": stats.isup,
                            "duplex": str(stats.duplex)
                        }
                    
                    # Add IO counters
                    if interface in net_io:
                        io = net_io[interface]
                        interface_metrics["io"] = {
                            "bytes_sent": format_size(io.bytes_sent),
                            "bytes_recv": format_size(io.bytes_recv),
                            "packets_sent": io.packets_sent,
                            "packets_recv": io.packets_recv,
                            "errin": io.errin,
                            "errout": io.errout,
                            "dropin": io.dropin,
                            "dropout": io.dropout
                        }
                    
                    network_metrics[interface] = interface_metrics
                
                metrics["metrics"]["network"] = network_metrics

        except Exception as e:
            self.logger.error(f"Error collecting metrics: {str(e)}")

        return metrics

    def _save_metrics(self, metrics):
        """Save metrics to a file"""
        date_str = datetime.now().strftime("%Y%m%d")
        metrics_file = self.data_dir / f"metrics_{date_str}.json"
        
        try:
            if metrics_file.exists():
                with open(metrics_file, 'r') as f:
                    data = json.load(f)
            else:
                data = []
            
            data.append(metrics)
            
            with open(metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving metrics: {str(e)}")

    def get_latest_metrics(self):
        """Get the latest collected metrics"""
        return self._collect_metrics()

    def get_metrics_history(self, days=1):
        """Get metrics history for the specified number of days"""
        history = []
        for i in range(days):
            date_str = (datetime.now() - timedelta(days=i)).strftime("%Y%m%d")
            metrics_file = self.data_dir / f"metrics_{date_str}.json"
            if metrics_file.exists():
                try:
                    with open(metrics_file, 'r') as f:
                        history.extend(json.load(f))
                except Exception as e:
                    self.logger.error(f"Error reading metrics history: {str(e)}")
        return history
