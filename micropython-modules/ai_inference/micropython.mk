# MicroPython module makefile for ai_inference

AI_INFERENCE_MOD_DIR := $(USERMOD_DIR)

# Add source files
SRC_USERMOD += $(AI_INFERENCE_MOD_DIR)/ai_inference.c
SRC_USERMOD_CXX += $(AI_INFERENCE_MOD_DIR)/ai_inference_impl.cpp

# Add include directories
CFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)

# Add Edge Impulse library paths (update these paths based on your Edge Impulse export)
CFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/third_party/ruy
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/third_party/gemmlowp
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/third_party/flatbuffers/include
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/tensorflow
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/dsp
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/classifier
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/edge-impulse-sdk/anomaly
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/tflite-model
CXXFLAGS_USERMOD += -I$(AI_INFERENCE_MOD_DIR)/edge_impulse/model-parameters

# Compiler flags for Edge Impulse
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_TFLITE_ENABLE_ESP_NN=1
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_TFLITE_ENABLE_CMSIS_NN=0
CXXFLAGS_USERMOD += -DEIDSP_QUANTIZE_FILTERBANK=0
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_SLICES_PER_MODEL_WINDOW=3
CXXFLAGS_USERMOD += -DEI_CLASSIFIER_ALLOCATION_STATIC=1
CXXFLAGS_USERMOD += -DEIDSP_USE_CMSIS_DSP=0
CXXFLAGS_USERMOD += -DEIDSP_LOAD_CMSIS_DSP_SOURCES=0

# Optimization flags
CXXFLAGS_USERMOD += -O2 -fno-exceptions -fno-rtti