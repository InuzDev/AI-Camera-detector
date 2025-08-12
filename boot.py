
# The MIT License (MIT)
#
# Copyright (c) Sharil Tumin
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#-----------------------------------------------------------------------------

# Import required modules
from time import sleep  # Used for delays during connection attempts
import env              # Loads WiFi credentials from env.py
import network          # MicroPython network module for WiFi control

class Sta:
    """
    Sta (Station) class manages WiFi connection in station mode.
    It uses credentials from env.py by default, but can accept custom ones.
    Provides methods to connect, check status, wait for connection, and scan networks.
    """
    AP = env.WIFI_SSID  # Default WiFi SSID from env.py
    PWD = env.WIFI_PASS  # Default WiFi password from env.py

    def __init__(my, ap='', pwd=''):
        """
        Initialize the WiFi station interface.
        Disables AP mode, enables STA mode, and sets credentials.
        Args:
            ap (str): WiFi SSID (optional, uses default if empty)
            pwd (str): WiFi password (optional, uses default if empty)
        """
        network.WLAN(network.AP_IF).active(False)  # Disable access point mode
        my.wlan = network.WLAN(network.STA_IF)     # Create station interface
        my.wlan.active(True)                       # Enable station mode
        if ap == '':
            my.ap = Sta.AP
            my.pwd = Sta.PWD
        else:
            my.ap = ap
            my.pwd = pwd

    def connect(my, ap='', pwd=''):
        """
        Attempt to connect to the WiFi network using stored or provided credentials.
        Handles errors and retries if initial connection fails.
        Args:
            ap (str): WiFi SSID (optional)
            pwd (str): WiFi password (optional)
        Returns:
            bool: True if connection attempt was made, False if failed
        """
        if ap != '':
            my.ap = ap
            my.pwd = pwd

        if not my.wlan.isconnected():
            try:
                # Ensure WiFi is properly disconnected first
                my.wlan.disconnect()
                sleep(1)
                # Reconnect with credentials
                my.wlan.connect(my.ap, my.pwd)
            except OSError as e:
                print("WiFi connect error: " + str(e))
                # Try to reset WiFi module
                my.wlan.active(False)
                sleep(2)
                my.wlan.active(True)
                sleep(1)
                # Retry connection
                try:
                    my.wlan.connect(my.ap, my.pwd)
                except OSError as e2:
                    print("WiFi retry failed:", e2)
                    return False
        return True

    def status(my):
        """
        Get current WiFi connection status and network configuration.
        Returns:
            tuple: Network config if connected, empty tuple otherwise
        """
        if my.wlan.isconnected():
            return my.wlan.ifconfig()
        else:
            return ()

    def wait(my):
        """
        Wait for WiFi connection to be established, retrying if needed.
        Returns:
            bool: True if connected, False if timeout or failure
        """
        cnt = 30  # Timeout counter (seconds)
        connect_result = my.connect()  # Actually initiate the connection

        if not connect_result:
            print("Initial connection failed!")
            return False

        while cnt > 0:
            print("Waiting for connection... (%ds remaining)" % cnt)
            if my.wlan.isconnected():
                print("Connected to %s" % my.ap)
                print('network config:', my.wlan.ifconfig())
                return True
            else:
                sleep(1)
                cnt -= 1

                # Try reconnecting every 10 seconds if still failing
                if cnt % 10 == 0 and cnt > 0:
                    print("Retrying connection...")
                    my.connect()

        print("Connection timeout!")
        return False

    def scan(my):
        """
        Scan for available WiFi access points.
        Returns:
            list: List of tuples with AP info
        """
        return my.wlan.scan()   # Scan for available access points

# --- WiFi Initialization on Boot ---
print("Initializing WiFi connection...")
wifi_connected = False  # Tracks if WiFi was successfully connected

try:
    # Create Sta object and attempt to connect to WiFi
    wifi = Sta()
    wifi_connected = wifi.wait()

    if wifi_connected:
        print("Boot: WiFi connection successful!")
    else:
        print("Boot: WiFi connection failed!")

except Exception as e:
    # Catch any unexpected errors during WiFi setup
    print("Boot: WiFi initialization error:", e)
    print("Boot: Continuing without WiFi...")

# Make wifi object available globally for main.py
# If initialization failed, wifi will be None
if 'wifi' not in locals():
    wifi = None
