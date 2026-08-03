import sys
from .audio import get_audio_driver

def run_daemon():
    driver = get_audio_driver()
    print("[Daemon] Starting Multi-Earbud Background Listener...")

    if sys.platform.startswith("linux"):
        import dbus
        from dbus.mainloop.glib import DBusGMainLoop
        from gi.repository import GLib

        def interfaces_added_handler(path, interfaces):
            if "org.bluez.Device1" in interfaces:
                print("[Daemon] Bluetooth event detected! Triggering audio sync...")
                driver.update_hub()

        DBusGMainLoop(set_as_default=True)
        bus = dbus.SystemBus()
        bus.add_signal_receiver(
            interfaces_added_handler,
            dbus_interface="org.freedesktop.DBus.ObjectManager",
            signal_name="InterfacesAdded"
        )
        
        driver.update_hub()
        loop = GLib.MainLoop()
        try:
            loop.run()
        except KeyboardInterrupt:
            print("\n[Daemon] Stopping daemon...")
            driver.unload_hub()
    else:
        print("[Daemon] Background service is currently implemented for Linux D-Bus.")

if __name__ == "__main__":
    run_daemon()