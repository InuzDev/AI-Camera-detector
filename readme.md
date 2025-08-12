# Firevolt AI Camera Detector

## Project Overview

Firevolt is an AI-powered camera system designed to detect fires and communicate alerts to users or other robots (e.g., a firefighting robot). The project is built for learning about camera systems, AI-based detection, and networked robotics. It is designed for extensibility and integration with other hardware, such as ESP32S3 microcontrollers.

---

## Features

- **AI-based Fire Detection:** Uses a camera and AI model to detect fire in real-time.
- **Network Communication:** Sends alerts to users or other robots when fire is detected.
- **Configurable Networking:** Supports WiFi configuration via environment variables and .env files.
- **Modular Python Codebase:** Designed for easy integration and extension.
- **Edge Impulse Integration (Incoming):** Planned FFI (Foreign Function Interface) to integrate Edge Impulse models directly into the Python logic for optimized inference.
- **Closed Network Support (Incoming):** ESP32S3 will generate its own WiFi network, enabling direct robot-to-robot communication without external infrastructure.

---

## WiFi Initialization and boot.py Logic

The `boot.py` script is responsible for initializing the WiFi connection on device boot. It uses credentials from `env.py` (which loads from your `.env` file) and manages connection attempts, retries, and error handling. The main logic is encapsulated in the `Sta` class:

- **Sta Class:**
  - Manages WiFi in station mode (STA).
  - Disables access point mode to ensure the device connects to an existing network.
  - Reads SSID and password from `env.py` or accepts custom credentials.
  - Provides methods to connect, check status, wait for connection (with retries), and scan for available networks.
  - On boot, attempts to connect and prints status. If connection fails, it retries and handles errors gracefully.
  - The `wifi` object is made globally available for use in `main.py` and other modules.

**Typical Workflow:**

1. On boot, `Sta` is instantiated and attempts to connect to WiFi.
2. If connection fails, it retries and prints error messages.
3. If successful, network configuration is printed and the system continues.
4. If all attempts fail, the system continues without WiFi, but the `wifi` object is set to `None`.

---

## Server Directory and AI Server Integration

The `Server/` directory contains the AI server code that processes images or data sent from the camera (ESP32S3 or other device). This server can run on a PC, Raspberry Pi, or other host, and is responsible for:

- Receiving image data or alerts from the camera.
- Running AI inference (e.g., fire detection) on received data.
- Sending responses or alerts to clients (robots, user interfaces, etc.).

### Enabling and Connecting the AI Server to the Camera

**1. Start the AI Server:**

- Navigate to the `Server/` directory and run the server script (e.g., `python server.py`).
- Ensure all dependencies are installed (see `Server/requirements.txt` if available).

**2. Configure the Camera (ESP32S3):**

- Ensure the camera is flashed with the correct firmware and has network access (see WiFi setup above).
- In your `.env` file, set the WiFi SSID and password to match the network the server is connected to.
- If using closed network mode, configure the ESP32S3 as an access point and connect the server device to its WiFi.

**3. Connect the Camera to the Server:**

- The camera (via `main.py` or other logic) should send image data or alerts to the server's IP address and port.
- The server will process incoming data and respond as needed.
- Ensure firewall rules allow communication between devices on the network.

**Example Communication Flow:**

- Camera detects fire event → sends image/data to server → server runs AI inference → server sends alert/response to user or robot.

**Troubleshooting:**

- Ensure both devices are on the same network (SSID).
- Check IP addresses and port numbers in your configuration.
- Monitor server logs for incoming connections and errors.

---

## Theoretical Application Schema

```txt
+-------------------+         WiFi/Closed Network        +-------------------+
|   Firevolt Cam    |  <------------------------------>  |  Firefighting Bot |
| (ESP32S3 + AI)    |   (Alert, Location, Status)        | (Optional Camera) |
+-------------------+                                    +-------------------+
        |                                                      |
        |                                                      |
        +-------------------+         User Notification        |
                            | <---------------------------->   |
                            |          (App/Console)           |
                            +----------------------------------+
```

- **ESP32S3**: Hosts the camera, runs the AI model, and manages the closed WiFi network.
- **FFI/Edge Impulse**: Python code will call optimized C/C++ Edge Impulse models for efficient inference.
- **Communication**: Alerts and data are sent to other robots or user interfaces over the closed network.

---

## Incoming Changes

### 1. FFI (Foreign Function Interface) for Edge Impulse

- Integrate Edge Impulse models using FFI for high-performance inference in Python.
- Maintain or improve code optimization.
- Allow seamless updates to AI models without major code changes.

### 2. Closed Network (ESP32S3 as Access Point)

- ESP32S3 will generate its own WiFi network (Access Point mode).
- Enables direct communication with other robots (e.g., a firefighting robot) without relying on external WiFi infrastructure.
- Configuration and connection details will be handled in the Python logic and .env files.

---

## Environment Variables

Create a `.env` file in the project root with the following template:

> Do not use quotes ("") or else the output will be buggy and you will have to modify yourself.

```env
WIFI_SSID=<Your WiFi SSID>
WIFI_PASS=<Your WiFi Password>
```

Use the `loadEnv.py` script to load these variables into your environment:

```sh
python loadEnv.py
```

---

## Development Setup & Build Instructions

### 1. Clone the Repository

```sh
git clone <repo-url>
cd AI-Camera-detector
```

### 2. Python Virtual Environment Setup

#### Windows 10/11

- **CMD:**

  ```cmd
  python -m venv tf-env
  tf-env\Scripts\activate.bat
  pip install -r requirements.txt
  ```

- **PowerShell:**

  ```powershell
  python -m venv tf-env
  .\tf-env\Scripts\Activate.ps1
  pip install -r requirements.txt
  ```

  > If you get execution policy errors, run:
  > `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Git Bash/WSL:**

  ```bash
  python -m venv tf-env
  source tf-env/Scripts/activate
  pip install -r requirements.txt
  ```

#### macOS / Linux / Unix

```bash
python3 -m venv tf-env
source tf-env/bin/activate
pip install -r requirements.txt
```

- To deactivate the virtual environment:

  ```sh
  deactivate
  ```

### 3. Environment Variables

- Create a `.env` file as described above.
- Run the environment loader:

  ```sh
  python loadEnv.py
  ```

### 4. Building & Running the Application

- **Standard Run:**

  ```sh
  python main.py
  ```

- **With Edge Impulse FFI (after integration):**
  - Ensure Edge Impulse libraries are built and available (see Edge Impulse documentation for your OS).
  - Update the FFI configuration in the code as needed.
  - Run as above.

### 5. ESP32S3 Firmware (for Closed Network)

- Flash the ESP32S3 with the provided firmware (see `firmware/` directory or documentation).
- Configure the ESP32S3 to run in Access Point mode.
- Connect your development machine or other robots to the ESP32S3 WiFi network.

---

## Testing the Application

1. **Unit Tests:**
   - Run Python unit tests (if available):

     ```sh
     python -m unittest discover tests/
     ```

2. **Integration Test:**
   - Start the application and verify it connects to the WiFi network.
   - Simulate a fire event (use test images or a lighter in a safe environment) and check for detection and alert transmission.
   - If another robot is available, verify it receives the alert and responds appropriately.
3. **Edge Impulse FFI Test (after integration):**
   - Run inference using the Edge Impulse model and verify results.
   - Check for performance improvements and correct operation.
4. **Closed Network Test:**
   - Ensure the ESP32S3 creates a WiFi network.
   - Connect a client device and verify communication between devices.

---

## Contribution & Further Development

- Contributions are welcome! Please fork the repository and submit pull requests.
- For major changes, open an issue first to discuss your ideas.
- See the roadmap for planned features and improvements.

---

## Troubleshooting

- **Virtual Environment Issues:**
  - Ensure you are using the correct activation command for your OS and shell.
  - If you encounter permission issues on Windows PowerShell, set the execution policy as described above.
- **WiFi/Network Issues:**
  - Double-check your `.env` file for correct SSID and password.
  - Ensure the ESP32S3 is properly flashed and configured.
- **FFI/Edge Impulse Issues:**
  - Ensure all required libraries are built and available in your environment.
  - Consult the Edge Impulse documentation for platform-specific build instructions.

---

## License

This project is for educational purposes. See LICENSE for details.
