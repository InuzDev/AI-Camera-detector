extern "C"
{
#include <stdio.h>
#include <string.h>
#include "esp_camera.h"
#include "esp_log.h"
#include "esp_http_server.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "nvs_flash.h"
#include "lwip/err.h"
#include "lwip/sys.h"
#include "freertos/FreeRTOS.h"
#include "freertos/event_groups.h"
}

EventGroupHandle_t wifi_event_group;

#define WIFI_CONNECTED_BIT BIT0

#define WIFI_SSID "YourSSID"
#define WIFI_PASSWORD "YourPassword"
#define STREAM_PORT 80

#define AUTH_UID "david"
#define AUTH_PWD "Dev"

static const char *TAG = "CAM_SERVER";

// Camera config for Seeed XIAO ESP32S3 Sense
camera_config_t camera_config = {
    camera_config.pin_pwdn = -1,
    camera_config.pin_reset = -1,
    camera_config.pin_xclk = 10,
    camera_config.pin_sccb_sda = 8,
    camera_config.pin_sccb_scl = 9,
    camera_config.pin_d7 = 18,
    camera_config.pin_d6 = 17,
    camera_config.pin_d5 = 16,
    camera_config.pin_d4 = 15,
    camera_config.pin_d3 = 14,
    camera_config.pin_d2 = 13,
    camera_config.pin_d1 = 12,
    camera_config.pin_d0 = 11,
    camera_config.pin_vsync = 6,
    camera_config.pin_href = 7,
    camera_config.pin_pclk = 5,
    camera_config.xclk_freq_hz = 20000000,
    camera_config.ledc_timer = LEDC_TIMER_0,
    camera_config.ledc_channel = LEDC_CHANNEL_0,
    camera_config.pixel_format = PIXFORMAT_JPEG,
    camera_config.frame_size = FRAMESIZE_QVGA,
    camera_config.jpeg_quality = 10,
    camera_config.fb_count = 2,
    camera_config.grab_mode = CAMERA_GRAB_LATEST,
    camera_config.fb_location = CAMERA_FB_IN_PSRAM,
};

esp_err_t stream_handler(httpd_req_t *req)
{
  char url[128];
  strncpy(url, req->uri, sizeof(url));
  ESP_LOGI(TAG, "Request: %s", url);

  // Simple auth check: /UID/PWD
  char *uid = strtok(url + 1, "/");
  char *pwd = strtok(NULL, "/");
  if (!uid || !pwd || strcmp(uid, AUTH_UID) || strcmp(pwd, AUTH_PWD))
  {
    httpd_resp_send_err(req, HTTPD_401_UNAUTHORIZED, "Unauthorized");
    return ESP_FAIL;
  }

  // MJPEG header
  httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");

  while (true)
  {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb)
    {
      ESP_LOGE(TAG, "Camera capture failed");
      break;
    }

    char part[64];
    snprintf(part, sizeof(part),
             "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n",
             fb->len);
    httpd_resp_send_chunk(req, part, strlen(part));
    httpd_resp_send_chunk(req, (char *)fb->buf, fb->len);
    httpd_resp_send_chunk(req, "\r\n", 2);

    esp_camera_fb_return(fb);
  }

  return ESP_OK;
}

void start_server()
{
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = STREAM_PORT;

  httpd_handle_t server = NULL;
  httpd_start(&server, &config);

  httpd_uri_t stream_uri = {
      .uri = "/*",
      .method = HTTP_GET,
      .handler = stream_handler,
      .user_ctx = NULL};

  httpd_register_uri_handler(server, &stream_uri);
}

void connect_wifi()
{
  ESP_LOGI(TAG, "Connecting to Wi-Fi: %s", WIFI_SSID);
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();

  ESP_ERROR_CHECK(esp_netif_init());
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  esp_netif_create_default_wifi_sta();

  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  wifi_config_t wifi_config = {
      .sta = {
          .ssid = WIFI_SSID,
          .password = WIFI_PASSWORD,
          .threshold.authmode = WIFI_AUTH_WPA2_PSK}};

  strncpy((char *)wifi_config_sta.ssid, WIFI_SSID, sizeof(wifi_config.sta.ssid));

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  ESP_LOGI(TAG, "Wi-Fi init done");

  ESP_LOGI(TAG, "Waiting for connection...");
  EventBits_t bits = xEventGroupWaitBits(wifi_event_group, WIFI_CONNECTED_BIT, pdTRUE, pdFALSE, portMAX_DELAY);

  wifi_event_group = xEventGroupCreate();

  esp_wifi_connect();
  vTaskDelay(4000 / portTICK_PERIOD_MS); // wait ~4s
}

void app_main()
{
  wifi_event_group = xEventGroupCreate();
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND)
    ESP_ERROR_CHECK(nvs_flash_erase());
  ESP_ERROR_CHECK(nvs_flash_init());

  connect_wifi();

  ESP_LOGI(TAG, "Initializing camera...");
  if (esp_camera_init(&camera_config) != ESP_OK)
  {
    ESP_LOGE(TAG, "Camera init failed");
    return;
  }

  ESP_LOGI(TAG, "Starting stream server...");
  start_server();
}