# Simple script to have mavproxy search available serial and connect to it

import os
import sys

def find_serial_device():
    # List all devices in /dev directory
    dev_list = os.listdir('/dev')

    # Filter devices that partially match the name requirement
    serial_devices = [dev for dev in dev_list if 'tty.usbmodem1' in dev]

    if serial_devices:
        print(f"Serial device found: {serial_devices[0]}")
        return serial_devices[0]
    else:
        # Relax serial filter
        serial_devices = [dev for dev in dev_list if 'tty.usb' in dev]

    if serial_devices:
        print(f"Serial device found: {serial_devices[0]}")
        return serial_devices[0]
    else:
        print("No matching serial device found.")
        return None

if __name__ == "__main__":
    # Name of the application to launch
    application_to_launch = "your_application"

    serial_device = find_serial_device()
    other_options = ""
    if len(sys.argv) > 1 :
        other_options =  ' '.join(sys.argv[1:])

    if serial_device:
        print(other_options)
        os.system(f"mavproxy.py --master=/dev/{serial_device} --console {other_options}")
    else:
        print("Serial device not found, mavproxy not launched.")
