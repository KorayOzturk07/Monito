import psutil
import logging
from typing import List, Tuple, Dict, Any
from collections import deque
from datetime import datetime

class SystemMonitor:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.history = {
            'cpu': deque(maxlen=config['monitoring']['history_size']),
            'ram': deque(maxlen=config['monitoring']['history_size']),
            'disk': deque(maxlen=config['monitoring']['history_size']),
            'network': deque(maxlen=config['monitoring']['history_size'])
        }
        self.prev_net = None
        self.first_iteration = True

    def get_system_stats(self) -> Dict[str, float]:
        """Collect system statistics."""
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        disk = psutil.disk_usage('/').percent
        
        # Get network stats
        current_net = psutil.net_io_counters()
        
        if self.first_iteration:
            net_sent = 0.0
            net_recv = 0.0
            self.first_iteration = False
        else:
            time_elapsed = self.config['monitoring']['update_interval']
            net_sent = (current_net.bytes_sent - self.prev_net.bytes_sent) / (1024 * 1024 * time_elapsed)
            net_recv = (current_net.bytes_recv - self.prev_net.bytes_recv) / (1024 * 1024 * time_elapsed)
        
        self.prev_net = current_net
        
        # Update history
        self.history['cpu'].append((datetime.now(), cpu))
        self.history['ram'].append((datetime.now(), ram))
        self.history['disk'].append((datetime.now(), disk))
        self.history['network'].append((datetime.now(), (net_sent, net_recv)))
        
        return {
            'cpu': cpu,
            'ram': ram,
            'disk': disk,
            'network_sent': net_sent,
            'network_recv': net_recv
        }

    def get_top_processes(self) -> List[Tuple[float, int, str]]:
        """Get top CPU consuming processes."""
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
                try:
                    processes.append((proc.info['cpu_percent'], proc.info['pid'], proc.info['name']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            return sorted(processes, reverse=True)[:self.config['monitoring']['top_processes']]
        except Exception as e:
            logging.error(f"Error tracking processes: {e}")
            return []

    def check_thresholds(self, stats: Dict[str, float]) -> List[str]:
        """Check if any metrics exceed thresholds."""
        alerts = []
        thresholds = self.config['thresholds']
        
        if stats['cpu'] > thresholds['cpu']:
            alerts.append(f"High CPU Usage: {stats['cpu']:.1f}%")
        if stats['ram'] > thresholds['ram']:
            alerts.append(f"High RAM Usage: {stats['ram']:.1f}%")
        if stats['disk'] > thresholds['disk']:
            alerts.append(f"High Disk Usage: {stats['disk']:.1f}%")
        
        return alerts

    def get_system_health_score(self) -> float:
        """Calculate a system health score based on current metrics."""
        stats = self.get_system_stats()
        weights = {'cpu': 0.4, 'ram': 0.3, 'disk': 0.3}
        
        score = 100
        for metric, weight in weights.items():
            usage = stats[metric]
            if usage > self.config['thresholds'][metric]:
                score -= (usage - self.config['thresholds'][metric]) * weight
        
        return max(0, min(100, score)) 