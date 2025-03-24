#ifndef _SOFT_AP_H_
#define _SOFT_AP_H_

#define EXAMPLE_ESP_WIFI_SSID      "esp32-luchian"
#define EXAMPLE_ESP_WIFI_PASS      "12345678"
#define EXAMPLE_ESP_WIFI_CHANNEL   6
#define EXAMPLE_MAX_STA_CONN       4

void wifi_init_softap(void);
void wifi_scan(void);

#endif