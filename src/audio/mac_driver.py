"""Pure-Python macOS audio driver via ``SwitchAudioSource``.

.. deprecated::
    This driver is deprecated. Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver`
    instead. The native C++ bridge provides better performance and reliability.
    This fallback will be removed in a future release once the bridge reaches feature parity.
"""

import subprocess
import shutil
from .base import BaseAudioDriver

class MacAudioDriver(BaseAudioDriver):
    """Pure-Python macOS audio driver via ``SwitchAudioSource``.

    .. deprecated::
        Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver` instead.
    """
    _deprecated = True
    supports_default_device_switch = True
    supports_external_virtual_device = True

    def __init__(self):
        self._previous_default_sink = None

    def _switch_audio_source(self, *args) -> subprocess.CompletedProcess:
        return subprocess.run(["SwitchAudioSource", *args], check=False, capture_output=True, text=True)

    def _has_switch_audio_source(self) -> bool:
        return shutil.which("SwitchAudioSource") is not None

    def _is_virtual_hub_device(self, device_name: str) -> bool:
        normalized = device_name.lower()
        return any(
            keyword in normalized
            for keyword in (
                "multi-output",
                "aggregate",
                "virtual",
                "loopback",
                "blackhole",
                "soundflower",
            )
        )

    def get_connected_sinks(self) -> list[dict]:
        if not self._has_switch_audio_source():
            return []

        try:
            output = self._switch_audio_source("-a", "-t", "output").stdout
            sinks = []
            for line in output.splitlines():
                device_name = line.strip()
                normalized = device_name.lower()
                if any(keyword in normalized for keyword in ("bluetooth", "airpods", "headphone", "earbud", "buds")):
                    sinks.append({"name": device_name, "desc": device_name, "id": device_name})
            return sinks
        except Exception:
            return []

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        if self._has_switch_audio_source():
            self._switch_audio_source("-s", sink_name, "-t", "output")
        subprocess.run(["osascript", "-e", f"set volume output volume {volume_percent}"], check=False)

    def update_hub(self) -> None:
        if not self._has_switch_audio_source():
            print("[MacDriver] SwitchAudioSource is not installed.")
            return

        output_devices = self._switch_audio_source("-a", "-t", "output").stdout.splitlines()
        virtual_device = None
        for line in output_devices:
            device_name = line.strip()
            if device_name and self._is_virtual_hub_device(device_name):
                virtual_device = device_name
                break

        if virtual_device is None:
            print(
                "[MacDriver] No aggregate or multi-output device found. "
                "Create one in Audio MIDI Setup and retry."
            )
            return

        self._previous_default_sink = self._current_output_device()
        result = self._switch_audio_source("-s", virtual_device, "-t", "output")
        if result.returncode == 0:
            print(f"[MacDriver] Default output switched to virtual device {virtual_device}")
        else:
            print(f"[MacDriver] Failed to switch output: {result.stderr.strip()}")

    def _current_output_device(self) -> str | None:
        if not self._has_switch_audio_source():
            return None
        result = self._switch_audio_source("-c", "-t", "output")
        if result.returncode != 0:
            return None
        return result.stdout.strip() or None

    def unload_hub(self) -> None:
        if self._previous_default_sink and self._has_switch_audio_source():
            self._switch_audio_source("-s", self._previous_default_sink, "-t", "output")

    def has_usable_hub_device(self) -> bool:
        if not self._has_switch_audio_source():
            return False

        result = self._switch_audio_source("-a", "-t", "output")
        if result.returncode != 0:
            return False

        for line in result.stdout.splitlines():
            device_name = line.strip()
            if device_name and self._is_virtual_hub_device(device_name):
                return True
        return False