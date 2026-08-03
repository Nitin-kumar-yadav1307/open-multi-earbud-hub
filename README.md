# Multi-Earbud Hub 🎧🎧

A cross-platform background engine and GUI application that automatically combines multiple connected Bluetooth earbuds/headsets into a single virtual audio output on Linux (PipeWire/PulseAudio).

## Features
* **Auto-Sync Daemon:** Automatically merges new Bluetooth audio sinks via D-Bus system events.
* **Independent Volume Controls:** Adjust each set of earpods individually using a PyQt6 desktop window.
* **PipeWire & PulseAudio Native:** Leverages Linux audio subsystems without audio delay or quality loss.
* **Modular Driver Architecture:** Built to easily expand support for Windows (WASAPI) and macOS (CoreAudio).

## Quick Start (Linux)

### Installation
Clone the repository and run the auto-installer:
```bash
git clone [https://github.com/](https://github.com/)<your-username>/multi-earbud-hub.git
cd multi-earbud-hub
./install.sh