import sys
import argparse
from .gui import launch_gui
from .daemon import run_daemon

def main():
    parser = argparse.ArgumentParser(description="Multi-Earbud Hub Manager")
    parser.add_argument("--gui", action="store_true", help="Launch the PyQt6 graphical interface")
    parser.add_argument("--daemon", action="store_true", help="Run as background D-Bus listener daemon")

    args = parser.parse_args()

    if args.daemon:
        run_daemon()
    else:
        launch_gui()

if __name__ == "__main__":
    main()