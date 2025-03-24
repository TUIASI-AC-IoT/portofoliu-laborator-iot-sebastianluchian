/*  WiFi softAP Example

   This example code is in the Public Domain (or CC0 licensed, at your option.)

   Unless required by applicable law or agreed to in writing, this
   software is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
   CONDITIONS OF ANY KIND, either express or implied.
*/
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"
#include "freertos/event_groups.h"
#include "esp_http_server.h"


#include "lwip/err.h"
#include "lwip/sys.h"

#include "soft-ap.h"
#include "http-server.h"

#include "../mdns/include/mdns.h"

static const char *SOFTAP_TAG = "wifi softAP";

void app_main(void)
{
    //Initialize NVS
    esp_err_t ret = nvs_flash_init();
    if (ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
      ESP_ERROR_CHECK(nvs_flash_erase());
      ret = nvs_flash_init();
    }
    ESP_ERROR_CHECK(ret);

     // Initialize NVS
     esp_err_t err = nvs_flash_init();
     if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
         // NVS partition was truncated and needs to be erased
         // Retry nvs_flash_init
         ESP_ERROR_CHECK(nvs_flash_erase());
         err = nvs_flash_init();
     }
     ESP_ERROR_CHECK( err );

    static httpd_handle_t server = NULL;

    // TODO: 3. Pornire mod STA + scanare SSID-uri disponibile


    // wifi_scan();

    // TODO: 4. Initializare mDNS (daca mai ramana timp)   


    // TODO: 1. Pornire softAP

    ESP_LOGI(SOFTAP_TAG, "ESP_WIFI_MODE_AP");
    wifi_init_softap();

    
    esp_netif_init();
    esp_event_loop_create_default();
    esp_netif_t *wifi_netif = esp_netif_create_default_wifi_sta();
    wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
    esp_wifi_init(&cfg);
    esp_wifi_set_mode(WIFI_MODE_STA);
    esp_wifi_start();
    esp_wifi_stop();
    esp_wifi_deinit();
    esp_wifi_clear_default_wifi_driver_and_handlers(wifi_netif);
    esp_netif_destroy(wifi_netif);

    // TODO: 2. Pornire server web (si config specifice in http-server.c) 
    server = start_webserver();

     // Open
     printf("\n");
     printf("Opening Non-Volatile Storage (NVS) handle... ");
     nvs_handle_t my_handle;
     err = nvs_open("storage", NVS_READWRITE, &my_handle);
     if (err != ESP_OK) {
         printf("Error (%s) opening NVS handle!\n", esp_err_to_name(err));
     } else {
         printf("Done\n");
 
         // Read
         printf("Reading restart counter from NVS ... ");
         int32_t restart_counter = 0; // value will default to 0, if not set yet in NVS
         err = nvs_get_i32(my_handle, "restart_counter", &restart_counter);
         switch (err) {
             case ESP_OK:
                 printf("Done\n");
                 break;
             case ESP_ERR_NVS_NOT_FOUND:
                 printf("The value is not initialized yet!\n");
                 break;
             default :
                 printf("Error (%s) reading!\n", esp_err_to_name(err));
         }
 
         // Write
         printf("Updating restart counter in NVS ... ");
         restart_counter++;
         err = nvs_set_i32(my_handle, "restart_counter", restart_counter);
         printf((err != ESP_OK) ? "Failed!\n" : "Done\n");
 
         // Commit written value.
         // After setting any values, nvs_commit() must be called to ensure changes are written
         // to flash storage. Implementations may write to storage at other times,
         // but this is not guaranteed.
         printf("Committing updates in NVS ... ");
         err = nvs_commit(my_handle);
         printf((err != ESP_OK) ? "Failed!\n" : "Done\n");
 
         // Close
         nvs_close(my_handle);
     }
 
     printf("\n");
}