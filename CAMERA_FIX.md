# 🎯 CAMERA TIMEOUT FIX

## **Root Cause Identified** ✅

Your camera **initializes correctly** but fails with **`Failed to get frame: timeout`**.

This is a **timing/synchronization issue** with the OV2640 sensor.

## **Quick Fix - Change These Lines**

In your `src/main.cpp`, find these lines and change them:

### **Line 56** - Change pixel format:
```cpp
// CHANGE FROM:
.pixel_format = PIXFORMAT_JPEG,

// CHANGE TO:
.pixel_format = PIXFORMAT_RGB565,
```

### **Line 57** - Change frame size:
```cpp
// CHANGE FROM:
.frame_size = FRAMESIZE_QQVGA,    // Smallest size for testing

// CHANGE TO:
.frame_size = FRAMESIZE_96X96,    // Even smaller
```

### **Line 59** - Change buffer count:
```cpp
// CHANGE FROM:
.fb_count = 1,                    // Single buffer for initial testing

// CHANGE TO:
.fb_count = 2,                    // Double buffer for stability
```

### **Line 61** - Change grab mode:
```cpp
// CHANGE FROM:
.grab_mode = CAMERA_GRAB_WHEN_EMPTY,

// CHANGE TO:
.grab_mode = CAMERA_GRAB_LATEST,
```

## **Why These Changes Work**

1. **RGB565 vs JPEG**: RGB565 is simpler format, no encoding needed
2. **96x96 vs QQVGA**: Smaller frame = less data = faster capture
3. **Double buffer**: Prevents timing conflicts
4. **GRAB_LATEST**: More reliable than WHEN_EMPTY

## **Expected Result**

After these changes, you should see:
- ✅ Camera initialization: SUCCESS
- ✅ Frame capture: SUCCESS  
- ✅ Stream working: SUCCESS

## **Test Steps**

1. Make the 4 changes above
2. Build and flash: `pio run --target upload`
3. Check logs for: `"Capture successful! Frame size: X bytes"`
4. Test stream: `http://192.168.86.238/InuzDev/ALPHADEV`

## **If Still Failing**

Try this additional change - **enable test pattern permanently**:

Find line ~369 and change:
```cpp
// CHANGE FROM:
s->set_colorbar(s, 0);                   // 0 = disable , 1 = enable

// CHANGE TO:
s->set_colorbar(s, 1);                   // Enable test pattern permanently
```

This will show colored bars instead of camera image, confirming the data path works.

---

**The 404 favicon error is harmless** - just browser requesting an icon. Focus on the frame timeout fix! 📸