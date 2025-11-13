# IoT Healthcare Asset Tracker 🏥

A real-time asset tracking prototype designed for healthcare environments. This system uses **ESP32** microcontrollers to detect the proximity of high-value assets (like wheelchairs) via Wi-Fi RSSI signal strength and visualizes their location on a **Python**-based dashboard.

## 📸 Project Overview

**Problem:** Hospital staff waste significant time searching for mobile equipment, leading to operational delays.
**Solution:** A low-cost, localized tracking system that categorizes asset distance into "zones" (<3m, 3-7m, etc.) using a "Sonar/Archery" style visualization.

## 🛠️ Tech Stack

* **Hardware:** ESP32 (WROOM-32)
* **Firmware:** C++ (Arduino IDE)
* **Backend:** Python (PySerial for UART telemetry)
* **Frontend:** Streamlit, Matplotlib (Custom polar-coordinate visualization)
* **Data Storage:** Local JSON (Lightweight NoSQL)

