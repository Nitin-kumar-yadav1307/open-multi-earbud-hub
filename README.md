<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:007acc,100:00d4ff&height=220&section=header&text=Open%20Multi-Earbud%20Hub&fontSize=40&fontColor=ffffff&animation=fadeIn&subtext=Unified%20Desktop%20Control%20for%20Wireless%20Earbuds&subFontSize=16" width="100%" alt="Header Banner" />

[![GitHub Release](https://img.shields.io/github/v/release/Nitin-Kumar-yadav1307/open-multi-earbud-hub?color=007acc&style=for-the-badge)](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/releases/latest)
[![Platform Support](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-informational?style=for-the-badge)](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/releases)
[![License](https://img.shields.io/github/license/Nitin-Kumar-yadav1307/open-multi-earbud-hub?style=for-the-badge)](LICENSE)

[Download Executables](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/releases/latest) · [Report Bug](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/issues) · [Request Feature](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/issues)

</div>

---

## ✨ Features

* **🎛️ Unified Control:** Manage Active Noise Cancellation (ANC), Transparency mode, and EQ presets directly from your desktop.
* **🔋 Battery Monitoring:** Real-time battery level tracking for left earbud, right earbud, and charging case.
* **⚡ Hotkey Integration:** Rapidly toggle audio modes using customizable global keyboard shortcuts.
* **🌐 Cross-Platform UI:** Native interface built with PyQt6 on **Linux**, **Windows**, and **macOS**.
* **🧩 Platform-Specific Audio Support:** Linux creates a combined virtual sink natively; macOS and Windows can switch to an existing aggregate or virtual audio device, with volume control and device detection.

---

## ⚡ Quickstart

Get up and running immediately with pre-built binaries:

1. Head to the **[Latest Releases](https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub/releases/latest)** page.
2. Download the package for your operating system:
   * 🐧 **Linux:** `Open-Multi-Earbud-Hub-Linux.zip`
   * 🪟 **Windows:** `Open-Multi-Earbud-Hub-Windows.zip`
   * 🍏 **macOS:** `Open-Multi-Earbud-Hub-macOS.zip`
3. Extract the contents and launch the `Open-Multi-Earbud-Hub` application.

### Platform Notes

* **Linux:** the app creates and removes a combined sink automatically when multiple Bluetooth earbuds are connected.
* **macOS:** create a Multi-Output or Aggregate Device in Audio MIDI Setup, then launch the app and sync to that virtual output.
* **Windows:** install a virtual audio device such as VB-Audio Cable or Voicemeeter, then launch the app and sync to that virtual output.

---

## 🛠️ Developer Setup & Local Building

To set up the project locally for development or run from source:

### 1. Prerequisites

* Python `3.11` or higher installed.

<details>
<summary><b>🐧 System Dependencies for Linux (Click to expand)</b></summary>

Linux requires native D-Bus, GObject, and GLib development libraries before installing Python packages:

```bash
# Ubuntu / Debian
sudo apt update
sudo apt install -y libdbus-1-dev libglib2.0-dev gobject-introspection libgirepository1.0-dev libcairo2-dev pkg-config build-essential

# Fedora
sudo dnf install dbus-devel glib2-devel gobject-introspection-devel cairo-gobject-devel pkgconfig gcc
```

</details>

### 2. Environment Setup

```bash
# Clone the repository
git clone https://github.com/Nitin-Kumar-yadav1307/open-multi-earbud-hub.git
cd open-multi-earbud-hub

# Create a virtual environment
python -m venv venv

# Activate virtual environment
# On Linux / macOS:
source venv/bin/activate
# On Windows:
# venv\Scripts\activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Run Application

```bash
python run.py
```

### Native Bridge Build

The app will use the compiled C++ bridge from `native/` when it is available.
To build it manually during development:

```bash
cmake -S native_bridge -B native_bridge/build
cmake --build native_bridge/build -j2
```

---

## 🧪 Testing

To run the test suites locally, see [`docs/testing.md`](docs/testing.md).

In short:

```bash
# Install test dependencies
python -m pip install -r requirements-dev.txt

# Run Python tests
python -m pytest tests/ -v

# Build and run C++ tests
cmake -S native_bridge -B native_bridge/build
cmake --build native_bridge/build --target multi_earbud_bridge_tests
cd native_bridge/build && ctest --output-on-failure
```

---



## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.



---

