#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

// Put function declarations here:
int myFunction(int, int);

// This is the ESP-IDF entry point
extern "C" void app_main()
{
  // Initialization code runs once
  int result = myFunction(2, 3);
  printf("Result: %d\n", result);

  // Example loop simulation using FreeRTOS task
  while (true)
  {
    printf("Running main loop...\n");
    vTaskDelay(pdMS_TO_TICKS(1000)); // delay 1 second
  }
}

// Put function definitions here:
int myFunction(int x, int y)
{
  return x + y;
}