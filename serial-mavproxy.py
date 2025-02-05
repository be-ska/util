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
    serial_device = find_serial_device()
    other_options = ""
    conection_string = f"--master=/dev/{serial_device}"

    # if the --noserial flag is found, do not pass the serial device to mavproxy
    # and pass the rest of the arguments as is
    if len(sys.argv) > 1 :
        if "--noserial" in sys.argv:
            conection_string = ""
            serial_device = True
            sys.argv.remove("--noserial")
        other_options =  ' '.join(sys.argv[1:])

    if serial_device:
        print(other_options)
        os.system(f"mavproxy.py {conection_string} --console {other_options}")
    else:
        print("Serial device not found, mavproxy not launched.")
