import pytest
from src.audio.base import BaseAudioDriver, DriverCapabilities


class ConcreteDriver(BaseAudioDriver):
    def get_connected_sinks(self):
        return []

    def set_volume(self, sink_name, volume_percent):
        pass

    def update_hub(self):
        pass

    def unload_hub(self):
        pass


def test_default_capabilities():
    driver = ConcreteDriver()
    caps = driver.get_capabilities()

    assert isinstance(caps, DriverCapabilities)
    assert caps.can_create_virtual_hub is False
    assert caps.can_use_external_virtual_device is False
    assert caps.can_switch_default_device is False


def test_capabilities_from_flags():
    class CustomDriver(ConcreteDriver):
        supports_virtual_hub = True
        supports_external_virtual_device = True
        supports_default_device_switch = True

    driver = CustomDriver()
    caps = driver.get_capabilities()

    assert caps.can_create_virtual_hub is True
    assert caps.can_use_external_virtual_device is True
    assert caps.can_switch_default_device is True


def test_capabilities_are_frozen():
    driver = ConcreteDriver()
    caps = driver.get_capabilities()

    with pytest.raises(AttributeError):
        caps.can_create_virtual_hub = True  # type: ignore[misc]