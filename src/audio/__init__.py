import sys
from .base import BaseAudioDriver

def get_audio_driver() -> BaseAudioDriver:
    try:
        from .native_bridge import NativeBridgeAudioDriver
        native_driver = NativeBridgeAudioDriver()
        if native_driver.is_available():
            return native_driver
    except Exception:
        pass

    if sys.platform.startswith("linux"):
        from .linux_driver import LinuxAudioDriver
        return LinuxAudioDriver()
    elif sys.platform == "win32":
        from .windows_driver import WindowsAudioDriver
        return WindowsAudioDriver()
    elif sys.platform == "darwin":
        from .mac_driver import MacAudioDriver
        return MacAudioDriver()
    else:
        raise NotImplementedError(f"Unsupported Operating System: {sys.platform}")