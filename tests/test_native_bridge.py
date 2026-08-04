import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "native" / ("multi_earbud_bridge.exe" if sys.platform == "win32" else "multi_earbud_bridge")


def test_help_command_returns_json():
    assert BRIDGE.exists(), f"Native bridge not built at {BRIDGE}"

    result = subprocess.run([str(BRIDGE), "help"], capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout + result.stderr

    payload = json.loads(result.stdout.strip())
    assert payload["ok"] is True
    assert "Available commands" in payload["message"]


def test_all_commands_return_valid_json():
    assert BRIDGE.exists(), f"Native bridge not built at {BRIDGE}"

    commands = [
        ["list_sinks"],
        ["has_usable_hub_device"],
        ["update_hub"],
        ["unload_hub"],
        ["set_volume", "TestSink", "50"],
    ]

    for cmd in commands:
        result = subprocess.run([str(BRIDGE), *cmd], capture_output=True, text=True, check=False)
        assert result.returncode == 0, f"{cmd} exited {result.returncode}: {result.stdout + result.stderr}"
        payload = json.loads(result.stdout.strip())
        assert "ok" in payload
        assert "sinks" in payload
        assert "available" in payload


def test_bridge_missing_command_returns_error_json():
    assert BRIDGE.exists(), f"Native bridge not built at {BRIDGE}"

    result = subprocess.run([str(BRIDGE)], capture_output=True, text=True, check=False)
    assert result.returncode == 1, result.stdout + result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["ok"] is False
