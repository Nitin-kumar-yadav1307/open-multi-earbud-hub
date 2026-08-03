from abc import ABC, abstractmethod

class BaseAudioDriver(ABC):
    HUB_NAME = "MultiEarbudSink"
    supports_virtual_hub = False
    supports_default_device_switch = False
    supports_external_virtual_device = False

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