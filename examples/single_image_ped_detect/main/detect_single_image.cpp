// initialization
#include "pedestrian_detect.hpp"
#include "who_detect_app.hpp"
#include <stdio.h> // Added for file operations

using namespace who::cam;
using namespace who::lcd;
using namespace who::app;

#define WITH_LCD 1
#define LOAD_IMAGE_FROM_SD 1 // <<-- Add this to enable image loading

// Define the path to your image on the SD card
#define IMAGE_PATH "/sdcard/your_image.rgb565" // <<-- IMPORTANT: Change this to your image file
                                             // Ensure this is a raw RGB565 file
                                             // or adapt for JPEG/PNG decoding.
#define IMAGE_WIDTH 240  // <<-- Set your image width
#define IMAGE_HEIGHT 240 // <<-- Set your image height

#if LOAD_IMAGE_FROM_SD
// Buffer to hold image data (RGB565 uses 2 bytes per pixel)
uint16_t image_data[IMAGE_WIDTH * IMAGE_HEIGHT]; // For RGB565

/**
 * @brief Reads an image from the SD card and displays it on the LCD.
 *
 * @param lcd Pointer to the WhoLCD object.
 * @param filename Path to the image file on the SD card.
 * @return esp_err_t ESP_OK on success, ESP_FAIL otherwise.
 */
esp_err_t display_image_from_sd(WhoLCD *lcd, const char *filename)
{
    FILE *f = fopen(filename, "rb");
    if (f == NULL)
    {
        printf("Failed to open image file: %s\n", filename);
        return ESP_FAIL;
    }
    printf("Successfully opened image file: %s\n", filename);

    // Read the image data directly into the buffer
    // This assumes the file is raw pixel data matching IMAGE_WIDTH, IMAGE_HEIGHT, and RGB565 format
    size_t bytes_to_read = IMAGE_WIDTH * IMAGE_HEIGHT * sizeof(uint16_t);
    size_t bytes_read = fread(image_data, 1, bytes_to_read, f);

    fclose(f);

    if (bytes_read != bytes_to_read)
    {
        printf("Failed to read complete image data. Read %d bytes, expected %d\n", bytes_read, bytes_to_read);
        // You might still try to display partial data if desired, or return ESP_FAIL
        // For simplicity, we'll try to display what was read.
    } else {
        printf("Successfully read %d bytes from image file.\n", bytes_read);
    }

    if (bytes_read > 0) {
        // Display the image on the LCD
        // The draw_bitmap function might take different parameters depending on the WhoLCD implementation.
        // This is a common signature: (x_start, y_start, width, height, data_buffer)
        lcd->draw_full_lcd(image_data);
        printf("Image displayed on LCD.\n");
        return ESP_OK;
    }
    return ESP_FAIL;
}
#endif

// execution begins
extern "C" void app_main(void)
{
    // if ped model is on sd card, mount it at the start.
    // checks if esp_err_t value (runtime error) = ESP_OK (which is 0, meaning no error)
#if CONFIG_PEDESTRIAN_DETECT_MODEL_IN_SDCARD || LOAD_IMAGE_FROM_SD // Mount SD if model or image is on it
    printf("Mounting SD card...\n");
    esp_err_t ret = bsp_sdcard_mount();
    if (ret != ESP_OK) {
        printf("Failed to mount SD card: %s\n", esp_err_to_name(ret));
        // Handle error, perhaps by not proceeding or trying to reinitialize
    } else {
        printf("SD card mounted successfully.\n");
    }
    ESP_ERROR_CHECK(ret); // This will abort if ret is not ESP_OK
#endif

    // for ESP32-S3 models, setup LEDs and turn off the green LED on the physical board.
#if CONFIG_IDF_TARGET_ESP32S3
    ESP_ERROR_CHECK(bsp_leds_init());
    ESP_ERROR_CHECK(bsp_led_set(BSP_LED_GREEN, false));
#endif

// Initialize LCD first
    auto lcd = new WhoLCD();
    printf("LCD Initialized.\n");


#if LOAD_IMAGE_FROM_SD && WITH_LCD
    printf("Attempting to load image from SD card...\n");
    esp_err_t display_ret = display_image_from_sd(lcd, IMAGE_PATH);
    if (display_ret == ESP_OK) {
        printf("Image from SD card displayed.\n");
        // You might want to loop here or wait, otherwise app_main will exit
        // For example, wait for 10 seconds:
        // vTaskDelay(pdMS_TO_TICKS(10000));
    } else {
        printf("Failed to display image from SD card.\n");
        // Fallback or error indication if image loading fails
        // For example, fill screen with red
        uint16_t screen_buffer[IMAGE_WIDTH * IMAGE_HEIGHT];
        uint16_t red_color = 0xF800; // RGB565 value for red

        for (int i = 0; i < IMAGE_WIDTH * IMAGE_HEIGHT; ++i) {
            screen_buffer[i] = red_color;
        }
        lcd->draw_full_lcd(screen_buffer);
    }
    // If you only want to display the image and then stop, you can end app_main here
    // or enter a delay loop. The original detection loop is bypassed in this case.
    while(1) { // Keep the image displayed
        vTaskDelay(pdMS_TO_TICKS(1000));
    }

#else // Original camera detection logic
    // for ESP32-P4 or ESP32-S3 models, setup the camera (more details in who_cam folder under who_peripherals)
    #if CONFIG_IDF_TARGET_ESP32P4
        auto cam = new WhoP4Cam(VIDEO_PIX_FMT_RGB565, 3, V4L2_MEMORY_USERPTR, true);
        // auto cam = new WhoP4PPACam(VIDEO_PIX_FMT_RGB565, 4, V4L2_MEMORY_USERPTR, 224, 224, true);
    #elif CONFIG_IDF_TARGET_ESP32S3
        auto cam = new WhoS3Cam(PIXFORMAT_RGB565, FRAMESIZE_240X240, 2, true);
    #endif

    #if WITH_LCD // if LCD = 1
        auto model = new PedestrianDetect(); // new instance of neural network model
        // loop: grab frames from camera, runs model on each frame, draws a red box around each person detected
        auto detect = new WhoDetectAppLCD({{255, 0, 0}});
        detect->set_cam(cam);
        detect->set_lcd(lcd);
        detect->set_model(model);
        // detect->set_fps(5); // good for saving power, debugging
        detect->run();
    #else // if LCD = 0
        auto model = new PedestrianDetect();
        auto detect = new WhoDetectAppTerm(); // print pedestrian coordinates to the terminal
        detect->set_cam(cam);
        detect->set_model(model);
        // detect->set_fps(5);
        detect->run();
    #endif
#endif // LOAD_IMAGE_FROM_SD
}