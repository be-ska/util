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
    serial_device = False
    other_options = ""
    conection_string = ""

    if "--noserial" in sys.argv:
        # if the --noserial flag is found, do not pass the serial device to mavproxy
        sys.argv.remove("--noserial")
    elif "--sitl" in sys.argv:
        # connect to sitl
        conection_string = "--master=tcp:127.0.0.1:5760"
        sys.argv.remove("--sitl")
    else:
        # default try to connect to a serial device, most used case
        serial_device = find_serial_device()
        conection_string = f"--master=/dev/{serial_device}"
        if not serial_device:
            print("Serial device not found, mavproxy not launched.")
            sys.exit(1)

    # choose mavproxy version
    if "--stable" in sys.argv:
        # run mavproxy stable (pip)
        mavproxy = f"~/.pyenv/versions/3.10.3/bin/python ~/.pyenv/versions/3.10.3/bin/mavproxy.py"
        sys.argv.remove("--stable")
    else:
        # run mavproxy master
        mavproxy = f"~/.pyenv/versions/3.13.0/bin/python ~/code/MAVProxy/MAVProxy/mavproxy.py"

    # pass the rest of the arguments as is
    if len(sys.argv) > 1 :
        other_options =  ' '.join(sys.argv[1:])

    # run mavproxy
    os.system(f"{mavproxy} {conection_string} --console {other_options}")
