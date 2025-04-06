from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from rich.panel import Panel
from rich.layout import Layout
from rich.progress import Progress
from typing import Dict, Any, List, Tuple
from datetime import datetime

class Dashboard:
    def __init__(self, config: Dict[str, Any]):
        self.console = Console()
        self.config = config
        self.ascii_art = """
 .----------------.  .----------------.  .-----------------. .----------------.  .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
| | ____    ____ | || |     ____     | || | ____  _____  | || |     _____    | || |  _________   | || |     ____     | |
| ||_   \  /   _|| || |   .'    `.   | || ||_   \|_   _| | || |    |_   _|   | || | |  _   _  |  | || |   .'    `.   | |
| |  |   \/   |  | || |  /  .--.  \  | || |  |   \ | |   | || |      | |     | || | |_/ | | \_|  | || |  /  .--.  \  | |
| |  | |\  /| |  | || |  | |    | |  | || |  | |\ \| |   | || |      | |     | || |     | |      | || |  | |    | |  | |
| | _| |_\/_| |_ | || |  \  `--'  /  | || | _| |_\   |_  | || |     _| |_    | || |    _| |_     | || |  \  `--'  /  | |
| ||_____||_____|| || |   `.____.'   | || ||_____|\____| | || |    |_____|   | || |   |_____|    | || |   `.____.'   | |
| |              | || |              | || |              | || |              | || |              | || |              | |
| '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
"""

    def create_metric_table(self, stats: Dict[str, float], health_score: float) -> Table:
        """Create a table with system metrics."""
        table = Table(title="System Metrics", style="bold magenta")
        table.add_column("Metric", justify="left", style="cyan")
        table.add_column("Value", justify="right", style="yellow")
        table.add_column("Status", justify="center")

        # System stats with color coding
        thresholds = self.config['thresholds']
        
        cpu_color = "red" if stats['cpu'] > thresholds['cpu'] else "green"
        ram_color = "red" if stats['ram'] > thresholds['ram'] else "green"
        disk_color = "red" if stats['disk'] > thresholds['disk'] else "green"
        
        table.add_row("CPU Usage", f"[{cpu_color}]{stats['cpu']:.1f}%[/{cpu_color}]", 
                     "⚠️" if stats['cpu'] > thresholds['cpu'] else "✅")
        table.add_row("RAM Usage", f"[{ram_color}]{stats['ram']:.1f}%[/{ram_color}]", 
                     "⚠️" if stats['ram'] > thresholds['ram'] else "✅")
        table.add_row("Disk Usage", f"[{disk_color}]{stats['disk']:.1f}%[/{disk_color}]", 
                     "⚠️" if stats['disk'] > thresholds['disk'] else "✅")
        
        if self.config['ui']['show_network']:
            table.add_row("Network Sent", f"{stats['network_sent']:.2f} MB/s", "📡")
            table.add_row("Network Recv", f"{stats['network_recv']:.2f} MB/s", "📡")
        
        # Health score with color
        health_color = "red" if health_score < 50 else "yellow" if health_score < 75 else "green"
        table.add_row("System Health", f"[{health_color}]{health_score:.1f}%[/{health_color}]", 
                     "⚠️" if health_score < 75 else "✅")
        
        return table

    def create_process_table(self, processes: List[Tuple[float, int, str]]) -> Table:
        """Create a table with top processes."""
        if not processes:
            return None
            
        table = Table(title="Top Processes", style="bold blue")
        table.add_column("Process", justify="left", style="cyan")
        table.add_column("PID", justify="right", style="yellow")
        table.add_column("CPU %", justify="right", style="magenta")
        
        for cpu, pid, name in processes:
            proc_color = "red" if cpu > self.config['thresholds']['process'] else "yellow"
            table.add_row(name, str(pid), f"[{proc_color}]{cpu:.1f}%[/{proc_color}]")
        
        return table

    def create_alerts_panel(self, alerts: List[str]) -> Panel:
        """Create a panel for system alerts."""
        if not alerts:
            return Panel("No alerts", title="Alerts", style="green")
        
        alert_text = "\n".join([f"⚠️ {alert}" for alert in alerts])
        return Panel(alert_text, title="Alerts", style="red")

    def render_dashboard(self, stats: Dict[str, float], processes: List[Tuple[float, int, str]], 
                        alerts: List[str], health_score: float) -> None:
        """Render the complete dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header"),
            Layout(name="main"),
            Layout(name="footer")
        )
        
        # Header with ASCII art
        if self.config['ui']['show_ascii_art']:
            layout["header"].update(Panel(Text(self.ascii_art, style="bold magenta")))
        
        # Main content
        main_layout = Layout()
        main_layout.split_row(
            Layout(name="metrics"),
            Layout(name="processes")
        )
        
        main_layout["metrics"].update(self.create_metric_table(stats, health_score))
        if self.config['ui']['show_processes']:
            process_table = self.create_process_table(processes)
            if process_table:
                main_layout["processes"].update(process_table)
        
        layout["main"].update(main_layout)
        
        # Footer with alerts
        layout["footer"].update(self.create_alerts_panel(alerts))
        
        return layout 