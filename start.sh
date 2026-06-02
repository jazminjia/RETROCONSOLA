#!/bin/bash
# Boot screen sin sudo
python3 /home/pi/retroconsola/src/boot_screen.py

# Menu en HDMI
sudo openvt -s -w -- python3 /home/pi/retroconsola/src/menu_terminal.py
