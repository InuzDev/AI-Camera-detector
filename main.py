
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

# run this on ESP32 Camera

import esp
import network
import socket as soc
import camera
from time import sleep

esp.osdebug(None)  # Disable debug logs

# Camera authentication
UID = 'david'
PWD = 'Dev'

# Camera headers for MJPEG streaming
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

# Init Wi-Fi connection
def connect_wifi(ssid, password):
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

# Wi-Fi credentials
SSID = 'ATLAS 2.4G'
PASSWORD = 'Charlie7445'

# Start
wlan = connect_wifi(SSID, PASSWORD)
cam_ready = camera.init()
print("Camera ready?:", cam_ready)

if wlan and cam_ready:
    camera.framesize(11)
    camera.quality(5)
    camera.contrast(2)

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
            w = cs.recv(200)
            request_line = w.decode().split('\r\n')[0]
            print("Request line:", request_line)
            
            parts = request_line.split()
            if len(parts) < 2:
                raise ValueError("Invalid HTTP request")
            
            path = parts[1]
            segments = path.strip('/').split('/')
            uid = segments[0] if len(segments) > 0 else ''
            pwd = segments[1] if len(segments) > 1 else ''
            
            if not (uid == UID and pwd == PWD):
                print("Authentication failed")
                cs.close()
                continue
            cs.write(b'%s\r\n\r\n' % hdr['stream'].encode())
            pic = camera.capture
            put = cs.write
            hr = hdr['frame'].encode()
            
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
    if not wlan:
        print("Wi-Fi not connected.")
    if not cam_ready:
        print("Camera not ready.")
    print("System not ready. Please restart.")
