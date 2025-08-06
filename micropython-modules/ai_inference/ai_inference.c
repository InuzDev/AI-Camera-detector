/*
 * MicroPython C Extension for Edge Impulse AI Inference
 * This module provides Python bindings for Edge Impulse C++ library
 */

#include "py/runtime.h"
#include "py/obj.h"
#include "py/objarray.h"
#include "ai_inference.h"

// Forward declarations
STATIC mp_obj_t ai_inference_init(void);
STATIC mp_obj_t ai_inference_classify(mp_obj_t image_data);
STATIC mp_obj_t ai_inference_get_info(void);

// Module function table
STATIC const mp_rom_map_elem_t ai_inference_module_globals_table[] = {
    { MP_ROM_QSTR(MP_QSTR___name__), MP_ROM_QSTR(MP_QSTR_ai_inference) },
    { MP_ROM_QSTR(MP_QSTR_init), MP_ROM_PTR(&ai_inference_init_obj) },
    { MP_ROM_QSTR(MP_QSTR_classify), MP_ROM_PTR(&ai_inference_classify_obj) },
    { MP_ROM_QSTR(MP_QSTR_get_info), MP_ROM_PTR(&ai_inference_get_info_obj) },
};

STATIC MP_DEFINE_CONST_DICT(ai_inference_module_globals, ai_inference_module_globals_table);

// Module definition
const mp_obj_module_t ai_inference_module = {
    .base = { &mp_type_module },
    .globals = (mp_obj_dict_t*)&ai_inference_module_globals,
};

// Initialize the AI model
STATIC mp_obj_t ai_inference_init(void) {
    // Initialize Edge Impulse model
    if (ai_model_init() == 0) {
        return mp_const_true;
    }
    return mp_const_false;
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(ai_inference_init_obj, ai_inference_init);

// Classify image data
STATIC mp_obj_t ai_inference_classify(mp_obj_t image_data) {
    // Get buffer from MicroPython bytes object
    mp_buffer_info_t bufinfo;
    mp_get_buffer_raise(image_data, &bufinfo, MP_BUFFER_READ);
    
    // Run inference
    float confidence = 0.0f;
    const char* label = ai_classify_image((uint8_t*)bufinfo.buf, bufinfo.len, &confidence);
    
    // Return result as tuple (label, confidence)
    mp_obj_t result[2] = {
        mp_obj_new_str(label, strlen(label)),
        mp_obj_new_float(confidence)
    };
    return mp_obj_new_tuple(2, result);
}
STATIC MP_DEFINE_CONST_FUN_OBJ_1(ai_inference_classify_obj, ai_inference_classify);

// Get model information
STATIC mp_obj_t ai_inference_get_info(void) {
    const char* model_info = ai_get_model_info();
    return mp_obj_new_str(model_info, strlen(model_info));
}
STATIC MP_DEFINE_CONST_FUN_OBJ_0(ai_inference_get_info_obj, ai_inference_get_info);

// Register module
MP_REGISTER_MODULE(MP_QSTR_ai_inference, ai_inference_module, 1);