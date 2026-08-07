from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class DriverCapabilities:
    """Describes which operations the current audio driver supports."""

    can_create_virtual_hub: bool = False
    can_use_external_virtual_device: bool = False
    can_switch_default_device: bool = False


class BaseAudioDriver(ABC):
    HUB_NAME = "MultiEarbudSink"
    supports_virtual_hub = False
    supports_default_device_switch = False
    supports_external_virtual_device = False
    _deprecated = False  # Subclasses may set True to indicate pending removal

    def get_capabilities(self) -> DriverCapabilities:
        """Return a structured description of this driver's capabilities.

        Subclasses may override this to provide dynamic capability detection.
        The default implementation reads the legacy class-level flags.
        """
        return DriverCapabilities(
            can_create_virtual_hub=self.supports_virtual_hub,
            can_use_external_virtual_device=self.supports_external_virtual_device,
            can_switch_default_device=self.supports_default_device_switch,
        )

    @abstractmethod
    def get_connected_sinks(self) -> list[dict]:
        """Returns list of active Bluetooth sinks: [{'name': str, 'desc': str}]"""
        pass

    @abstractmethod
    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        """Sets output volume (0-100) for a specific device."""
        pass

    @abstractmethod
    def update_hub(self) -> None:
        """Combines all available Bluetooth sinks into a single virtual output hub."""
        pass

    @abstractmethod
    def unload_hub(self) -> None:
        """Removes the combined virtual hub."""
        pass

    def has_usable_hub_device(self) -> bool:
        """Returns True when the platform already has a usable hub or virtual device."""
        return False