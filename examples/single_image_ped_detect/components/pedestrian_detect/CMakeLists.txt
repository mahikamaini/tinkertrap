idf_component_register(SRCS "esp-dl/models/pedestrian_detect/pedestrian_detect.cpp"
                       INCLUDE_DIRS "" 
                       PRIV_INCLUDE_DIRS "${CMAKE_BINARY_DIR}/config"
                       REQUIRES esp-dl)
