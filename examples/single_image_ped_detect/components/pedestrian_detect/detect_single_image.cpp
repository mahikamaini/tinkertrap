#include "detect_single_image.hpp"
#include "pedestrian_detect.hpp"
#include "esp_log.h"
#include "esp_err.h"
#include "esp_vfs_fat.h"
#include "driver/sdmmc_host.h"
#include "driver/sdmmc_defs.h"
#include "sdmmc_cmd.h"
#include "esp_timer.h"
#include "dl_image.hpp"

#define TAG "SingleImageDetect"

// Load RGB565 raw image from SD card
bool load_image_from_sd(const char *path, dl::image::Image &img)
{
    FILE *f = fopen(path, "rb");
    if (!f) {
        ESP_LOGE(TAG, "Failed to open image file: %s", path);
        return false;
    }

    size_t size = 240 * 240 * 2; // RGB565: 2 bytes per pixel
    uint8_t *buf = (uint8_t *)malloc(size);
    if (!buf) {
        ESP_LOGE(TAG, "Failed to allocate memory for image");
        fclose(f);
        return false;
    }

    fread(buf, 1, size, f);
    fclose(f);

    img.buffer = buf;
    img.height = 240;
    img.width = 240;
    img.channels = 3; // Will be converted
    img.pix_format = DL_IMAGE_CAP_RGB565_BIG_ENDIAN;
    return true;
}

void run_single_image_detection(const char *image_path)
{
    // Mount SD card
    ESP_LOGI(TAG, "Mounting SD card...");
    esp_err_t ret = bsp_sdcard_mount();  // assumes your BSP defines this
    if (ret != ESP_OK) {
        ESP_LOGE(TAG, "Failed to mount SD card");
        return;
    }

    // Load image
    dl::image::Image img;
    if (!load_image_from_sd(image_path, img)) {
        ESP_LOGE(TAG, "Image load failed");
        return;
    }

    // Initialize model
    PedestrianDetect model;
    auto &results = model.run(img);

    // Display results
    for (auto &r : results) {
        ESP_LOGI(TAG, "Detection: x0=%d y0=%d x1=%d y1=%d score=%.2f",
                 r.box[0], r.box[1], r.box[2], r.box[3], r.score);
    }

    free(img.buffer);
}
