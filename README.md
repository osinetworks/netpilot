# Network Automation Suite

A scalable and modular network automation tool for multi-vendor environments (Arista, Cisco, and more).  
Supports configuration management, backup, inventory collection, and firmware upgrade tasks with full multithreading and YAML-based inventory.

---

## Features

- **Multi-vendor support:** Arista EOS, Cisco IOS, and others via [Netmiko](https://github.com/ktbyers/netmiko)
- **Modular codebase:** Each automation task is its own module
- **YAML-based inventory and configuration**
- **Multithreaded execution for high performance**
- **Centralized logging (debug, info, error)**
- **Separation of credentials, configs, and outputs**
- **Extensive validation and error handling**

---

## Directory Structure

<pre>
project-root/
├── config/ # YAML configs, inventory, and command templates
│ └── commands/ # Device command files (per vendor/task)
├── docs/ # Documentation
├── logs/ # All log files (info, error, debug)
├── output/ # Task results (backups, configs, inventories)
├── scripts/ # Python modules (core logic)
├── test/ # Unit tests
├── utils/ # Helper utilities
├── main.py # Main entry point
├── requirements.txt # Python dependencies
└── README.md # This file

</pre>
---

## Configuration

- **Edit device inventory:**  
  `config/devices.yaml`
- **Edit credentials:**  
  `config/credentials.yaml`
- **Edit task parameters:**  
  `config/config.yaml`
- **Command templates:**  
  `config/commands/*.cfg`

---

## Usage

For script version:
Run an automation task (e.g., configuration deployment):
<pre> ```bash python main.py --task config ``` </pre>
<pre> ```bash python main.py --task backup ``` </pre>

For text gui version:
<pre> ```bash python main_tui.py ``` </pre>

For Web gui version:
web interface can be reached via Network URL: http://<ip_address or hostname>:8501
It is possible to redirect port 8501 to 80 via nginx
<pre> ```bash streamlit run netpilot_gui.py ``` </pre>

Nginx reverse proxy configuration
<pre>
server {
    listen 80;
    server_name osinetworks.lab;
    location / {
        proxy_pass http://localhost:8501/;
        proxy_http_version 1.1;
	      proxy_set_header Upgrade $http_upgrade;
	      proxy_set_header Connection "upgrade";
        include proxy_params;
    }
}
</pre>
---

## GUI Alternatives
Netpilot Automation Suite offers multiple graphical user interfaces (GUIs) to accommodate different user profiles and deployment scenarios:

## 1. Streamlit Web GUI
File: netpilot_gui.py

Type: Web-based (runs in browser)

Description:
Streamlit provides a modern and interactive web application for network automation.

Allows users to run automation tasks (config, backup, inventory) via buttons

Displays live log/status updates for each task

Supports uploading CSV device inventories and vendor-specific command files (e.g., Arista/Cisco backup commands)

Converts CSV files to YAML inventory, displays and saves them automatically

Recommended for customers and non-technical users due to its user-friendly, accessible interface

How to run:

<pre> streamlit run netpilot_gui.py  </pre>

Then open the shown URL in your browser.

## 2. Textual Terminal GUI
File: textual_main.py

Type: Terminal-based (Text User Interface, TUI)

Description:
Textual is a modern TUI framework for Python that brings rich, interactive dashboards to the terminal.

Provides a panel with task buttons (config, backup, inventory, firmware)

Features a live log panel with color/highlighting using RichLog

Fast keyboard navigation and visually appealing for terminal users

Suitable for power users, NOC/SRE staff, and environments where a browser is not available

How to run:

<pre> python main_tui.py </pre> 

## 3. Questionary-based Simple Terminal Menu
File: main_tui.py

Type: Terminal-based (Text Menu)

Description:
This is a minimal and portable terminal UI using the questionary library.

Presents a simple menu to select and run automation tasks

Uses plain text input and output, no mouse needed

Ideal for script lovers, CLI fans, or SSH-only environments

How to run:

<pre> python main_tui.py </pre> 

---

## Contributing
<pre>
Pull requests and issue reports are welcome!
Please submit bug reports, feature requests, or improvements via GitHub. 
</pre>

---

## Example: config/devices.yaml
```yaml 
defaults:
  username: admin
  password: admin
groups:
  cisco:
    device_type: cisco_ios
    enable_secret: admin
  arista:
    device_type: arista_eos
devices:
  - name: arista-sw-001
    host: 172.20.20.101
    group: arista
  - name: arista-sw-002
    host: 172.20.20.102
    group: arista
  - name: cisco-sw-001
    host: 10.10.10.11
    group: cisco
  - name: cisco-sw-002
    host: 10.10.10.12
    group: cisco
```

---

## Example: config/config.yaml

```yaml 
operation_mode: config
supported_device_types: ["arista_eos", "cisco_ios"]

thread_pools:
  num_threads: 10 
  max_queue: 20
```

---

## Example: config/credentials.yaml
```yaml 
default:
  username: "admin"
  password: "admin"
  enable_secret: "admin"

overrides:
  arista-sw-001:
    username: "arista_user"
    password: "arista_pass"
    enable_secret: "arista_secret"
  cisco-sw-001:
    username: "cisco_user"
    password: "cisco_pass"
    enable_secret: "cisco_secret"
```



## Example: config/commands/arista_config_commands.cfg

<pre> 
vlan 100
name USERS
!
interface Ethernet1
switchport access vlan 100
!
</pre>


