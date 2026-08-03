


```markdown
# Open Multi-Earbud Hub 🎧

![Version](https://img.shields.io/github/v/release/Nitin-kumar-yadav1307/open-multi-earbud-hub?color=blue&style=flat-square)
![License](https://img.shields.io/github/license/Nitin-kumar-yadav1307/open-multi-earbud-hub?color=green&style=flat-square)
![Platform](https://img.shields.io/badge/platform-Linux-orange?style=flat-square)

An open-source Linux desktop utility designed for managing multiple Bluetooth audio devices simultaneously. Built with Python and PyQt6.

---

## ✨ Features

* **Multi-Device Management:** Seamlessly discover, pair, and route audio across multiple Bluetooth earbuds or headphones.
* **Modern PyQt6 Interface:** Clean, responsive desktop GUI.
* **Standalone AppImage:** Zero dependencies required—runs on Fedora, Ubuntu, Arch, Debian, and Linux Mint.
* **Background Daemon:** Optional `systemd` user service for automated background monitoring.

---

## 🚀 Quick Start (AppImage)

The easiest way to run **Open Multi-Earbud Hub** is by downloading the standalone AppImage.

1. Download the latest `Open-Multi-Earbud-Hub-x86_64.AppImage` from the [Releases Page](https://github.com/Nitin-kumar-yadav1307/open-multi-earbud-hub/releases/latest).
2. Open your terminal in your download folder and make the file executable:
   ```bash
   chmod +x Open-Multi-Earbud-Hub-x86_64.AppImage

```

3. Launch the application:
```bash
./Open-Multi-Earbud-Hub-x86_64.AppImage

```



*(Alternatively, right-click the downloaded AppImage in your file manager, navigate to **Properties** -> **Permissions**, check **"Allow executing file as program"**, and double-click to run).*

---

## 🛠️ Building from Source

If you want to run or modify the application locally:

### 1. Clone the Repository

```bash
git clone [https://github.com/Nitin-kumar-yadav1307/open-multi-earbud-hub.git](https://github.com/Nitin-kumar-yadav1307/open-multi-earbud-hub.git)
cd open-multi-earbud-hub

```

### 2. Install Dependencies

```bash
pip install -r requirements.txt

```

### 3. Run the Application

```bash
python3 run.py

```

### 4. Build Your Own AppImage

To bundle your local source code into a new AppImage executable:

```bash
./build_appimage.sh

```

---

## 📄 License

Distributed under the MIT License. See `LICENSE` for more information.



---

