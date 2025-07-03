# gr1d — Crypto Node Launcher & Monitor

A lightweight automation tool to launch and monitor multiple crypto nodes across various VPS machines.

## 🚀 Features

- **Auto-deployment** of nodes via `build.sh` and `grid_launcher.py`
- Parallel deployment of node containers with unique names
- Simple monitoring logic (see: `monitor.py`)
- Designed for **multi-container, multi-node** environments
- Easily extendable and fast to set up

## 🧱 Components

- `build.sh`: Prepares the environment (installs Docker, dependencies, etc.)
- `grid_launcher.py`: Launches multiple containers based on user input
- `monitor.py`: (Optional) Monitor logs and send alerts if needed
- `requirements.txt`: Minimal Python dependencies

## 🛠️ Usage

```bash
git clone https://github.com/egzakutacno/gr1d.git
cd gr1d
chmod +x build.sh
./build.sh
python3 grid_launcher.py
