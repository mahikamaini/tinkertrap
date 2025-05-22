cmake_minimum_required(VERSION 3.5)

set(ENV{IDF_PATH} "/Users/mahikamaini/esp/esp-idf-v5.1.1")  # Add this line manually

include($ENV{IDF_PATH}/tools/cmake/project.cmake)
project(single_image_ped_detect)
