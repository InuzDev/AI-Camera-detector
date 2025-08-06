
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

#Basic WiFi configuration:



from time import sleep
import env
import network

class Sta:

   AP = env.WIFI_SSID  # change to your SSID
   PWD = env.WIFI_PASS  # change to your password

   def __init__(my, ap='', pwd=''):
      network.WLAN(network.AP_IF).active(False) # disable access point
      my.wlan = network.WLAN(network.STA_IF)
      my.wlan.active(True)
      if ap == '':
        my.ap = Sta.AP
        my.pwd = Sta.PWD 
      else:
        my.ap = ap
        my.pwd = pwd

   def connect(my, ap='', pwd=''):
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
      if my.wlan.isconnected():
        return my.wlan.ifconfig()
      else:
        return ()

   def wait(my):
      cnt = 30
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
      return my.wlan.scan()   # Scan for available access points

# Initialize WiFi connection on boot with error handling
print("Initializing WiFi connection...")
wifi_connected = False

try:
    wifi = Sta()
    wifi_connected = wifi.wait()
    
    if wifi_connected:
        print("Boot: WiFi connection successful!")
    else:
        print("Boot: WiFi connection failed!")
        
except Exception as e:
    print("Boot: WiFi initialization error:", e)
    print("Boot: Continuing without WiFi...")
    
# Make wifi object available globally for main.py
if 'wifi' not in locals():
    wifi = None
