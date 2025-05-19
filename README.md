# TinkerTrap Notebook
## Tuesday, May 13, 2025
### Task
Set up ESP-IDF code environment in VSCode on my Mac. 
### Notes
In order to test if the code runs, the ESP-IDF will need to be plugged into my laptop. This should arrive by the end of the week. 
### What I Accomplished
I followed a provided video tutorial to integrate the necessary software with the ESP-IDF VSCode extension. While it was meant for Windows, I was able to successfully integrate it with MacOS. I also cloned the GitHub repository for the ESP-IDF code, including the pedestrian-detect sample we will be using, and created a new repository, TinkerTrap, for our purposes. 

## Wednesday, May 14, 2025
### Task
Read through and understand the pedestrian_detect example code from the original GitHub repository.
### Notes
I commented all observations in the app_main.cpp file under the pedestrian_detect folder.
### What I Accomplished
I read through the example code and broke it down to understand its functionality. While I don't have a background in C++, I utilized the Espressif API and ChatGPT to break down some of the syntax in order to better understand the logical function. As a result, I'm a little more familiar with the code function, though not necessarily how to adapt it to our specific purpose quite yet. 

## Monday, May 19, 2025
### Task
Plug in and set up the ESP32-S3 device. 
### Notes
The device requires a USB-A to micro-USB cable, not a USB-A to USB-C cable. 
### What I Accomplished
I was able to install the necessary UART drivers on my laptop and obtain a USB-A to micro-USB cable. From there, I connected the ESP32 to my laptop and successfully flashed some of the example scripts to it. With Ben, we also discussed how to best adapt the existing pedestrian_detect code to apply to single images rather than a continuous video feed using ChatGPT as a guide. 