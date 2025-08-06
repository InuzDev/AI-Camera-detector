# Enhanced main.py with AI inference capability
# This will replace your current main.py once the C++ module is built

import esp
import network
import socket as soc
import camera
from time import sleep
import gc

# Import our custom AI inference module (will be available after building firmware)
try:
    import ai_inference
    AI_AVAILABLE = True
    print("✅ AI inference module loaded successfully")
except ImportError:
    AI_AVAILABLE = False
    print("⚠️ AI inference module not available - running without AI")

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

# AI inference settings
AI_CONFIDENCE_THRESHOLD = 0.7
FIRE_DETECTION_ENABLED = True

def initialize_ai():
    """Initialize the AI inference engine"""
    if not AI_AVAILABLE:
        return False
    
    try:
        print("🤖 Initializing AI model...")
        result = ai_inference.init()
        if result:
            model_info = ai_inference.get_info()
            print("✅ AI model initialized: " + str(model_info))
            return True
        else:
            print("❌ AI model initialization failed")
            return False
    except Exception as e:
        print("❌ AI initialization error: " + str(e))
        return False

def analyze_frame(frame_data):
    """Analyze a camera frame for fire detection"""
    if not AI_AVAILABLE or not FIRE_DETECTION_ENABLED:
        return None, 0.0
    
    try:
        # Run AI inference on the frame
        label, confidence = ai_inference.classify(frame_data)
        return label, confidence
    except Exception as e:
        print("AI analysis error: " + str(e))
        return None, 0.0

def handle_fire_detection(label, confidence):
    """Handle fire detection event"""
    if label == "fire_detected" and confidence >= AI_CONFIDENCE_THRESHOLD:
        print("🔥 FIRE DETECTED! Confidence: " + str(confidence))
        # Here you could:
        # - Send alert to external system
        # - Trigger alarm
        # - Save image
        # - Send notification
        return True
    return False

# Check if WiFi is already connected from boot.py
wlan = network.WLAN(network.STA_IF)
if not wlan.isconnected():
    print("WiFi not connected! Check boot.py configuration.")
    wlan = None
else:
    print("Using existing WiFi connection: " + str(wlan.ifconfig()))

# Initialize camera with error handling and retry
cam_ready = False
for i in range(3):
    try:
        gc.collect()
        print("Attempting to initialize camera (attempt " + str(i + 1) + ")...")
        try:
            camera.deinit()
        except Exception as e:
            print("Camera deinit failed (this is often ok): " + str(e))
        
        sleep(1)
        cam_ready = camera.init()
        if cam_ready:
            print("Camera ready?: True")
            sleep(1)
            break
        else:
            print("Camera init returned False.")
            sleep(1)
    except Exception as e:
        print("Error initializing camera: " + str(e))
        sleep(2)

if not cam_ready:
    print("Camera initialization failed after multiple attempts.")

# Initialize AI
ai_ready = initialize_ai()

if wlan and cam_ready:
    camera.framesize(9)  # Resolution
    camera.quality(2)    # Quality
    camera.contrast(2)   # Contrast

    port = 80
    addr = soc.getaddrinfo('0.0.0.0', port)[0][-1]
    s = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
    s.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
    s.bind(addr)
    s.listen(1)

    ip_address = wlan.ifconfig()[0]
    print("Streaming ready at http://" + ip_address + "/david/Dev")
    if ai_ready:
        print("🤖 AI fire detection: ENABLED")
    else:
        print("⚠️ AI fire detection: DISABLED")

    frame_count = 0
    ai_analysis_interval = 10  # Analyze every 10th frame to save processing power

    while True:
        gc.collect()
        cs, ca = s.accept()
        print('Request from: ' + str(ca))
        
        try:
            # Receive HTTP request
            w = cs.recv(512)
            if not w:
                print("Empty request received")
                cs.close()
                continue
                
            request_str = w.decode('utf-8', 'ignore')
            lines = request_str.split('\r\n')
            request_line = lines[0] if lines else ""
            
            print("Request line: " + str(request_line))
            
            # Validate HTTP request format
            if not request_line or not request_line.startswith(('GET', 'POST', 'HEAD')):
                print("Invalid HTTP method or empty request")
                cs.close()
                continue
            
            parts = request_line.split()
            if len(parts) < 2:
                print("Malformed HTTP request - insufficient parts")
                cs.close()
                continue
            
            path = parts[1]
            segments = path.strip('/').split('/')
            uid = segments[0] if len(segments) > 0 else ''
            pwd = segments[1] if len(segments) > 1 else ''
            
            if not (uid == UID and pwd == PWD):
                print("Authentication failed for path: " + str(path))
                cs.close()
                continue
                
            # Send HTTP headers
            stream_header = hdr['stream'].encode() + b'\r\n\r\n'
            cs.write(stream_header)
            
            pic = camera.capture
            put = cs.write
            frame_header = hdr['frame'].encode() + b'\r\n\r\n'
            
            # Camera streaming loop with AI analysis
            max_empty_frames = 5
            empty_frame_count = 0
            
            while True:
                gc.collect()
                try:
                    frame = pic()
                    if not frame:
                        empty_frame_count += 1
                        print("Empty frame captured! (" + str(empty_frame_count) + "/" + str(max_empty_frames) + ")")
                        
                        if empty_frame_count >= max_empty_frames:
                            print("Too many empty frames, restarting camera...")
                            camera.deinit()
                            sleep(0.1)
                            camera.init()
                            camera.framesize(9)
                            camera.quality(2)
                            camera.contrast(2)
                            pic = camera.capture
                            empty_frame_count = 0
                            continue
                        
                        sleep(0.05)
                        continue
                    
                    # Reset empty frame counter
                    empty_frame_count = 0
                    frame_count += 1
                    
                    # AI Analysis (every Nth frame to save processing power)
                    if ai_ready and (frame_count % ai_analysis_interval == 0):
                        label, confidence = analyze_frame(frame)
                        if label:
                            fire_detected = handle_fire_detection(label, confidence)
                            if fire_detected:
                                print("🚨 FIRE ALERT - Frame: " + str(frame_count))
                    
                    # Send frame to client
                    put(frame_header)
                    put(frame)
                    put(b'\r\n')
                    
                    sleep(0.03)  # Frame rate control
                    
                except Exception as e:
                    print("TCP send error: " + str(e))
                    break
            
            cs.close()
            
        except MemoryError as e:
            print("MemoryError: " + str(e))
            gc.collect()
            cs.close()
            continue
        except (OSError, Exception) as e:
            print("Error processing request: " + str(e))
            cs.close()
            continue

else:
    if not wlan:
        print("Wi-Fi not connected.")
    if not cam_ready:
        print("Camera not ready.")
    print("System not ready. Please restart.")