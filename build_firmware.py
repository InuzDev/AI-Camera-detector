#!/usr/bin/env python3
"""
Build script for MicroPython firmware with AI inference module
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Configuration
MICROPYTHON_PATH = "micropython"  # Path to MicroPython source
ESP_IDF_PATH = os.environ.get("IDF_PATH", "esp-idf")
PROJECT_ROOT = Path(__file__).parent
MODULE_PATH = PROJECT_ROOT / "micropython-modules"

def check_prerequisites():
    """Check if all required tools are available"""
    print("🔍 Checking prerequisites...")
    
    # Check ESP-IDF
    if not Path(ESP_IDF_PATH).exists():
        print("❌ ESP-IDF not found. Please install ESP-IDF first.")
        return False
    
    # Check MicroPython source
    if not Path(MICROPYTHON_PATH).exists():
        print("❌ MicroPython source not found. Please clone MicroPython repository.")
        return False
    
    print("✅ Prerequisites check passed")
    return True

def setup_build_environment():
    """Setup the build environment"""
    print("🔧 Setting up build environment...")
    
    # Set environment variables
    os.environ["IDF_PATH"] = ESP_IDF_PATH
    os.environ["ESPIDF"] = ESP_IDF_PATH
    
    # Copy user modules to MicroPython
    micropython_modules_dir = Path(MICROPYTHON_PATH) / "ports" / "esp32" / "modules"
    if MODULE_PATH.exists():
        print(f"📁 Copying modules from {MODULE_PATH} to {micropython_modules_dir}")
        # You would copy your modules here
    
    print("✅ Build environment setup complete")

def build_firmware():
    """Build the MicroPython firmware with custom modules"""
    print("🔨 Building MicroPython firmware...")
    
    # Change to MicroPython ESP32 port directory
    esp32_port_dir = Path(MICROPYTHON_PATH) / "ports" / "esp32"
    os.chdir(esp32_port_dir)
    
    # Build commands
    commands = [
        ["make", "clean"],
        ["make", "submodules"],
        ["make", f"USER_C_MODULES={MODULE_PATH}", "BOARD=GENERIC_S3"]
    ]
    
    for cmd in commands:
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {' '.join(cmd)}")
            print(f"Error: {result.stderr}")
            return False
    
    print("✅ Firmware build complete")
    return True

def main():
    """Main build function"""
    print("🚀 Starting MicroPython + AI Inference build process")
    
    if not check_prerequisites():
        sys.exit(1)
    
    setup_build_environment()
    
    if not build_firmware():
        print("❌ Build failed")
        sys.exit(1)
    
    print("🎉 Build completed successfully!")
    print("📁 Firmware binary location: micropython/ports/esp32/build-GENERIC_S3/firmware.bin")
    print("💡 Flash with: esptool.py --chip esp32s3 --port /dev/ttyUSB0 write_flash -z 0x0 firmware.bin")

if __name__ == "__main__":
    main()