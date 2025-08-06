# Camera Troubleshooting Guide

## Current Status ✅
- **Camera initializes successfully** - Great progress!
- **WiFi connects properly**
- **HTTP server starts**
- **Issue**: Camera capture fails (`esp_camera_fb_get()` returns NULL)

## Favicon Issue ❌
The `/favicon.ico` requests are **NOT** the problem. This is normal browser behavior.

## Next Steps to Fix Camera Capture

### 1. **Test Different Pixel Formats**
Try changing in main.cpp:
```cpp
.pixel_format = PIXFORMAT_RGB565,  // Instead of PIXFORMAT_JPEG
```

### 2. **Test Different Frame Sizes**
```cpp
.frame_size = FRAMESIZE_96X96,     // Even smaller than QQVGA
```

### 3. **Enable Test Pattern**
The camera sensor supports a test pattern. If this works, it confirms the hardware is OK:
```cpp
// In your sensor configuration section, try:
s->set_colorbar(s, 1);  // Enable test pattern
```

### 4. **Check Power Supply**
Camera modules need stable power. The OV2640 requires:
- **3.3V supply**
- **Sufficient current** (can be 100-200mA during operation)

### 5. **Verify Pin Connections**
Double-check these critical pins on your Seeed XIAO ESP32S3:
- **XCLK (Pin 10)** - Clock signal
- **PCLK (Pin 2)** - Pixel clock  
- **VSYNC (Pin 42)** - Vertical sync
- **HREF (Pin 41)** - Horizontal reference
- **SDA (Pin 40)** - I2C data
- **SCL (Pin 39)** - I2C clock

## Quick Test URLs

Once your camera is working, test these URLs:
- **Stream**: `http://YOUR_IP/InuzDev/ALPHADEV`
- **Single capture**: `http://YOUR_IP/test` (if we add this endpoint)

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Camera init OK, capture fails | Try different pixel formats |
| All captures return NULL | Check power supply |
| Intermittent failures | Reduce XCLK frequency |
| Hardware suspected | Enable test pattern |

## Debug Commands

Add these to your code for more diagnostics:
```cpp
ESP_LOGI(TAG, "Free heap: %d bytes", esp_get_free_heap_size());
ESP_LOGI(TAG, "Camera status: %s", esp_camera_sensor_get() ? "OK" : "FAIL");
```