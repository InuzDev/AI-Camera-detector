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

// Wi-Fi and HTTP Auth settings
#define WIFI_SSID "StarlinkGil" // TODO: Move to a secure config or secrets file
#define WIFI_PASSWORD "Diego2125"
#define AUTH_UID "david"
#define AUTH_PWD "Dev"
#define STREAM_PORT 80

static const char *TAG = "CAM_SERVER";

EventGroupHandle_t wifi_event_group;
#define WIFI_CONNECTED_BIT BIT0

// OV2640 camera config for Seeed XIAO ESP32S3 Sense
camera_config_t camera_config = {
    .pin_pwdn = -1,
    .pin_reset = -1,
    .pin_xclk = 10,
    .pin_sccb_sda = 8,
    .pin_sccb_scl = 9,
    .pin_d7 = 11,
    .pin_d6 = 39,
    .pin_d5 = 40,
    .pin_d4 = 14,
    .pin_d3 = 13,
    .pin_d2 = 41,
    .pin_d1 = 42,
    .pin_d0 = 12,
    .pin_vsync = 38,
    .pin_href = 47,
    .pin_pclk = 48,
    .xclk_freq_hz = 5000000,
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,
    .pixel_format = PIXFORMAT_JPEG,
    .frame_size = FRAMESIZE_QVGA,
    .jpeg_quality = 12,
    .fb_count = 2,
    .fb_location = CAMERA_FB_IN_PSRAM,
    .grab_mode = CAMERA_GRAB_LATEST,
    .sccb_i2c_port = 1};

esp_err_t stream_handler(httpd_req_t *req)
{
  char url[128];
  strncpy(url, req->uri, sizeof(url));
  ESP_LOGI(TAG, "Request: %s", url);

  char *uid = strtok(url + 1, "/");
  char *pwd = strtok(NULL, "/");
  if (!uid || !pwd || strcmp(uid, AUTH_UID) || strcmp(pwd, AUTH_PWD))
  {
    httpd_resp_send_err(req, HTTPD_401_UNAUTHORIZED, "Unauthorized");
    return ESP_FAIL;
  }

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
  if (httpd_start(&server, &config) == ESP_OK)
  {
    httpd_uri_t stream_uri = {
        .uri = "/*",
        .method = HTTP_GET,
        .handler = stream_handler,
        .user_ctx = NULL};
    httpd_register_uri_handler(server, &stream_uri);
  }
  else
  {
    ESP_LOGE(TAG, "Failed to start HTTP server");
  }
}

void connect_wifi()
{
  ESP_LOGI(TAG, "Connecting to Wi-Fi: %s", WIFI_SSID);

  ESP_ERROR_CHECK(esp_netif_init());
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  esp_netif_create_default_wifi_sta();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  wifi_config_t wifi_config = {0};
  strcpy((char *)wifi_config.sta.ssid, WIFI_SSID);
  strcpy((char *)wifi_config.sta.password, WIFI_PASSWORD);
  wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  wifi_event_group = xEventGroupCreate();
  esp_wifi_connect();

  vTaskDelay(4000 / portTICK_PERIOD_MS); // simple wait
  ESP_LOGI(TAG, "Wi-Fi init done");
}

void app_main(void)
{
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND)
  {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ESP_ERROR_CHECK(nvs_flash_init());
  }

  connect_wifi();

  ESP_LOGI(TAG, "Initializing camera...");
  int retry = 0;
  esp_err_t cam_err;
  do
  {
    cam_err = esp_camera_init(&camera_config);
    if (cam_err != ESP_OK)
    {
      ESP_LOGE(TAG, "Camera init failed: %s. Retrying in 2s...", esp_err_to_name(cam_err));
      vTaskDelay(2000 / portTICK_PERIOD_MS);
      retry++;
    }
  } while (cam_err != ESP_OK);

  sensor_t *s = esp_camera_sensor_get();
  ESP_LOGI(TAG, "Sensor PID: 0x%02x", s->id.PID);

  ESP_LOGI(TAG, "Starting stream server...");
  start_server();
}