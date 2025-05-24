cmake_minimum_required(VERSION 3.5)

set(EXTRA_COMPONENT_DIRS ../../components/who_task
                         ../../components/who_peripherals/who_cam
                         ../../components/who_peripherals/who_lcd
                         ../../components/who_frame_cap
                         ../../components/who_detect
                         ../../components/who_app/who_detect_app
                         components/pedestrian_detect
                         components/pedestrian_detect/esp-dl/models/pedestrian_detect)  


include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(single_image_ped_detect)
