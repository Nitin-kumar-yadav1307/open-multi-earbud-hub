import sys
import warnings

from .base import BaseAudioDriver

warnings.simplefilter("default", DeprecationWarning)


def _warn_deprecated_driver(driver_name: str) -> None:
    warnings.warn(
        f"Falling back to deprecated {driver_name}. "
        "The native C++ bridge provides better performance and reliability. "
        "Pre-built binaries are available in GitHub Releases. "
        "See README.md for installation instructions.",
        DeprecationWarning,
        stacklevel=3,
    )


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
        driver = LinuxAudioDriver()
        if getattr(driver, "_deprecated", False):
            _warn_deprecated_driver("LinuxAudioDriver")
        return driver
    elif sys.platform == "win32":
        from .windows_driver import WindowsAudioDriver
        driver = WindowsAudioDriver()
        if getattr(driver, "_deprecated", False):
            _warn_deprecated_driver("WindowsAudioDriver")
        return driver
    elif sys.platform == "darwin":
        from .mac_driver import MacAudioDriver
        driver = MacAudioDriver()
        if getattr(driver, "_deprecated", False):
            _warn_deprecated_driver("MacAudioDriver")
        return driver
    else:
        raise NotImplementedError(f"Unsupported Operating System: {sys.platform}")