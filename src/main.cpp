extern "C"
{
#include "secret.h"
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
#include "esp_netif.h"
#include "esp_netif_ip_addr.h"
#include "esp_netif_types.h"
#include "mbedtls/base64.h"
}

#define STREAM_PORT 80
#define WIFI_CONNECTED_BIT BIT0

EventGroupHandle_t wifi_event_group;

static const char *TAG = "CAM_SERVER";

// Camera config for Seeed XIAO ESP32S3 Sense (OV2640)
camera_config_t config = {
    .pin_pwdn = -1,     // Power down pin (not used)
    .pin_reset = -1,    // Reset pin (not used)
    .pin_xclk = 10,     // XCLK pin
    .pin_sccb_sda = 40, // I2C SDA (SCCB)
    .pin_sccb_scl = 39, // I2C SCL (SCCB)

    // Camera data pins (DVP interface)
    .pin_d7 = 48,
    .pin_d6 = 47,
    .pin_d5 = 38,
    .pin_d4 = 21,
    .pin_d3 = 14,
    .pin_d2 = 13,
    .pin_d1 = 12,
    .pin_d0 = 11,
    .pin_vsync = 42, // Vertical sync
    .pin_href = 41,  // Horizontal reference
    .pin_pclk = 2,   // Pixel clock

    // Clock and timing settings - try different frequencies
    .xclk_freq_hz = 20000000, // Back to 20MHz - original setting
    .ledc_timer = LEDC_TIMER_0,
    .ledc_channel = LEDC_CHANNEL_0,

    // Image format settings - minimal for testing
    .pixel_format = PIXFORMAT_RGB565,
    .frame_size = FRAMESIZE_96X96, // Smallest size for testing
    .jpeg_quality = 10,            // Lower quality for stability
    .fb_count = 2,                 // Single buffer for initial testing
    .fb_location = CAMERA_FB_IN_DRAM,
    .grab_mode = CAMERA_GRAB_LATEST,
    .conv_mode = CONV_DISABLE, // Disable conversion for now
    .sccb_i2c_port = 1,        // I2C port 1
};

static void wifi_event_handler(void *arg, esp_event_base_t event_base,
                               int32_t event_id, void *event_data)
{
  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START)
  {
    esp_wifi_connect();
    ESP_LOGI(TAG, "Wi-Fi started, attempting to connect");
  }
  else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED)
  {
    esp_wifi_connect();
    ESP_LOGI(TAG, "Disconnected, retrying to connect to the AP");
  }
  else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP)
  {
    ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
    ESP_LOGI(TAG, "Got IP: " IPSTR, IP2STR(&event->ip_info.ip));
    ESP_LOGI(TAG, "Access stream at: http://" IPSTR ":%d/%s/%s", IP2STR(&event->ip_info.ip), STREAM_PORT, AUTH_UID, AUTH_PWD);
    xEventGroupSetBits(wifi_event_group, WIFI_CONNECTED_BIT);
  }
}

esp_err_t stream_handler(httpd_req_t *req)
{
  ESP_LOGI(TAG, "Stream handler called for URI: %s", req->uri);

  char *buf = NULL;
  size_t buf_len = 0;
  bool authenticated = false;

  // Basic Authentication check
  buf_len = httpd_req_get_hdr_value_len(req, "Authorization") + 1;
  if (buf_len > 1)
  {
    buf = (char *)malloc(buf_len);
    if (httpd_req_get_hdr_value_str(req, "Authorization", buf, buf_len) == ESP_OK)
    {
      char *auth_credentials = strstr(buf, "Basic ") + 6;
      if (auth_credentials)
      {
        unsigned char decoded_credentials[128];
        size_t decoded_len = 0;
        char expected_credentials[128];
        snprintf(expected_credentials, sizeof(expected_credentials), "%s:%s", AUTH_UID, AUTH_PWD);

        // Base64 decode the credentials
        if (mbedtls_base64_decode(decoded_credentials, sizeof(decoded_credentials) - 1, &decoded_len, (unsigned char *)auth_credentials, strlen(auth_credentials)) == 0)
        {
          decoded_credentials[decoded_len] = '\0'; // Null-terminate
          if (strcmp((char *)decoded_credentials, expected_credentials) == 0)
          {
            authenticated = true;
          }
        }
      }
    }
    free(buf);
  }

  if (!authenticated)
  {
    ESP_LOGW(TAG, "Authentication failed");
    httpd_resp_set_hdr(req, "WWW-Authenticate", "Basic realm=\"Camera\"");
    httpd_resp_send_err(req, HTTPD_401_UNAUTHORIZED, "Authentication required");
    return ESP_FAIL;
  }

  ESP_LOGI(TAG, "Authentication successful");

  // MJPEG header
  httpd_resp_set_type(req, "multipart/x-mixed-replace; boundary=frame");

  int consecutive_failures = 0;
  const int max_consecutive_failures = 3;

  while (true)
  {
    camera_fb_t *fb = esp_camera_fb_get();
    if (!fb)
    {
      consecutive_failures++;
      ESP_LOGE(TAG, "Camera capture failed (attempt %d/%d)", consecutive_failures, max_consecutive_failures);

      if (consecutive_failures >= max_consecutive_failures)
      {
        ESP_LOGE(TAG, "Too many consecutive camera failures, ending stream");
        httpd_resp_send_err(req, HTTPD_500_INTERNAL_SERVER_ERROR, "Camera capture failed");
        return ESP_FAIL;
      }

      // Wait a bit before retrying
      vTaskDelay(100 / portTICK_PERIOD_MS);
      continue;
    }

    // Reset failure counter on successful capture
    consecutive_failures = 0;

    // Validate frame buffer
    if (fb->len == 0 || fb->buf == NULL)
    {
      ESP_LOGW(TAG, "Invalid frame buffer received (len=%d, buf=%p)", fb->len, fb->buf);
      esp_camera_fb_return(fb);
      continue;
    }

    ESP_LOGD(TAG, "Frame captured successfully, size: %d bytes", fb->len);

    char part[128];
    int part_len = snprintf(part, sizeof(part),
                            "--frame\r\nContent-Type: image/jpeg\r\nContent-Length: %d\r\n\r\n",
                            fb->len);

    if (httpd_resp_send_chunk(req, part, part_len) != ESP_OK ||
        httpd_resp_send_chunk(req, (const char *)fb->buf, fb->len) != ESP_OK ||
        httpd_resp_send_chunk(req, "\r\n", 2) != ESP_OK)
    {
      esp_camera_fb_return(fb);
      ESP_LOGW(TAG, "Connection closed by client");
      break;
    }

    esp_camera_fb_return(fb);

    // Small delay to prevent overwhelming the system
    vTaskDelay(30 / portTICK_PERIOD_MS);
  }

  return ESP_OK;
}

httpd_handle_t start_server(void)
{
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  config.server_port = STREAM_PORT;

  httpd_handle_t server = NULL;
  if (httpd_start(&server, &config) != ESP_OK)
  {
    ESP_LOGE(TAG, "Failed to start HTTP server");
    return NULL;
  }

  httpd_uri_t stream_uri = {
      .uri = "/InuzDev/ALPHADEV",
      .method = HTTP_GET,
      .handler = stream_handler,
      .user_ctx = NULL};
  httpd_register_uri_handler(server, &stream_uri);
  ESP_LOGI(TAG, "Registering URI handler for /InuzDev/ALPHADEV");
  ESP_LOGI(TAG, "Stream server started on port %d", STREAM_PORT);
  return server;
}

void stop_server(httpd_handle_t server)
{
  if (server)
  {
    httpd_stop(server);
  }
}

void connect_wifi()
{
  ESP_LOGI(TAG, "Connecting to Wi-Fi: %s", WIFI_SSID);
  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();

  ESP_ERROR_CHECK(esp_netif_init());
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  esp_netif_create_default_wifi_sta();

  // Register event handlers
  ESP_ERROR_CHECK(esp_event_handler_register(WIFI_EVENT, ESP_EVENT_ANY_ID, &wifi_event_handler, NULL));
  ESP_ERROR_CHECK(esp_event_handler_register(IP_EVENT, IP_EVENT_STA_GOT_IP, &wifi_event_handler, NULL));

  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  wifi_config_t wifi_config = {};
  strncpy((char *)wifi_config.sta.ssid, WIFI_SSID, sizeof(wifi_config.sta.ssid) - 1);
  wifi_config.sta.ssid[sizeof(wifi_config.sta.ssid) - 1] = '\0';
  strncpy((char *)wifi_config.sta.password, WIFI_PASSWORD, sizeof(wifi_config.sta.password) - 1);
  wifi_config.sta.password[sizeof(wifi_config.sta.password) - 1] = '\0';
  wifi_config.sta.threshold.authmode = WIFI_AUTH_WPA2_PSK;

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  ESP_LOGI(TAG, "Wi-Fi init done");
  ESP_LOGI(TAG, "Waiting for connection...");

  // Wait for connection
  EventBits_t bits = xEventGroupWaitBits(wifi_event_group, WIFI_CONNECTED_BIT, pdFALSE, pdFALSE, 10000 / portTICK_PERIOD_MS);
  if (bits & WIFI_CONNECTED_BIT)
  {
    ESP_LOGI(TAG, "Connected to Wi-Fi");
  }
  else
  {
    ESP_LOGE(TAG, "Failed to connect to Wi-Fi within 10 seconds");
  }
}

extern "C" void app_main()
{
  wifi_event_group = xEventGroupCreate();
  esp_err_t err = nvs_flash_init();
  if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND)
    ESP_ERROR_CHECK(nvs_flash_erase());
  ESP_ERROR_CHECK(nvs_flash_init());

  connect_wifi();

  // Print detailed camera configuration
  ESP_LOGI(TAG, "Camera Configuration:");
  ESP_LOGI(TAG, "  XCLK: %d Hz", config.xclk_freq_hz);
  ESP_LOGI(TAG, "  Frame size: %d", config.frame_size);
  ESP_LOGI(TAG, "  JPEG quality: %d", config.jpeg_quality);
  ESP_LOGI(TAG, "  Frame buffers: %d", config.fb_count);
  ESP_LOGI(TAG, "  Grab mode: %d", config.grab_mode);

  ESP_LOGI(TAG, "Initializing camera...");

  // Try different XCLK frequencies to find one that works
  uint32_t xclk_frequencies[] = {20000000, 10000000, 8000000, 5000000};
  int num_frequencies = sizeof(xclk_frequencies) / sizeof(xclk_frequencies[0]);

  esp_err_t cam_err = ESP_FAIL;
  bool camera_initialized = false;

  for (int freq_idx = 0; freq_idx < num_frequencies && !camera_initialized; freq_idx++)
  {
    config.xclk_freq_hz = xclk_frequencies[freq_idx];
    ESP_LOGI(TAG, "Trying XCLK frequency: %d Hz", config.xclk_freq_hz);

    for (int retry = 0; retry < 2; retry++)
    {
      ESP_LOGI(TAG, "Camera init attempt %d/2 with %d MHz", retry + 1, config.xclk_freq_hz / 1000000);
      cam_err = esp_camera_init(&config);

      if (cam_err == ESP_OK)
      {
        ESP_LOGI(TAG, "Camera initialized successfully with %d MHz XCLK!", config.xclk_freq_hz / 1000000);
        camera_initialized = true;
        break;
      }
      else
      {
        ESP_LOGE(TAG, "Camera init failed: %s (0x%x)", esp_err_to_name(cam_err), cam_err);
        vTaskDelay(1000 / portTICK_PERIOD_MS);
      }
    }
  }

  if (!camera_initialized)
  {
    ESP_LOGE(TAG, "Failed to init camera with any XCLK frequency. Error: %s (0x%x)", esp_err_to_name(cam_err), cam_err);
    ESP_LOGE(TAG, "This could indicate:");
    ESP_LOGE(TAG, "  1. Hardware connection issues");
    ESP_LOGE(TAG, "  2. Power supply problems");
    ESP_LOGE(TAG, "  3. Pin configuration errors");
    ESP_LOGE(TAG, "  4. Camera module failure");
    ESP_LOGE(TAG, "  5. Incorrect pin mapping for your board");
    esp_restart();
  }

  sensor_t *s = esp_camera_sensor_get();
  if (s == NULL)
  {
    ESP_LOGE(TAG, "Failed to get camera sensor!");
    esp_restart();
  }

  ESP_LOGI(TAG, "Sensor PID: 0x%02x", s->id.PID);
  ESP_LOGI(TAG, "Sensor VER: 0x%02x", s->id.VER);
  ESP_LOGI(TAG, "Sensor MIDL: 0x%02x", s->id.MIDL);
  ESP_LOGI(TAG, "Sensor MIDH: 0x%02x", s->id.MIDH);

  // Additional camera sensor configuration for better stability
  if (s != NULL)
  {
    // Set some sensor-specific settings for OV2640
    s->set_brightness(s, 0);                 // -2 to 2
    s->set_contrast(s, 0);                   // -2 to 2
    s->set_saturation(s, 0);                 // -2 to 2
    s->set_special_effect(s, 0);             // 0 to 6 (0=No Effect, 1=Negative, 2=Grayscale, 3=Red Tint, 4=Green Tint, 5=Blue Tint, 6=Sepia)
    s->set_whitebal(s, 1);                   // 0 = disable , 1 = enable
    s->set_awb_gain(s, 1);                   // 0 = disable , 1 = enable
    s->set_wb_mode(s, 0);                    // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
    s->set_exposure_ctrl(s, 1);              // 0 = disable , 1 = enable
    s->set_aec2(s, 0);                       // 0 = disable , 1 = enable
    s->set_ae_level(s, 0);                   // -2 to 2
    s->set_aec_value(s, 300);                // 0 to 1200
    s->set_gain_ctrl(s, 1);                  // 0 = disable , 1 = enable
    s->set_agc_gain(s, 0);                   // 0 to 30
    s->set_gainceiling(s, (gainceiling_t)0); // 0 to 6
    s->set_bpc(s, 0);                        // 0 = disable , 1 = enable
    s->set_wpc(s, 1);                        // 0 = disable , 1 = enable
    s->set_raw_gma(s, 1);                    // 0 = disable , 1 = enable
    s->set_lenc(s, 1);                       // 0 = disable , 1 = enable
    s->set_hmirror(s, 0);                    // 0 = disable , 1 = enable
    s->set_vflip(s, 0);                      // 0 = disable , 1 = enable
    s->set_dcw(s, 1);                        // 0 = disable , 1 = enable
    s->set_colorbar(s, 1);                   // 0 = disable , 1 = enable

    ESP_LOGI(TAG, "Camera sensor configured successfully");
  }
  else
  {
    ESP_LOGW(TAG, "Failed to get camera sensor for configuration");
  }

  // Test camera capture before starting server with multiple attempts
  ESP_LOGI(TAG, "Testing camera capture...");

  // Try different approaches to get the camera working
  ESP_LOGI(TAG, "Attempting to reset camera sensor...");

  // Try to trigger the sensor
  if (s != NULL)
  {
    // Try enabling colorbar first (test pattern)
    ESP_LOGI(TAG, "Enabling test pattern...");
    s->set_colorbar(s, 1);
    vTaskDelay(500 / portTICK_PERIOD_MS);

    camera_fb_t *test_fb = esp_camera_fb_get();
    if (test_fb)
    {
      ESP_LOGI(TAG, "Test pattern capture successful! Frame size: %d bytes", test_fb->len);
      esp_camera_fb_return(test_fb);

      // Disable test pattern and try normal capture
      s->set_colorbar(s, 0);
      ESP_LOGI(TAG, "Disabling test pattern, trying normal capture...");
      vTaskDelay(500 / portTICK_PERIOD_MS);
    }
    else
    {
      ESP_LOGW(TAG, "Test pattern capture failed");
    }
  }

  // Try multiple capture attempts with different settings
  bool capture_success = false;
  for (int attempt = 1; attempt <= 5; attempt++)
  {
    ESP_LOGI(TAG, "Capture attempt %d/5...", attempt);

    camera_fb_t *test_fb = esp_camera_fb_get();
    if (test_fb)
    {
      ESP_LOGI(TAG, "Capture successful! Frame size: %d bytes, format: %d", test_fb->len, test_fb->format);
      esp_camera_fb_return(test_fb);
      capture_success = true;
      break;
    }
    else
    {
      ESP_LOGW(TAG, "Capture attempt %d failed", attempt);

      // Try different settings between attempts
      if (s != NULL && attempt < 5)
      {
        switch (attempt)
        {
        case 1:
          ESP_LOGI(TAG, "Trying with different exposure settings...");
          s->set_aec_value(s, 600);
          break;
        case 2:
          ESP_LOGI(TAG, "Trying with manual gain...");
          s->set_gain_ctrl(s, 0);
          s->set_agc_gain(s, 10);
          break;
        case 3:
          ESP_LOGI(TAG, "Trying with different white balance...");
          s->set_whitebal(s, 0);
          break;
        case 4:
          ESP_LOGI(TAG, "Trying with simplified settings...");
          s->set_exposure_ctrl(s, 0);
          s->set_gain_ctrl(s, 0);
          break;
        }
        vTaskDelay(1000 / portTICK_PERIOD_MS);
      }
    }
  }

  if (!capture_success)
  {
    ESP_LOGE(TAG, "All capture attempts failed!");
    ESP_LOGE(TAG, "Camera hardware may have issues or need different configuration");
    ESP_LOGE(TAG, "Continuing with server startup - streaming may still work...");
  }

  ESP_LOGI(TAG, "Starting stream server...");
  httpd_handle_t server = start_server();
  if (server == NULL)
  {
    ESP_LOGE(TAG, "Failed to start web server, restarting.");
    esp_restart();
  }
}
