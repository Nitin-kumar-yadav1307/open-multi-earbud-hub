"""Pure-Python Linux audio driver via ``pactl``.

.. deprecated::
    This driver is deprecated. Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver`
    instead. The native C++ bridge provides better performance and reliability.
    This fallback will be removed in a future release once the bridge reaches feature parity.
"""

import logging
import subprocess
import time
import re
from .base import BaseAudioDriver

logger = logging.getLogger(__name__)


class LinuxAudioDriver(BaseAudioDriver):
    """Pure-Python Linux audio driver via ``pactl``.

    .. deprecated::
        Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver` instead.
    """
    _deprecated = True
    supports_virtual_hub = True

    def get_connected_sinks(self) -> list[dict]:
        try:
            output = subprocess.check_output(["pactl", "list", "sinks"]).decode("utf-8")
            sinks = []
            blocks = output.split("Sink #")
            for block in blocks[1:]:
                name_match = re.search(r"Name:\s+(bluez_output\.[^\s]+)", block)
                desc_match = re.search(r"Description:\s+(.+)", block)
                if name_match and desc_match:
                    sinks.append({
                        "name": name_match.group(1),
                        "desc": desc_match.group(1).strip()
                    })
            return sinks
        except Exception as e:
            logger.error("Error fetching sinks: %s", e)
            return []

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        subprocess.run(["pactl", "set-sink-volume", sink_name, f"{volume_percent}%"])

    def unload_hub(self) -> None:
        try:
            output = subprocess.check_output(["pactl", "list", "modules", "short"]).decode("utf-8")
            for line in output.splitlines():
                if "module-combine-sink" in line and self.HUB_NAME in line:
                    module_id = line.split()[0]
                    subprocess.run(["pactl", "unload-module", module_id])
                    logger.info("Unloaded old hub module (ID: %s)", module_id)
        except Exception as e:
            logger.error("Error unloading hub: %s", e)

    def update_hub(self) -> None:
        time.sleep(5)  # Allow PipeWire sink registration to settle
        sinks = [s["name"] for s in self.get_connected_sinks()]
        self.unload_hub()

        if len(sinks) >= 2:
            sink_list_str = ",".join(sinks)
            cmd = [
                "pactl", "load-module", "module-combine-sink",
                f"sink_name={self.HUB_NAME}",
                "sink_properties=device.description=Multi-Earbud-Hub",
                f"sinks={sink_list_str}"
            ]
            try:
                module_id = subprocess.check_output(cmd).decode("utf-8").strip()
                subprocess.run(["pactl", "set-default-sink", self.HUB_NAME])
                logger.info("Created Multi-Earbud Hub for %d devices (Module: %s)", len(sinks), module_id)
            except Exception as e:
                logger.error("Sync failed: %s", e)
        else:
            logger.info("Only %d Bluetooth sink(s) active. Standby.", len(sinks))