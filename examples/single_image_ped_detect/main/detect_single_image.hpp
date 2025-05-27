#ifdef __cplusplus
extern "C" {
#endif

void run_single_image_detection(const char *image_path);
void app_main(void);

#ifdef __cplusplus
}
#endif

void app_main(void)
{
    run_single_image_detection("/sdcard/test.rgb");
}