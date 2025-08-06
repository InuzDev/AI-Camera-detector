# 🚀 FFI Setup Guide: MicroPython + Edge Impulse C++ Integration

## 📋 What You Need to Start

### 1. **Development Tools**

```bash
# Install ESP-IDF
git clone --recursive https://github.com/espressif/esp-idf.git
cd esp-idf
./install.sh esp32,esp32s3
source ./export.sh

# Clone MicroPython
git clone https://github.com/micropython/micropython.git
cd micropython
git submodule update --init
make -C mpy-cross
```

### 2. **Edge Impulse Model**

- Train your fire detection model on Edge Impulse Studio
- Export as **"Arduino library"** or **"C++ library"**
- Extract the downloaded ZIP file

### 3. **Hardware**

- Seeed XIAO ESP32-S3 Sense (your current board)
- USB-C cable for programming

## 🏗️ Implementation Steps

### Step 1: Prepare Edge Impulse Library

```bash
# Extract your Edge Impulse export to:
mkdir -p micropython-modules/ai_inference/edge_impulse
# Copy the contents of your Edge Impulse export here
```

### Step 2: Update the C++ Implementation

Edit `micropython-modules/ai_inference/ai_inference_impl.cpp`:

```cpp
// Replace the placeholder includes with your actual Edge Impulse headers
#include "edge_impulse/edge-impulse-sdk/classifier/ei_run_classifier.h"
#include "edge_impulse/edge-impulse-sdk/dsp/image/image.hpp"
#include "edge_impulse/model-parameters/model_metadata.h"

// Update the ai_classify_image function with real Edge Impulse code
extern "C" const char* ai_classify_image(uint8_t* image_data, size_t data_len, float* confidence) {
    // Convert image data to Edge Impulse format
    signal_t signal;
    signal.total_length = EI_CLASSIFIER_INPUT_WIDTH * EI_CLASSIFIER_INPUT_HEIGHT;
    signal.get_data = &get_signal_data;
    
    // Run classifier
    ei_impulse_result_t result = { 0 };
    EI_IMPULSE_ERROR res = run_classifier(&signal, &result, false);
    
    if (res != EI_IMPULSE_OK) {
        *confidence = 0.0f;
        strcpy(result_label, "error");
        return result_label;
    }
    
    // Find highest confidence result
    float max_confidence = 0.0f;
    int max_index = 0;
    for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        if (result.classification[ix].value > max_confidence) {
            max_confidence = result.classification[ix].value;
            max_index = ix;
        }
    }
    
    *confidence = max_confidence;
    strcpy(result_label, result.classification[max_index].label);
    return result_label;
}
```

### Step 3: Build Custom Firmware

```bash
# Make the build script executable
chmod +x build_firmware.py

# Run the build
python3 build_firmware.py
```

### Step 4: Flash the Firmware

```bash
# Flash the custom firmware
esptool.py --chip esp32s3 --port /dev/ttyUSB0 write_flash -z 0x0 micropython/ports/esp32/build-GENERIC_S3/firmware.bin

# Upload your Python files
ampy --port /dev/ttyUSB0 put boot.py
ampy --port /dev/ttyUSB0 put env.py
ampy --port /dev/ttyUSB0 put main_with_ai.py main.py
```

## 🔧 Configuration Options

### Memory Optimization

In `micropython.mk`, adjust these flags:

```makefile
# Reduce memory usage
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_ALLOCATION_STATIC=1
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_SLICES_PER_MODEL_WINDOW=1

# Enable ESP32 optimizations
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_TFLITE_ENABLE_ESP_NN=1
```

### AI Analysis Settings

In `main_with_ai.py`:

```python
# Adjust these based on your needs
AI_CONFIDENCE_THRESHOLD = 0.7  # Minimum confidence for fire detection
ai_analysis_interval = 10       # Analyze every Nth frame (saves CPU)
FIRE_DETECTION_ENABLED = True   # Enable/disable AI analysis
```

## 🚨 Troubleshooting

### Build Errors

- **"No module named 'ai_inference'"**: Firmware not built with custom module
- **Memory allocation errors**: Reduce model size or increase heap
- **Compilation errors**: Check Edge Impulse library paths in `micropython.mk`

### Runtime Issues

- **AI initialization fails**: Check model files are included in build
- **Low confidence scores**: Retrain model with more diverse data
- **Performance issues**: Increase `ai_analysis_interval`

## 📊 Expected Performance

### Memory Usage

- **Base MicroPython**: ~200KB
- **Camera module**: ~100KB
- **AI inference**: ~300-500KB (depends on model)
- **Available for buffers**: ~1.5MB

### Processing Speed

- **Camera capture**: ~30 FPS
- **AI inference**: ~1-5 FPS (depending on model complexity)
- **Combined throughput**: ~10-15 FPS with AI analysis

## 🎯 Next Steps

1. **Train your Edge Impulse model** with fire/no-fire images
2. **Export the C++ library** from Edge Impulse Studio
3. **Follow this guide** to integrate it with your camera system
4. **Test and optimize** the performance for your specific use case

## 💡 Pro Tips

- Start with a simple model and gradually increase complexity
- Use quantized models for better performance on ESP32
- Monitor memory usage with `gc.mem_free()`
- Consider using dual-core processing (one core for camera, one for AI)

---

**Ready to start?** Begin with Step 1 and work through each section systematically. The FFI approach will give you the best performance for real-time fire detection!
