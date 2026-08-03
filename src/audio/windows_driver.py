import sounddevice as sd
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from .base import BaseAudioDriver

class WindowsAudioDriver(BaseAudioDriver):

    def get_connected_sinks(self) -> list[dict]:
        devices = sd.query_devices()
        sinks = []
        for dev in devices:
            if dev['max_output_channels'] > 0 and ("Bluetooth" in dev['name'] or "Headphone" in dev['name']):
                sinks.append({"name": str(dev['index']), "desc": dev['name']})
        return sinks

    def set_volume(self, sink_name: str, volume_percent: int) -> None:
        sessions = AudioUtilities.GetAllSessions()
        for session in sessions:
            volume = session._ctl.QueryInterface(ISimpleAudioVolume)
            if session.Process and session.Process.name():
                volume.SetMasterVolume(volume_percent / 100.0, None)

    def update_hub(self) -> None:
        # Code to route input audio buffer concurrently to multiple output streams
        pass

    def unload_hub(self) -> None:
        pass