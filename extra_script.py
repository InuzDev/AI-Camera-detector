Import("env")

# Add the include directory for esp32-camera
env.Append(CPPPATH=[
    "components/esp32-camera"
])

# Make sure the source files from the component are compiled
env.Append(SRC_FILTER=["+<components/esp32-camera>"])
