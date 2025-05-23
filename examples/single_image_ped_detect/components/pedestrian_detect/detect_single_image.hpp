#pragma once

#ifdef __cplusplus
extern "C" void app_main(void)
{
    run_single_image_detection("/sdcard/test.rgb");
}
#endif

void run_single_image_detection(const char *image_path);

#ifdef __cplusplus
}
#endif
