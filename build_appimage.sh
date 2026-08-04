#!/bin/bash
set -e

echo "=== Building Open Multi-Earbud Hub AppImage ==="

# Clean old build artifacts
rm -rf build dist AppDir *.spec

# 0. Build native audio bridge
if command -v cmake &> /dev/null; then
  cmake -S native_bridge -B native_bridge/build
  cmake --build native_bridge/build --config Release
else
  echo "cmake not found; native bridge build skipped"
fi

# 1. Compile Python bundle with new binary name
pyinstaller --noconfirm --onedir --windowed \
  --name "open-multi-earbud-hub" \
  --add-data "src:src" \
  --add-data "assets:assets" \
  --add-data "systemd:systemd" \
  --add-data "native:native" \
  run.py

# 2. Assemble AppDir layout
mkdir -p AppDir/usr/bin AppDir/usr/share/icons/hicolor/scalable/apps
cp -r dist/open-multi-earbud-hub/* AppDir/usr/bin/
if [ -d native ]; then
  mkdir -p AppDir/usr/bin/native
  cp -r native/* AppDir/usr/bin/native/
fi
cp assets/multi-bt-hub.desktop AppDir/
cp assets/multi-bt-hub.desktop AppDir/open-multi-earbud-hub.desktop
touch AppDir/audio-headphones.png

# 3. Create entrypoint runner
cat << 'APPRUN' > AppDir/AppRun
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/open-multi-earbud-hub" "$@"
APPRUN
chmod +x AppDir/AppRun

# 4. Generate AppImage with the new name
ARCH=x86_64 appimagetool AppDir Open-Multi-Earbud-Hub-x86_64.AppImage

echo "=== Build Complete: Open-Multi-Earbud-Hub-x86_64.AppImage ==="
