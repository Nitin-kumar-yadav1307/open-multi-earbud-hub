import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QPushButton, QSlider, QFrame)
from PyQt6.QtCore import Qt, QTimer
from .audio import get_audio_driver

class EarbudHubGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = get_audio_driver()
        
        self.setWindowTitle("Multi-Earbud Hub")
        self.setFixedSize(420, 360)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("Multi-Earbud Audio Controller")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #3584e4;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(title)

        self.status_label = QLabel("Scanning Bluetooth devices...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #777; font-size: 10pt;")
        self.layout.addWidget(self.status_label)

        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        self.layout.addWidget(line)

        self.devices_widget = QWidget()
        self.devices_layout = QVBoxLayout(self.devices_widget)
        self.layout.addWidget(self.devices_widget)

        self.layout.addStretch()

        self.sync_btn = QPushButton("Force Sync Virtual Hub")
        self.sync_btn.setStyleSheet("padding: 8px; font-weight: bold;")
        self.sync_btn.clicked.connect(self.manual_sync)
        self.layout.addWidget(self.sync_btn)

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(3000)

        self.refresh_devices()

    def refresh_devices(self):
        sinks = self.driver.get_connected_sinks()
        
        for i in reversed(range(self.devices_layout.count())): 
            widget = self.devices_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)

        if not sinks:
            self.status_label.setText("No Bluetooth earpods connected.")
            return

        self.status_label.setText(f"Connected Earpods: {len(sinks)}")

        for dev in sinks:
            dev_box = QHBoxLayout()
            lbl = QLabel(dev["desc"])
            lbl.setStyleSheet("font-size: 11pt;")
            
            slider = QSlider(Qt.Orientation.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(100)
            slider.valueChanged.connect(lambda val, s_name=dev["name"]: self.driver.set_volume(s_name, val))
            
            dev_box.addWidget(lbl)
            dev_box.addWidget(slider)
            
            container = QWidget()
            container.setLayout(dev_box)
            self.devices_layout.addWidget(container)

    def manual_sync(self):
        self.driver.update_hub()
        self.refresh_devices()

def launch_gui():
    app = QApplication(sys.argv)
    window = EarbudHubGUI()
    window.show()
    sys.exit(app.exec())