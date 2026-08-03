import subprocess
from .base import BaseAudioDriver

class MacAudioDriver(BaseAudioDriver):

    def get_connected_sinks(self) -> list[dict]:
        try:
            output = subprocess.check_output(["SwitchAudioSource", "-a", "-t", "output"]).decode("utf-8")
            sinks = []
            for line in output.splitlines():
                if "Bluetooth" in line or "AirPods" in line:
                    sinks.append({"name": line.strip(), "desc": line.strip()})
            return sinks
        except Exception:
            return []

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        subprocess.run(["osascript", "-e", f"set volume output volume {volume_percent}"])

    def update_hub(self) -> None:
        # Automate CoreAudio Aggregate Device via osascript or PyObjC
        pass

    def unload_hub(self) -> None:
        pass