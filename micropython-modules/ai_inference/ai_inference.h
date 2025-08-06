/*
 * Header file for AI Inference C++ wrapper
 */

#ifndef AI_INFERENCE_H
#define AI_INFERENCE_H

#include <stdint.h>
#include <stddef.h>

#ifdef __cplusplus
extern "C" {
#endif

// Function prototypes for Edge Impulse integration
int ai_model_init(void);
const char* ai_classify_image(uint8_t* image_data, size_t data_len, float* confidence);
const char* ai_get_model_info(void);
void ai_model_deinit(void);

#ifdef __cplusplus
}
#endif

#endif // AI_INFERENCE_H