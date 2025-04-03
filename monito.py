import os
import psutil
import logging
import time
from datetime import datetime
from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.text import Text
from collections import deque

# Initialize Rich Console
console = Console()

# ASCII Art for Monito
ASCII_ART = """

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

console.print(Text(ASCII_ART, style="bold magenta"))

# Logging setup
LOG_FILE = "monito.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Thresholds
CPU_THRESHOLD = 85.0  # Percentage
RAM_THRESHOLD = 85.0  # Percentage
DISK_THRESHOLD = 90.0  # Percentage
PROCESS_THRESHOLD = 50.0  # Percentage

def get_system_stats():
    """Collects CPU, RAM, and Disk usage."""
    cpu_usage = psutil.cpu_percent(interval=1)
    ram_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    return cpu_usage, ram_usage, disk_usage

def log_anomalies(cpu, ram, disk):
    """Logs and alerts on system anomalies."""
    if cpu > CPU_THRESHOLD:
        logging.warning(f"High CPU Usage Detected: {cpu}%")
    if ram > RAM_THRESHOLD:
        logging.warning(f"High RAM Usage Detected: {ram}%")
    if disk > DISK_THRESHOLD:
        logging.warning(f"High Disk Usage Detected: {disk}%")

def track_processes():
    """Tracks top CPU consuming processes."""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
            try:
                processes.append((proc.info['cpu_percent'], proc.info['pid'], proc.info['name']))
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        # Get top 5 processes
        top_processes = sorted(processes, reverse=True)[:5]
        for cpu, pid, name in top_processes:
            if cpu > PROCESS_THRESHOLD:
                logging.warning(f"High CPU Process: {name} (PID: {pid}) - {cpu}%")
        return top_processes
    except Exception as e:
        logging.error(f"Error tracking processes: {e}")
        return []

def create_table(cpu, ram, disk, net_sent, net_recv, processes=None):
    """Creates a Rich Table with system metrics and color coding."""
    table = Table(title="System Monitoring Dashboard", style="bold magenta")
    table.add_column("Metric", justify="left", style="cyan")
    table.add_column("Value", justify="right", style="yellow")

    # System stats
    cpu_color = "red" if cpu > CPU_THRESHOLD else "green"
    ram_color = "red" if ram > RAM_THRESHOLD else "green"
    disk_color = "red" if disk > DISK_THRESHOLD else "green"
    
    table.add_row("CPU Usage", f"[{cpu_color}]{cpu:.1f}%[/{cpu_color}]")
    table.add_row("RAM Usage", f"[{ram_color}]{ram:.1f}%[/{ram_color}]")
    table.add_row("Disk Usage", f"[{disk_color}]{disk:.1f}%[/{disk_color}]")
    table.add_row("Network Sent", f"{net_sent:.2f} MB/s")
    table.add_row("Network Recv", f"{net_recv:.2f} MB/s")
    
    # Add process information if available
    if processes:
        table.add_row("", "")
        table.add_row("[bold]Top Processes[/bold]", "[bold]CPU %[/bold]")
        for cpu, pid, name in processes:
            proc_color = "red" if cpu > PROCESS_THRESHOLD else "yellow"
            table.add_row(f"{name} (PID: {pid})", f"[{proc_color}]{cpu:.1f}%[/{proc_color}]")

    return table

def main():
    prev_net = None
    first_iteration = True
    
    with Live(console=console, auto_refresh=False) as live:
        while True:
            # Get system stats
            cpu, ram, disk = get_system_stats()
            
            # Get network stats
            current_net = psutil.net_io_counters()
            
            # Calculate network rates (skip first iteration)
            if first_iteration:
                net_sent = 0.0
                net_recv = 0.0
                first_iteration = False
            else:
                time_elapsed = 3  # seconds
                net_sent = (current_net.bytes_sent - prev_net.bytes_sent) / (1024 * 1024 * time_elapsed)
                net_recv = (current_net.bytes_recv - prev_net.bytes_recv) / (1024 * 1024 * time_elapsed)
            
            prev_net = current_net
            
            # Track processes
            top_processes = track_processes()
            
            # Log anomalies
            log_anomalies(cpu, ram, disk)
            
            # Create and update table
            table = create_table(cpu, ram, disk, net_sent, net_recv, top_processes)
            
            # Update display
            live.update(table)
            live.refresh()
            
            time.sleep(3)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Monitoring stopped by user[/bold red]")
    except Exception as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
        logging.error(f"Critical error: {e}")