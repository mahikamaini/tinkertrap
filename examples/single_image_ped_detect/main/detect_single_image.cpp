#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "esp_log.h"
#include "esp_heap_caps.h" // For heap_caps_malloc

// == Board Support Package / Driver Includes ==
// You MUST ensure these are correctly set up for your specific board/hardware
// Example for ESP-BSP:
#include "bsp/esp-bsp.h" // Provides bsp_sdcard_mount() and often LCD init via WhoLCD constructor

// == LCD Class Definition ==
// You MUST include the header file that defines 'who::lcd::WhoLCD'
// This is just a placeholder comment, replace with your actual include.
// For example: #include "who_lcd.hpp"
// Based on your previous input, we know it should at least have:
// namespace who { namespace lcd { class WhoLCD { public: WhoLCD(); void init(); void draw_full_lcd(const void *data); /* ... */ }; } }
// For this example, we'll assume the constructor `new who::lcd::WhoLCD()` initializes the LCD.
// If not, you'll need to call an explicit init function like `lcd->init();`
#include "who_lcd.hpp" // <<<--- REPLACE THIS WITH YOUR ACTUAL WhoLCD HEADER IF DIFFERENT

// For ESP32-S3 Hardware JPEG Decoder
#if CONFIG_IDF_TARGET_ESP32S3
#include "dl_image_jpeg.hpp"
#else
#warning "This example is optimized for ESP32-S3 hardware JPEG decoding."
#endif

static const char *TAG_APP = "jpeg_app_main"; // Tag for app_main
static const char *TAG_JPEG_DISPLAY = "jpeg_display_func"; // Tag for display functions

// Define your LCD dimensions
#define LCD_WIDTH  280
#define LCD_HEIGHT 240

// Buffer for the decoded RGB565 image.
// Allocated dynamically, preferably from PSRAM.
static uint16_t *s_decoded_rgb565_buffer = NULL;

#if CONFIG_IDF_TARGET_ESP32S3
/**
 * @brief Decodes a JPEG from a buffer and outputs to an RGB565 buffer
 * using ESP32-S3 hardware JPEG decoder.
 * The output buffer (out_rgb565_buffer) must be pre-allocated.
 * The JPEG dimensions must match target_width and target_height.
 */
static esp_err_t esp32s3_jpeg_decode_to_rgb565(const uint8_t *jpeg_data, size_t jpeg_data_len,
                                             uint16_t *out_rgb565_buffer, int target_width, int target_height)
{
    if (!jpeg_data || !out_rgb565_buffer || jpeg_data_len == 0) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Invalid arguments for JPEG decode");
        return ESP_ERR_INVALID_ARG;
    }

    jpeg_dec_handle_t jpeg_decoder = NULL;
    esp_err_t err = ESP_FAIL;

    jpeg_dec_config_t config = {
        .out_format = JPEG_DECODE_OUT_FORMAT_RGB565,
        .rgb_order = JPEG_DECODE_RGB_ORDER_RGB,
        .flags = {
            .swap_color_bytes = 1 // Common for ST7789. Adjust if your colors are swapped.
        }
    };

    jpeg_decoder = jpeg_dec_open(&config);
    if (!jpeg_decoder) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Failed to open JPEG decoder (check memory, ESP32-S3 target)");
        return ESP_FAIL;
    }

    jpeg_dec_header_info_t header_info;
    err = jpeg_dec_parse_header(jpeg_decoder, jpeg_data, jpeg_data_len, &header_info);
    if (err != ESP_OK) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Failed to parse JPEG header: %s (%d)", esp_err_to_name(err), err);
        jpeg_dec_close(jpeg_decoder);
        return err;
    }

    ESP_LOGI(TAG_JPEG_DISPLAY, "JPEG dimensions: %dx%d pixels", header_info.width, header_info.height);
    if (header_info.width != target_width || header_info.height != target_height) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "JPEG dimensions (%dx%d) do not match target LCD dimensions (%dx%d)",
                 header_info.width, header_info.height, target_width, target_height);
        jpeg_dec_close(jpeg_decoder);
        return ESP_ERR_INVALID_ARG;
    }

    jpeg_dec_io_t jpeg_io = {0};
    jpeg_io.inbuf = jpeg_data;
    jpeg_io.inbuf_len = jpeg_data_len;
    jpeg_io.outbuf = (uint8_t*)out_rgb565_buffer;
    jpeg_io.outbuf_len = target_width * target_height * sizeof(uint16_t);

    jpeg_dec_output_t jpeg_output_info = {0};

    ESP_LOGD(TAG_JPEG_DISPLAY, "Starting JPEG decoding process...");
    err = jpeg_dec_process(jpeg_decoder, &jpeg_io, &jpeg_output_info);
    if (err != ESP_OK) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "JPEG decode process failed: %s (%d)", esp_err_to_name(err), err);
    } else {
        ESP_LOGI(TAG_JPEG_DISPLAY, "JPEG decoded successfully. Bytes written to output: %d", jpeg_output_info.out_length);
    }

    jpeg_dec_close(jpeg_decoder);
    return err;
}

/**
 * @brief Reads a JPEG image from the SD card, decodes it, and displays it on the LCD.
 *
 * @param lcd Pointer to the initialized who::lcd::WhoLCD object.
 * @param filename Path to the JPEG image file on the SD card (e.g., "/sdcard/image.jpg").
 * @return esp_err_t ESP_OK on success, or an error code on failure.
 */
esp_err_t display_jpeg_from_sd(who::lcd::WhoLCD *lcd, const char *filename)
{
    if (!lcd || !filename) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Invalid arguments to display_jpeg_from_sd");
        return ESP_ERR_INVALID_ARG;
    }

    FILE *f = fopen(filename, "rb");
    if (f == NULL) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Failed to open image file: %s. Check SD card and path.", filename);
        perror("fopen"); // Print system error
        return ESP_FAIL;
    }
    ESP_LOGI(TAG_JPEG_DISPLAY, "Opened image file: %s", filename);

    fseek(f, 0, SEEK_END);
    long jpeg_file_size = ftell(f);
    fseek(f, 0, SEEK_SET);

    if (jpeg_file_size <= 0) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Invalid file size (%ld) for: %s", jpeg_file_size, filename);
        fclose(f);
        return ESP_FAIL;
    }

    uint8_t *jpeg_file_buf = (uint8_t *)heap_caps_malloc(jpeg_file_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_8BIT);
    if (!jpeg_file_buf) {
        jpeg_file_buf = (uint8_t *)malloc(jpeg_file_size); // Fallback to internal RAM
    }
    if (!jpeg_file_buf) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Failed to allocate memory for JPEG file buffer (%ld bytes)", jpeg_file_size);
        fclose(f);
        return ESP_ERR_NO_MEM;
    }

    size_t bytes_read = fread(jpeg_file_buf, 1, jpeg_file_size, f);
    fclose(f);

    if (bytes_read != (size_t)jpeg_file_size) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Read error. Expected %ld bytes, got %d bytes", jpeg_file_size, bytes_read);
        free(jpeg_file_buf);
        return ESP_FAIL;
    }
    ESP_LOGI(TAG_JPEG_DISPLAY, "Read %d bytes from JPEG file into buffer.", bytes_read);

    if (s_decoded_rgb565_buffer == NULL) {
        size_t buffer_size = LCD_WIDTH * LCD_HEIGHT * sizeof(uint16_t);
        ESP_LOGI(TAG_JPEG_DISPLAY, "Allocating RGB565 buffer for %dx%d image (%d bytes)", LCD_WIDTH, LCD_HEIGHT, buffer_size);
        s_decoded_rgb565_buffer = (uint16_t *)heap_caps_malloc(buffer_size, MALLOC_CAP_SPIRAM | MALLOC_CAP_DMA);
        if (!s_decoded_rgb565_buffer) {
            s_decoded_rgb565_buffer = (uint16_t *)malloc(buffer_size);
        }
    }

    if (!s_decoded_rgb565_buffer) {
        ESP_LOGE(TAG_JPEG_DISPLAY, "Failed to allocate memory for decoded RGB565 buffer");
        free(jpeg_file_buf);
        return ESP_ERR_NO_MEM;
    }
    ESP_LOGD(TAG_JPEG_DISPLAY, "RGB565 output buffer is at %p", s_decoded_rgb565_buffer);

    esp_err_t decode_err = esp32s3_jpeg_decode_to_rgb565(jpeg_file_buf, jpeg_file_size,
                                                        s_decoded_rgb565_buffer, LCD_WIDTH, LCD_HEIGHT);
    free(jpeg_file_buf);

    if (decode_err == ESP_OK) {
        ESP_LOGI(TAG_JPEG_DISPLAY, "JPEG decoded successfully. Displaying on LCD...");
        lcd->draw_full_lcd(s_decoded_rgb565_buffer);
        ESP_LOGI(TAG_JPEG_DISPLAY, "Image displayed on LCD.");
        return ESP_OK;
    } else {
        ESP_LOGE(TAG_JPEG_DISPLAY, "JPEG decoding failed. Error: %s (%d)", esp_err_to_name(decode_err), decode_err);
        return ESP_FAIL;
    }
}
#endif // CONFIG_IDF_TARGET_ESP32S3

// Main application entry point
extern "C" void app_main(void)
{
    ESP_LOGI(TAG_APP, "Starting JPEG Display Application (app_main)");

    // Initialize PSRAM if you haven't already (usually done by IDF startup if enabled)
#if CONFIG_ESP_SPIRAM_SUPPORT || CONFIG_SPIRAM // Kconfig names vary by IDF version
    ESP_LOGI(TAG_APP, "PSRAM should be enabled and initialized by startup.");
#else
    ESP_LOGW(TAG_APP, "PSRAM not enabled. JPEG decoding for large images might fail or be slow.");
#endif

    // Initialize LCD
    // This assumes your WhoLCD class constructor initializes the LCD.
    // If not, you might need to call lcd->init(); explicitly after creation.
    // It also assumes your project correctly links the WhoLCD implementation.
    ESP_LOGI(TAG_APP, "Initializing LCD...");
    who::lcd::WhoLCD *lcd = new who::lcd::WhoLCD();
    if (!lcd) { // Basic check, though new usually throws if fails
        ESP_LOGE(TAG_APP, "Failed to create WhoLCD object. Halting.");
        return;
    }
    // If your WhoLCD needs an explicit init and constructor doesn't call it:
    // lcd->init(); 
    ESP_LOGI(TAG_APP, "LCD object created.");

    // Mount SD Card
    // This uses bsp_sdcard_mount() which is common in ESP-BSP.
    // If you use a different method, replace this.
    ESP_LOGI(TAG_APP, "Mounting SD card...");
    esp_err_t ret_sd = bsp_sdcard_mount();
    if (ret_sd != ESP_OK) {
        ESP_LOGE(TAG_APP, "Failed to mount SD card: %s. Cannot load image.", esp_err_to_name(ret_sd));
        // Depending on your app, you might want to halt or continue without SD functionality
    } else {
        ESP_LOGI(TAG_APP, "SD card mounted successfully.");

#if CONFIG_IDF_TARGET_ESP32S3
        // Path to your 280x240 JPEG image on the SD card
        const char *jpeg_image_path = "dan/._IMG_0001.JPG"; // IMPORTANT: Use your actual filename
        ESP_LOGI(TAG_APP, "Attempting to display JPEG: %s", jpeg_image_path);

        esp_err_t display_ret = display_jpeg_from_sd(lcd, jpeg_image_path);
        if (display_ret == ESP_OK) {
            ESP_LOGI(TAG_APP, "Successfully displayed JPEG image.");
        } else {
            ESP_LOGE(TAG_APP, "Failed to display JPEG image.");
            // Optional: Fallback - fill screen with a color (e.g., blue)
            if (s_decoded_rgb565_buffer) { // Check if buffer was allocated
                ESP_LOGI(TAG_APP, "Display failed, filling screen with blue as fallback.");
                uint16_t fallback_color = 0x001F; // Blue in RGB565
                for(int i=0; i < LCD_WIDTH * LCD_HEIGHT; ++i) {
                    s_decoded_rgb565_buffer[i] = fallback_color;
                }
                lcd->draw_full_lcd(s_decoded_rgb565_buffer);
            }
        }
#else
        ESP_LOGE(TAG_APP, "JPEG display is only implemented for ESP32-S3 in this example.");
        // Optional: Fallback for non-S3 targets - fill screen with a color
        if (s_decoded_rgb565_buffer == NULL) { // Allocate if not done by S3 path
            size_t buffer_size = LCD_WIDTH * LCD_HEIGHT * sizeof(uint16_t);
            s_decoded_rgb565_buffer = (uint16_t *)malloc(buffer_size);
        }
        if (s_decoded_rgb565_buffer) {
             ESP_LOGI(TAG_APP, "Filling screen with gray (non-S3 fallback).");
            uint16_t fallback_color = 0x8410; // Gray
            for(int i=0; i < LCD_WIDTH * LCD_HEIGHT; ++i) s_decoded_rgb565_buffer[i] = fallback_color;
            lcd->draw_full_lcd(s_decoded_rgb565_buffer);
        }
#endif
    }

    ESP_LOGI(TAG_APP, "Display task finished. Looping indefinitely...");
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

    // Cleanup (normally not reached in this example due to infinite loop)
    // This would be important if app_main could exit or in a deinit function.
    if (s_decoded_rgb565_buffer) {
        free(s_decoded_rgb565_buffer);
        s_decoded_rgb565_buffer = NULL;
    }
    if (lcd) {
        // If WhoLCD has a specific deinit function or if 'delete' handles it:
        // lcd->deinit(); // or similar
        delete lcd;
        lcd = NULL;
    }
    // if (ret_sd == ESP_OK) { // Only unmount if successfully mounted
    //     bsp_sdcard_unmount();
    // }
    ESP_LOGI(TAG_APP, "Application cleanup finished (theoretically).");
}