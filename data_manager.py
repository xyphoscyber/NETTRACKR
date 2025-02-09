import json
import csv
import os
import sqlite3
from datetime import datetime
import yaml

class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self._ensure_data_dir()
        self.db_path = os.path.join(data_dir, "nettrackr.db")
        self._init_database()

    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables
        c.execute('''CREATE TABLE IF NOT EXISTS ip_scans
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     ip TEXT,
                     country TEXT,
                     city TEXT,
                     isp TEXT,
                     timestamp DATETIME)''')
        
        c.execute('''CREATE TABLE IF NOT EXISTS network_stats
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     bytes_sent INTEGER,
                     bytes_recv INTEGER,
                     connections INTEGER,
                     timestamp DATETIME)''')
        
        conn.commit()
        conn.close()

    def save_scan(self, scan_data):
        """Save IP scan data to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO ip_scans (ip, country, city, isp, timestamp)
                    VALUES (?, ?, ?, ?, ?)''',
                    (scan_data.get('ip'),
                     scan_data.get('country'),
                     scan_data.get('city'),
                     scan_data.get('isp'),
                     datetime.now()))
        
        conn.commit()
        conn.close()

    def save_network_stats(self, stats):
        """Save network statistics to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''INSERT INTO network_stats 
                    (bytes_sent, bytes_recv, connections, timestamp)
                    VALUES (?, ?, ?, ?)''',
                    (stats.get('bytes_sent'),
                     stats.get('bytes_recv'),
                     stats.get('connections'),
                     datetime.now()))
        
        conn.commit()
        conn.close()

    def export_data(self, data, format="json", filename=None):
        """Export data in various formats"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"nettrackr_report_{timestamp}"

        filepath = os.path.join(self.data_dir, filename)

        if format == "json":
            with open(f"{filepath}.json", 'w') as f:
                json.dump(data, f, indent=4)
            return f"{filepath}.json"

        elif format == "csv":
            with open(f"{filepath}.csv", 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)
            return f"{filepath}.csv"

        elif format == "yaml":
            with open(f"{filepath}.yaml", 'w') as f:
                yaml.dump(data, f)
            return f"{filepath}.yaml"

    def get_recent_scans(self, limit=10):
        """Get recent IP scans"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM ip_scans 
                    ORDER BY timestamp DESC LIMIT ?''', (limit,))
        
        columns = [description[0] for description in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results

    def get_network_stats_history(self, limit=10):
        """Get network statistics history"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''SELECT * FROM network_stats 
                    ORDER BY timestamp DESC LIMIT ?''', (limit,))
        
        columns = [description[0] for description in c.description]
        results = [dict(zip(columns, row)) for row in c.fetchall()]
        
        conn.close()
        return results

    def clear_old_data(self, days=30):
        """Clear data older than specified days"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''DELETE FROM ip_scans 
                    WHERE timestamp < datetime('now', '-? days')''', (days,))
        
        c.execute('''DELETE FROM network_stats 
                    WHERE timestamp < datetime('now', '-? days')''', (days,))
        
        conn.commit()
        conn.close()
