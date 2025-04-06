import time
import signal
import sys
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from typing import Dict, Any

from .utils import load_config, setup_logging, get_system_info
from .monitor import SystemMonitor
from .ui import Dashboard

def main():
    # Load configuration
    try:
        config = load_config()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)

    # Setup logging
    setup_logging(config)
    
    # Initialize components
    console = Console()
    monitor = SystemMonitor(config)
    dashboard = Dashboard(config)
    
    # Print system info
    system_info = get_system_info()
    console.print(Panel(
        f"OS: {system_info['os']} {system_info['os_version']}\n"
        f"Machine: {system_info['machine']}\n"
        f"Processor: {system_info['processor']}\n"
        f"Python: {system_info['python_version']}",
        title="System Information",
        style="bold blue"
    ))
    
    # Handle graceful shutdown
    def handle_shutdown(signum, frame):
        console.print("\n[bold red]Shutting down Monito...[/bold red]")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Main monitoring loop
    with Live(console=console, auto_refresh=False) as live:
        while True:
            # Get system stats
            stats = monitor.get_system_stats()
            
            # Get top processes
            processes = monitor.get_top_processes()
            
            # Check for alerts
            alerts = monitor.check_thresholds(stats)
            
            # Calculate health score
            health_score = monitor.get_system_health_score()
            
            # Render dashboard
            layout = dashboard.render_dashboard(stats, processes, alerts, health_score)
            live.update(layout)
            live.refresh()
            
            # Sleep for configured interval
            time.sleep(config['monitoring']['update_interval'])

if __name__ == "__main__":
    main() 