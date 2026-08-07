from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from .base import BaseAudioDriver


class BridgeError(Exception):
    """Base exception for native bridge failures."""


class BridgeInvalidArgumentsError(BridgeError):
    """Raised when the bridge receives an unknown command or invalid arguments."""


class BridgeBackendError(BridgeError):
    """Raised when the platform backend reports an error (e.g., missing tool, permission denied)."""


class BridgeInternalError(BridgeError):
    """Raised when the bridge encounters an unexpected internal error."""


# Maps C++ ErrorCode integer values to Python exception classes.
# Extend this dict when new error codes are added to native_bridge/include/bridge/types.hpp.
ERROR_CODE_MAP: dict[int, type[BridgeError]] = {
    1: BridgeInvalidArgumentsError,
    2: BridgeBackendError,
    3: BridgeInternalError,
}


class NativeBridgeAudioDriver(BaseAudioDriver):
    supports_virtual_hub = True
    supports_external_virtual_device = True

    def __init__(self):
        self._bridge_path = self._resolve_bridge_path()

    def _resolve_bridge_path(self) -> Path:
        base_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
        executable_name = "multi_earbud_bridge.exe" if sys.platform == "win32" else "multi_earbud_bridge"
        return base_dir / "native" / executable_name

    def is_available(self) -> bool:
        return self._bridge_path.exists()

    def _run_bridge(self, command: str, payload: dict | None = None) -> dict:
        if not self._bridge_path.exists():
            raise FileNotFoundError(f"Native bridge not found at {self._bridge_path}")

        args = [command]
        if payload and command == "set_volume":
            args.extend([str(payload.get("sink_name", "")), str(payload.get("volume_percent", 0))])

        result = subprocess.run(
            [str(self._bridge_path), *args],
            text=True,
            capture_output=True,
            check=False,
        )

        if result.returncode != 0:
            raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "Native bridge failed")

        output = result.stdout.strip() or "{}"
        response = json.loads(output)

        ok = response.get("ok", True)
        error_code = response.get("error_code")
        message = response.get("message", "")

        if not ok or (error_code is not None and error_code != 0):
            if error_code is not None and error_code != 0:
                exc_class = ERROR_CODE_MAP.get(error_code, BridgeInternalError)
                raise exc_class(f"[{error_code}] {message}")
            raise BridgeError(message)

        return response

    def get_connected_sinks(self) -> list[dict]:
        response = self._run_bridge("list_sinks")
        return response.get("sinks", [])

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        self._run_bridge("set_volume", {"sink_name": sink_name, "volume_percent": volume_percent})

    def update_hub(self) -> None:
        self._run_bridge("update_hub")

    def unload_hub(self) -> None:
        self._run_bridge("unload_hub")

    def has_usable_hub_device(self) -> bool:
        response = self._run_bridge("has_usable_hub_device")
        return bool(response.get("available", False))