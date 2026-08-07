"""Pure-Python Windows audio driver via ``pycaw``.

.. deprecated::
    This driver is deprecated. Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver`
    instead. The native C++ bridge provides better performance and reliability.
    This fallback will be removed in a future release once the bridge reaches feature parity.
"""

import logging
import warnings

from pycaw.constants import DEVICE_STATE, EDataFlow
from pycaw.pycaw import AudioUtilities
from .base import BaseAudioDriver

logger = logging.getLogger(__name__)


class WindowsAudioDriver(BaseAudioDriver):
    """Pure-Python Windows audio driver via ``pycaw``.

    .. deprecated::
        Use :class:`~src.audio.native_bridge.NativeBridgeAudioDriver` instead.
    """
    _deprecated = True
    supports_default_device_switch = True
    supports_external_virtual_device = True

    def __init__(self):
        self._previous_default_device_id = None

    def _connected_output_devices(self):
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            try:
                return AudioUtilities.GetAllDevices(
                    data_flow=EDataFlow.eRender.value,
                    device_state=DEVICE_STATE.ACTIVE.value,
                )
            except Exception as exc:
                logger.error("Error fetching devices: %s", exc)
                return []

    def _is_earbud_device(self, device_name: str) -> bool:
        normalized = device_name.lower()
        return any(
            keyword in normalized
            for keyword in ("bluetooth", "headphone", "earbud", "buds", "airpods")
        )

    def _is_virtual_hub_device(self, device_name: str) -> bool:
        normalized = device_name.lower()
        return any(
            keyword in normalized
            for keyword in (
                "voicemeeter",
                "vb-audio",
                "virtual cable",
                "cable input",
                "loopback",
                "aggregate",
                "multi-output",
            )
        )

    def get_connected_sinks(self) -> list[dict]:
        sinks = []
        for device in self._connected_output_devices():
            device_name = getattr(device, "FriendlyName", None) or getattr(device, "name", None)
            device_id = getattr(device, "id", None)
            if not device_name or not device_id:
                continue
            if self._is_earbud_device(device_name):
                sinks.append({"name": device_id, "desc": device_name, "id": device_id})
        return sinks

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        devices = self._connected_output_devices()
        target_device = None
        for device in devices:
            device_id = getattr(device, "id", None)
            device_name = getattr(device, "FriendlyName", None)
            if sink_name in {device_id, device_name}:
                target_device = device
                break

        if target_device is None:
            target_device = next(iter(devices), None)

        if target_device is None:
            logger.warning("No matching device found for volume update: %s", sink_name)
            return

        try:
            target_device.volume_percent = volume_percent
        except Exception as exc:
            logger.error("Failed to set volume for %s: %s", sink_name, exc)

    def update_hub(self) -> None:
        devices = self._connected_output_devices()
        if not devices:
            logger.warning("No output devices available.")
            return

        if self._previous_default_device_id is None:
            try:
                self._previous_default_device_id = AudioUtilities.GetSpeakers().id
            except Exception:
                self._previous_default_device_id = None

        target = None
        for device in devices:
            device_name = getattr(device, "FriendlyName", None) or getattr(device, "name", None)
            device_id = getattr(device, "id", None)
            if device_name and device_id and self._is_virtual_hub_device(device_name):
                target = {"id": device_id, "desc": device_name}
                break

        if target is None:
            logger.warning(
                "No virtual audio device found. Install a virtual audio cable or Voicemeeter and retry."
            )
            return

        try:
            AudioUtilities.SetDefaultDevice(target["id"])
            logger.info("Default output switched to virtual device %s", target["desc"])
        except Exception as exc:
            logger.error("Failed to switch default output: %s", exc)

    def unload_hub(self) -> None:
        if not self._previous_default_device_id:
            return

        try:
            AudioUtilities.SetDefaultDevice(self._previous_default_device_id)
            logger.info("Restored previous default output device")
        except Exception as exc:
            logger.error("Failed to restore default output: %s", exc)

    def has_usable_hub_device(self) -> bool:
        for device in self._connected_output_devices():
            device_name = getattr(device, "FriendlyName", None) or getattr(device, "name", None)
            if device_name and self._is_virtual_hub_device(device_name):
                return True
        return False