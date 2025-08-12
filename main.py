# The MIT License (MIT)
# Copyright (c) Sharil Tumin
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-----------------------------------------------------------------------------

"""
main.py - ESP32 Camera Streaming and WiFi Control

This script runs on the ESP32 camera module. It:
- Connects to WiFi using hardcoded credentials (edit as needed)
- Initializes the camera
- Starts an HTTP MJPEG streaming server with basic authentication
- Streams camera frames to any client that authenticates
- Handles connection errors and camera readiness

Sections are fully documented for clarity and maintainability.
"""

import env              # Loads environment variables (not used in this script, but imported for consistency)
import esp              # ESP32-specific functions
import network          # MicroPython network module for WiFi
import socket as soc    # MicroPython socket module
import camera           # ESP32 camera module
from time import sleep  # Used for connection delays

esp.osdebug(None)  # Disable debug logs for cleaner output

# Camera authentication credentials (change as needed)
UID = 'david'
PWD = 'Dev'

# HTTP headers for MJPEG streaming
hdr = {
    'stream': """HTTP/1.1 200 OK
Content-Type: multipart/x-mixed-replace; boundary=kaki5
Connection: keep-alive
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Expires: Thu, Jan 01 1970 00:00:00 GMT
Pragma: no-cache""",
    'frame': """--kaki5
Content-Type: image/jpeg"""
}

# --- WiFi Connection Logic ---
def connect_wifi(ssid, password):
    """
    Connect to a WiFi network using the given SSID and password.
    Retries connection for up to 10 attempts (20 seconds total).
    Args:
        ssid (str): WiFi network name
        password (str): WiFi password
    Returns:
        WLAN object if connected, None otherwise
    """
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.disconnect()
    wlan.connect(ssid, password)

    for _ in range(10):
        if wlan.isconnected():
            print("Wi-Fi connected:", wlan.ifconfig())
            return wlan
        print("Connecting to Wi-Fi...")
        sleep(2)
    print("Wi-Fi connection failed.")
    return None

# Wi-Fi credentials (edit as needed)
SSID = "Vasquez Gonzalez Google"
PASSWORD = "Bendecidos"

# --- Main Startup Sequence ---

# Connect to WiFi
wlan = connect_wifi(SSID, PASSWORD)
# Initialize camera
cam_ready = camera.init()
print("Camera ready?:", cam_ready)

if wlan and cam_ready:
    # Configure camera settings
    camera.framesize(11)  # Set resolution (higher = more detail)
    camera.quality(11)    # Set JPEG quality (higher = better, but more heat)
    camera.contrast(9)    # Set image contrast

    # Set up HTTP server for MJPEG streaming
    port = 80
    addr = soc.getaddrinfo('0.0.0.0', port)[0][-1]
    s = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
    s.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    print("Streaming ready at http://{}/david/Dev".format(wlan.ifconfig()[0]))

    while True:
        cs, ca = s.accept()
        print('Request from:', ca)
        
        try:
            # Read HTTP request
            w = cs.recv(200)
            request_line = w.decode().split('\r\n')[0]
            print("Request line:", request_line)
            
            # Parse HTTP request path and extract credentials
            parts = request_line.split()
            if len(parts) < 2:
                raise ValueError("Invalid HTTP request")
            
            path = parts[1]
            segments = path.strip('/').split('/')
            uid = segments[0] if len(segments) > 0 else ''
            pwd = segments[1] if len(segments) > 1 else ''
            
            # Basic authentication check
            if not (uid == UID and pwd == PWD):
                print("Authentication failed")
                cs.close()
                continue
            # Send MJPEG stream headers
            cs.write(b'%s\r\n\r\n' % hdr['stream'].encode())
            pic = camera.capture
            put = cs.write
            hr = hdr['frame'].encode()
            
            # Stream camera frames in a loop
            while True:
                try:
                    frame = pic()
                    if not frame:
                        print("Empty frame captured!")
                        break
                    put(b'%s\r\n\r\n' % hr)
                    put(frame)
                    put(b'\r\n')
                except Exception as e:
                    print("TCP send error:", e)
                    break
            
            cs.close()
            
        except Exception as e:
            print("Bad request format:", e)
            cs.close()
            break

else:
    # Error handling for WiFi or camera failure
    if not wlan:
        print("Wi-Fi not connected.")
    if not cam_ready:
        print("Camera not ready.")
    print("System not ready. Please restart.")
