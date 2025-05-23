idf_component_register(SRCS "detect_single_image.cpp"
                       INCLUDE_DIRS "." 
                       PRIV_INCLUDE_DIRS "${CMAKE_BINARY_DIR}/config"
                       REQUIRES pedestrian_detect)