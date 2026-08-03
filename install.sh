#!/bin/bash
set -e

echo "=== Installing Multi-Earbud Hub ==="

# 1. Install System Dependencies (Fedora)
if command -v dnf &> /dev/null; then
    echo "[Installer] Installing system dependencies via DNF..."
    sudo dnf install -y python3-pyqt6 python3-dbus python3-gobject
fi

# 2. Setup Desktop Launcher
echo "[Installer] Setting up desktop shortcut..."
mkdir -p ~/.local/share/applications
cp assets/multi-bt-hub.desktop ~/.local/share/applications/

# 3. Setup Systemd Service
echo "[Installer] Setting up background daemon service..."
mkdir -p ~/.config/systemd/user
cp systemd/multi-bt-hub.service ~/.config/systemd/user/

# Replace WorkingDirectory in service file with current directory
SED_DIR=$(pwd)
sed -i "s|WorkingDirectory=.*|WorkingDirectory=$SED_DIR|g" ~/.config/systemd/user/multi-bt-hub.service

# 4. Enable Service
systemctl --user daemon-reload
systemctl --user enable --now multi-bt-hub.service

echo "=== Installation Successful! ==="
echo "Launch 'Multi-Earbud Hub' from your desktop application menu."