/***************************************************************************//**
 * @file
 * @brief Core application logic.
 *******************************************************************************
 */
#include "em_common.h"
#include "app_assert.h"
#include "sl_bluetooth.h"
#include "app.h"

#include "em_cmu.h"
#include "em_gpio.h"
#define gattdb_LED_IO 27
#define gattdb_BUTTON_IO 29

static uint8_t advertising_set_handle = 0xff;

void GPIO_ODD_IRQHandler(void)
{
  uint32_t interruptMask = GPIO_IntGet();
  GPIO_IntClear(interruptMask);
}

SL_WEAK void app_init(void)
{
  CMU_ClockEnable(cmuClock_GPIO, true);
  GPIO_PinModeSet(gpioPortA, 4, gpioModePushPull, 1);
  GPIO_PinModeSet(gpioPortC, 7, gpioModeInputPullFilter, 1);
  GPIO_ExtIntConfig(gpioPortC, 7, 1, true, true, true);
  NVIC_ClearPendingIRQ(GPIO_ODD_IRQn);
  NVIC_EnableIRQ(GPIO_ODD_IRQn);
}

SL_WEAK void app_process_action(void)
{
}

void sl_bt_on_event(sl_bt_msg_t *evt)
{
  uint8_t recv_val;
  size_t recv_len;
  sl_status_t sc;

  switch (SL_BT_MSG_ID(evt->header)) {
    case sl_bt_evt_system_boot_id:
      sc = sl_bt_sm_configure(0x03, sl_bt_sm_io_capability_displayonly );
      app_assert_status(sc);

      sc = sl_bt_sm_set_passkey(2342);
      app_assert_status(sc);

      sc = sl_bt_sm_set_bondable_mode(1);
      app_assert_status(sc);

      sc = sl_bt_advertiser_create_set(&advertising_set_handle);
      app_assert_status(sc);

      sc = sl_bt_legacy_advertiser_generate_data(advertising_set_handle,
                                                 sl_bt_advertiser_general_discoverable);
      app_assert_status(sc);

      sc = sl_bt_advertiser_set_timing(
        advertising_set_handle,
        160,
        160,
        0,
        0);
      app_assert_status(sc);

      sc = sl_bt_legacy_advertiser_start(advertising_set_handle,
                                         sl_bt_advertiser_connectable_scannable);
      app_assert_status(sc);
      break;

    case sl_bt_evt_connection_opened_id:
      sc = sl_bt_sm_increase_security(evt->data.evt_connection_opened.connection);
      app_assert_status(sc);
      break;

    case sl_bt_evt_sm_passkey_display_id:
      printf("Passkey: %lu\n", evt->data.evt_sm_passkey_display.passkey);
      break;

    case sl_bt_evt_sm_bonded_id:
      printf("Bonding successful\n");
      break;

    case sl_bt_evt_sm_bonding_failed_id:
      printf("Bonding failed\n");
      break;

    case sl_bt_evt_connection_closed_id:
      sc = sl_bt_legacy_advertiser_generate_data(advertising_set_handle,
                                                 sl_bt_advertiser_general_discoverable);
      app_assert_status(sc);

      sc = sl_bt_legacy_advertiser_start(advertising_set_handle,
                                         sl_bt_advertiser_connectable_scannable);
      app_assert_status(sc);
      break;

    default:
      break;
  }
}
