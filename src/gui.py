import sys
from PyQt6.QtWidgets import (
    QApplication,
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSlider,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from PyQt6.QtCore import Qt, QTimer
from .audio import get_audio_driver


class SetupWizardDialog(QDialog):
    def __init__(self, driver, parent=None):
        super().__init__(parent)
        self.driver = driver

        self.setWindowTitle("Multi-Earbud Hub Setup")
        self.setMinimumSize(520, 360)

        layout = QVBoxLayout(self)

        title = QLabel("Setup Guide")
        title.setStyleSheet("font-size: 15pt; font-weight: bold; color: #3584e4;")
        layout.addWidget(title)

        self.summary_label = QLabel(self._summary_text())
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("color: #666; font-size: 10pt;")
        layout.addWidget(self.summary_label)

        self.steps = QTextBrowser()
        self.steps.setOpenExternalLinks(True)
        self.steps.setHtml(self._steps_html())
        layout.addWidget(self.steps)

        button_row = QHBoxLayout()
        refresh_btn = QPushButton("Recheck Devices")
        refresh_btn.clicked.connect(self._refresh_state)
        button_row.addWidget(refresh_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        button_row.addWidget(close_btn)

        layout.addLayout(button_row)

    def _summary_text(self):
        capabilities = self.driver.get_capabilities()
        if capabilities.can_create_virtual_hub:
            return "Linux can create and remove the combined sink automatically when multiple Bluetooth earbuds are available."
        if capabilities.can_use_external_virtual_device:
            return "This platform needs an existing aggregate or virtual audio device before the app can sync audio to it."
        return "This platform can detect devices, but it does not support hub creation in the current backend."

    def _steps_html(self):
        capabilities = self.driver.get_capabilities()
        if capabilities.can_create_virtual_hub:
            return """
            <h3>Linux setup</h3>
            <ol>
              <li>Install PipeWire or PulseAudio and the Bluetooth stack.</li>
              <li>Pair at least two Bluetooth earbuds or headphones.</li>
              <li>Press <b>Force Sync Virtual Hub</b> in the main window.</li>
            </ol>
            <p>The app will create a combine-sink output automatically.</p>
            """

        if capabilities.can_use_external_virtual_device:
            if sys.platform == "darwin":
                return """
                <h3>macOS setup</h3>
                <ol>
                  <li>Open <b>Audio MIDI Setup</b>.</li>
                  <li>Create a <b>Multi-Output Device</b> or <b>Aggregate Device</b>.</li>
                  <li>Include your Bluetooth earbuds and any desired output devices.</li>
                  <li>Select that device once, then press <b>Set Active Output Device</b>.</li>
                </ol>
                <p>If you do not see the device, refresh the list after creating it.</p>
                """

            return """
            <h3>Windows setup</h3>
            <ol>
              <li>Install a virtual audio device such as <b>VB-Audio Cable</b> or <b>Voicemeeter</b>.</li>
              <li>Open Windows Sound settings and confirm the virtual device appears as an output.</li>
              <li>Launch this app and press <b>Set Active Output Device</b>.</li>
            </ol>
            <p>If the device does not appear, install or enable the virtual driver first.</p>
            """

        return """
        <h3>Generic setup</h3>
        <p>No additional setup instructions are available for this platform backend.</p>
        """

    def _refresh_state(self):
        self.summary_label.setText(self._summary_text())
        self.steps.setHtml(self._steps_html())


class EarbudHubGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.driver = get_audio_driver()
        self.device_volumes = {}
        
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

        self.capability_label = QLabel(self._capability_text())
        self.capability_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.capability_label.setStyleSheet("color: #999; font-size: 9pt;")
        self.layout.addWidget(self.capability_label)

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

        self.setup_btn = QPushButton("Open Setup Guide")
        self.setup_btn.setStyleSheet("padding: 8px;")
        self.setup_btn.clicked.connect(self.open_setup_guide)
        self.layout.addWidget(self.setup_btn)

        self._update_sync_button_label()

        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_devices)
        self.timer.start(3000)

        self.refresh_devices()

    def _capability_text(self):
        capabilities = self.driver.get_capabilities()
        if capabilities.can_create_virtual_hub:
            return "Linux virtual hub mode: multiple Bluetooth sinks can be combined."
        if capabilities.can_use_external_virtual_device:
            return (
                "This platform can use an existing aggregate or virtual audio device. "
                "Create one first, then sync the hub."
            )
        if capabilities.can_switch_default_device:
            return "This platform supports device switching and volume control."
        return "This platform supports device detection only."

    def _update_sync_button_label(self):
        capabilities = self.driver.get_capabilities()
        if capabilities.can_create_virtual_hub:
            self.sync_btn.setText("Force Sync Virtual Hub")
        elif capabilities.can_switch_default_device:
            self.sync_btn.setText("Set Active Output Device")
        else:
            self.sync_btn.setText("Refresh Devices")

    def refresh_devices(self):
        try:
            sinks = self.driver.get_connected_sinks()
        except Exception as exc:
            self.status_label.setText(f"Failed to scan devices: {exc}")
            return
        
        for i in reversed(range(self.devices_layout.count())): 
            widget = self.devices_layout.itemAt(i).widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()

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
            current_volume = self.device_volumes.get(dev["name"], 100)
            slider.blockSignals(True)
            slider.setValue(current_volume)
            slider.blockSignals(False)
            slider.valueChanged.connect(lambda val, s_name=dev["name"]: self._set_device_volume(s_name, val))
            
            dev_box.addWidget(lbl)
            dev_box.addWidget(slider)
            
            container = QWidget()
            container.setLayout(dev_box)
            self.devices_layout.addWidget(container)

    def _set_device_volume(self, sink_name, value):
        self.device_volumes[sink_name] = value
        try:
            self.driver.set_volume(sink_name, value)
        except Exception as exc:
            self.status_label.setText(f"Failed to set volume: {exc}")

    def manual_sync(self):
        try:
            self.driver.update_hub()
        except Exception as exc:
            self.status_label.setText(f"Sync failed: {exc}")
        finally:
            self.refresh_devices()

    def open_setup_guide(self):
        dialog = SetupWizardDialog(self.driver, self)
        dialog.exec()

def launch_gui():
    app = QApplication(sys.argv)
    window = EarbudHubGUI()
    window.show()

    if window.driver.get_capabilities().can_use_external_virtual_device and not window.driver.has_usable_hub_device():
        QTimer.singleShot(250, window.open_setup_guide)

    sys.exit(app.exec())