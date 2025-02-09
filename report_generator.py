import json
import csv
import yaml
from datetime import datetime
from pathlib import Path
from prettytable import PrettyTable
import base64
import matplotlib.pyplot as plt
import io

class ReportGenerator:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger.get_logger(__name__)
        self.export_dir = Path(self.config.get("export", {}).get("output_dir", "exports"))
        self._setup_export_directory()

    def _setup_export_directory(self):
        """Set up the export directory"""
        if not self.export_dir.exists():
            self.export_dir.mkdir(parents=True)

    def generate_report(self, data, format="json", report_name=None):
        """Generate a report in the specified format"""
        if not report_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_name = f"nettrackr_report_{timestamp}"

        try:
            if format == "json":
                return self._generate_json(data, report_name)
            elif format == "csv":
                return self._generate_csv(data, report_name)
            elif format == "yaml":
                return self._generate_yaml(data, report_name)
            elif format == "html":
                return self._generate_html(data, report_name)
            elif format == "pdf":
                return self._generate_pdf(data, report_name)
            else:
                raise ValueError(f"Unsupported format: {format}")
        except Exception as e:
            self.logger.error(f"Error generating {format} report: {str(e)}")
            raise

    def _generate_json(self, data, report_name):
        """Generate JSON report"""
        file_path = self.export_dir / f"{report_name}.json"
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return file_path

    def _generate_csv(self, data, report_name):
        """Generate CSV report"""
        file_path = self.export_dir / f"{report_name}.csv"
        
        # Flatten nested dictionary
        flattened_data = self._flatten_dict(data)
        
        with open(file_path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(flattened_data.keys())
            writer.writerow(flattened_data.values())
        return file_path

    def _generate_yaml(self, data, report_name):
        """Generate YAML report"""
        file_path = self.export_dir / f"{report_name}.yaml"
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
        return file_path

    def _generate_html(self, data, report_name):
        """Generate HTML report with charts"""
        file_path = self.export_dir / f"{report_name}.html"
        
        # Generate charts
        charts = self._generate_charts(data)
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>NetTrackr Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .container {{ max-width: 1200px; margin: 0 auto; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; }}
                .section {{ margin: 20px 0; padding: 20px; border: 1px solid #ddd; }}
                .chart {{ margin: 20px 0; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; border: 1px solid #ddd; }}
                th {{ background-color: #f5f5f5; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>NetTrackr Report</h1>
                    <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                </div>
                {self._dict_to_html(data)}
                <div class="section">
                    <h2>Charts</h2>
                    {charts}
                </div>
            </div>
        </body>
        </html>
        """
        
        with open(file_path, 'w') as f:
            f.write(html_content)
        return file_path

    def _generate_pdf(self, data, report_name):
        """Generate PDF report"""
        try:
            import pdfkit
            html_path = self._generate_html(data, f"{report_name}_temp")
            pdf_path = self.export_dir / f"{report_name}.pdf"
            
            pdfkit.from_file(str(html_path), str(pdf_path))
            html_path.unlink()  # Remove temporary HTML file
            return pdf_path
        except ImportError:
            self.logger.error("pdfkit not installed. Please install 'pdfkit' for PDF export support.")
            raise

    def _flatten_dict(self, d, parent_key='', sep='_'):
        """Flatten nested dictionary"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            else:
                items.append((new_key, v))
        return dict(items)

    def _dict_to_html(self, data, level=2):
        """Convert dictionary to HTML representation"""
        html = []
        for key, value in data.items():
            if isinstance(value, dict):
                html.append(f"<div class='section'><h{level}>{key}</h{level}>")
                html.append(self._dict_to_html(value, level + 1))
                html.append("</div>")
            else:
                html.append(f"<p><strong>{key}:</strong> {value}</p>")
        return "\n".join(html)

    def _generate_charts(self, data):
        """Generate charts from data"""
        charts_html = []
        
        try:
            # Example: Generate system metrics chart if available
            if "metrics" in data:
                plt.figure(figsize=(10, 6))
                metrics = data["metrics"]
                if "cpu" in metrics and "percent" in metrics["cpu"]:
                    plt.plot(["CPU Usage"], [metrics["cpu"]["percent"]], 'bo-', label='CPU')
                if "memory" in metrics and "percent" in metrics["memory"]:
                    plt.plot(["Memory Usage"], [metrics["memory"]["percent"]], 'ro-', label='Memory')
                plt.title("System Resource Usage")
                plt.ylabel("Percentage")
                plt.legend()
                
                # Convert plot to base64 string
                buf = io.BytesIO()
                plt.savefig(buf, format='png')
                buf.seek(0)
                img_str = base64.b64encode(buf.read()).decode()
                charts_html.append(f'<img src="data:image/png;base64,{img_str}" />')
                plt.close()
        
        except Exception as e:
            self.logger.error(f"Error generating charts: {str(e)}")
        
        return "\n".join(charts_html)
