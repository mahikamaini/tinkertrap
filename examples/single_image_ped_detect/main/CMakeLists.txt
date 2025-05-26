idf_component_register(SRCS "detect_single_image.cpp"
                       INCLUDE_DIRS "."
                       REQUIRES pedestrian_detect
                       PRIV_INCLUDE_DIRS /Users/mahikamaini/esp/esp-who-2/examples/single_image_ped_detect/components/pedestrian_detect/esp-dl/models/pedestrian_detect
                       /Users/mahikamaini/esp/esp-who-2/examples/single_image_ped_detect/esp-idf-v5.1.1/components/fatfs/vfs)
