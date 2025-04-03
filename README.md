

```                                                            

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

```                                                              
                                                                 



# Monito - System Monitoring Dashboard

Monito is a real-time system monitoring tool built in Python using psutil and rich. It tracks CPU, RAM, disk usage, network activity, and top CPU-consuming processes, displaying the data in a dynamic terminal dashboard.

---

## Features
- **Real-time System Stats:** Monitors CPU, RAM, disk usage, and network activity.
- **Process Tracking:** Displays the top CPU-consuming processes.
- **Anomaly Logging:** Logs high resource usage in `monito.log`.
- **Dynamic Terminal UI:** Uses rich to display an interactive dashboard.

---

## Installation

### Requirements
Ensure you have Python 3 installed, then install dependencies:

```bash
pip install psutil rich
```

### Usage
Run the script with:
```bash
python monito.py
```
To stop monitoring, press `CTRL + C`

---

## Configuration

Thresholds for logging can be adjusted in the script:

```bash
CPU_THRESHOLD = 85.0  # CPU Usage %
RAM_THRESHOLD = 85.0  # RAM Usage %
DISK_THRESHOLD = 90.0  # Disk Usage %
PROCESS_THRESHOLD = 50.0  # Process CPU %
```

## Logging
Warnings for high usage are logged in `monito.log`.

## License
This project is licensed under the MIT License.