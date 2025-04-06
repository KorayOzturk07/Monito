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

 /$$      /$$                     /$$   /$$              
| $$$    /$$$                    |__/  | $$              
| $$$$  /$$$$  /$$$$$$  /$$$$$$$  /$$ /$$$$$$    /$$$$$$ 
| $$ $$/$$ $$ /$$__  $$| $$__  $$| $$|_  $$_/   /$$__  $$
| $$  $$$| $$| $$  \ $$| $$  \ $$| $$  | $$    | $$  \ $$
| $$\  $ | $$| $$  | $$| $$  | $$| $$  | $$ /$$| $$  | $$
| $$ \/  | $$|  $$$$$$/| $$  | $$| $$  |  $$$$/|  $$$$$$/
|__/     |__/ \______/ |__/  |__/|__/   \___/   \______/ 
                                                         
"""

    def create_metric_table(self, stats: Dict[str, float], health_score: float) -> Table:
        """Create a table with system metrics."""
        table = Table(
            title="System Metrics",
            style="bold magenta",
            border_style="bright_blue",
            title_style="bold cyan",
            show_header=True,
            header_style="bold yellow",
            padding=(0, 1)
        )
        table.add_column("Metric", justify="left", style="cyan", no_wrap=True)
        table.add_column("Value", justify="right", style="yellow", no_wrap=True)
        table.add_column("Status", justify="center", style="bold", no_wrap=True)
        table.add_column("Threshold", justify="right", style="dim", no_wrap=True)

        # System stats with color coding
        thresholds = self.config['thresholds']
        
        def get_status_emoji(value: float, threshold: float) -> str:
            if value > threshold:
                return "🔴"
            elif value > threshold * 0.8:
                return "🟡"
            return "🟢"
        
        def get_status_text(value: float, threshold: float) -> str:
            if value > threshold:
                return "Critical"
            elif value > threshold * 0.8:
                return "Warning"
            return "Normal"
        
        cpu_color = "red" if stats['cpu'] > thresholds['cpu'] else "green"
        ram_color = "red" if stats['ram'] > thresholds['ram'] else "green"
        disk_color = "red" if stats['disk'] > thresholds['disk'] else "green"
        
        table.add_row(
            "CPU Usage", 
            f"[{cpu_color}]{stats['cpu']:.1f}%[/{cpu_color}]", 
            get_status_emoji(stats['cpu'], thresholds['cpu']),
            f"{thresholds['cpu']}%"
        )
        table.add_row(
            "RAM Usage", 
            f"[{ram_color}]{stats['ram']:.1f}%[/{ram_color}]", 
            get_status_emoji(stats['ram'], thresholds['ram']),
            f"{thresholds['ram']}%"
        )
        table.add_row(
            "Disk Usage", 
            f"[{disk_color}]{stats['disk']:.1f}%[/{disk_color}]", 
            get_status_emoji(stats['disk'], thresholds['disk']),
            f"{thresholds['disk']}%"
        )
        
        if self.config['ui']['show_network']:
            table.add_row(
                "Network Sent", 
                f"[cyan]{stats['network_sent']:.2f} MB/s[/cyan]", 
                "📡",
                "N/A"
            )
            table.add_row(
                "Network Recv", 
                f"[cyan]{stats['network_recv']:.2f} MB/s[/cyan]", 
                "📡",
                "N/A"
            )
        
        # Health score with color and emoji
        health_color = "red" if health_score < 50 else "yellow" if health_score < 75 else "green"
        health_emoji = "🔴" if health_score < 50 else "🟡" if health_score < 75 else "🟢"
        table.add_row(
            "System Health", 
            f"[{health_color}]{health_score:.1f}%[/{health_color}]", 
            health_emoji,
            "N/A"
        )
        
        return table

    def create_process_table(self, processes: List[Tuple[float, int, str]]) -> Table:
        """Create a table with top processes."""
        if not processes:
            return None
            
        table = Table(
            title="Top Processes",
            style="bold blue",
            border_style="bright_blue",
            title_style="bold cyan",
            show_header=True,
            header_style="bold yellow",
            padding=(0, 1)
        )
        table.add_column("#", justify="right", style="dim", no_wrap=True)
        table.add_column("Process", justify="left", style="cyan", no_wrap=True)
        table.add_column("PID", justify="right", style="yellow", no_wrap=True)
        table.add_column("CPU %", justify="right", style="magenta", no_wrap=True)
        table.add_column("Status", justify="center", style="bold", no_wrap=True)
        
        for i, (cpu, pid, name) in enumerate(processes, 1):
            proc_color = "red" if cpu > self.config['thresholds']['process'] else "yellow"
            status_emoji = "🔴" if cpu > self.config['thresholds']['process'] else "🟡" if cpu > self.config['thresholds']['process'] * 0.8 else "🟢"
            table.add_row(
                str(i),
                name,
                str(pid),
                f"[{proc_color}]{cpu:.1f}%[/{proc_color}]",
                status_emoji
            )
        
        return table

    def create_alerts_panel(self, alerts: List[str]) -> Panel:
        """Create a panel for system alerts."""
        if not alerts:
            return Panel(
                Text("No active alerts", style="green"),
                title="Alerts",
                style="green",
                border_style="green",
                title_align="left",
                padding=(1, 2)
            )
        
        alert_text = Text()
        for alert in alerts:
            alert_text.append("⚠️ ", style="bold red")
            alert_text.append(alert, style="red")
            alert_text.append("\n")
        
        return Panel(
            alert_text,
            title="Alerts",
            style="red",
            border_style="red",
            title_align="left",
            subtitle="[dim]Press Ctrl+C to exit[/dim]",
            padding=(1, 2),
            box="double"
        )

    def render_dashboard(self, stats: Dict[str, float], processes: List[Tuple[float, int, str]], 
                        alerts: List[str], health_score: float) -> None:
        """Render the complete dashboard."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=5),
            Layout(name="main", ratio=2),
            Layout(name="footer", size=3)
        )
        
        # Header with system info
        header_layout = Layout()
        header_layout.split_row(
            Layout(name="title", ratio=2),
            Layout(name="status", ratio=1)
        )
        
        # Title section
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title_text = Text()
        title_text.append("System Monitor\n", style="bold cyan")
        title_text.append(f"Last Updated: {timestamp}", style="dim")
        header_layout["title"].update(Panel(title_text, style="bold blue", border_style="bright_blue"))
        
        # Status section
        health_color = "red" if health_score < 50 else "yellow" if health_score < 75 else "green"
        health_emoji = "🔴" if health_score < 50 else "🟡" if health_score < 75 else "🟢"
        status_text = Text()
        status_text.append("System Health\n", style="bold")
        status_text.append(f"{health_emoji} {health_score:.1f}%", style=health_color)
        header_layout["status"].update(Panel(status_text, style="bold blue", border_style="bright_blue"))
        
        layout["header"].update(header_layout)
        
        # Main content
        main_layout = Layout()
        main_layout.split_row(
            Layout(name="metrics", ratio=1),
            Layout(name="processes", ratio=1)
        )
        
        # Metrics section with border
        metrics_panel = Panel(
            self.create_metric_table(stats, health_score),
            title="System Metrics",
            style="bold blue",
            border_style="bright_blue",
            padding=(1, 2)
        )
        main_layout["metrics"].update(metrics_panel)
        
        # Processes section with border
        if self.config['ui']['show_processes']:
            process_table = self.create_process_table(processes)
            if process_table:
                process_panel = Panel(
                    process_table,
                    title="Top Processes",
                    style="bold blue",
                    border_style="bright_blue",
                    padding=(1, 2)
                )
                main_layout["processes"].update(process_panel)
        
        layout["main"].update(main_layout)
        
        # Footer with alerts
        layout["footer"].update(self.create_alerts_panel(alerts))
        
        return layout 