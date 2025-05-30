# In /Users/mahikamaini/esp/esp-who-2/examples/single_image_ped_detect/main/CMakeLists.txt
idf_component_register(SRCS "detect_single_image.cpp"
                     INCLUDE_DIRS "."
                     REQUIRES
                         who_detect_app        # Assuming this provides WhoApplication and PedestrianDetect interfaces
                         pedestrian_detect     # As before
                         esp_driver_jpeg       # For JPEG decoding
                         esp_lcd               # For LCD basic types/functions if needed directly
                         sdmmc                 # For SD card
                         fatfs                 # For File system
                         esp_psram
                    )