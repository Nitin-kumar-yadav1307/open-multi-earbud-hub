import sys
import argparse
import logging

from .gui import launch_gui
from .daemon import run_daemon

def main():
    parser = argparse.ArgumentParser(description="Multi-Earbud Hub Manager")
    parser.add_argument("--gui", action="store_true", help="Launch the PyQt6 graphical interface")
    parser.add_argument("--daemon", action="store_true", help="Run as background D-Bus listener daemon")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="[%(levelname)s] %(name)s: %(message)s",
        stream=sys.stderr,
    )

    if args.daemon:
        run_daemon()
    else:
        launch_gui()

if __name__ == "__main__":
    main()