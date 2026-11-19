# Simple script to have mavproxy search available serial and connect to it

import os
import sys
import time

def find_serial_device():
    # List all devices in /dev directory
    dev_list = os.listdir('/dev')

    # Filter devices that partially match the name requirement
    serial_devices = [dev for dev in dev_list if 'tty.usbmodem1' in dev]
    serial_devices_relaxed = [dev for dev in dev_list if 'tty.usb' in dev]
    serial_port = ""

    if serial_devices:
        serial_port = serial_devices[0]
    elif "tty.usbserial-58930108011" in serial_devices_relaxed:
        # RFD868 found, default at 115200 baud
        serial_port = "tty.usbserial-58930108011,115200"
    elif serial_devices_relaxed:
        serial_port = serial_devices_relaxed[0]
    else:
        return None

    print(f"Serial device found: {serial_port}")
    return serial_port

if __name__ == "__main__":
    serial_device = False
    other_options = ""
    connection_string = ""

    if "--noserial" in sys.argv:
        # if the --noserial flag is found, do not pass the serial device to mavproxy
        sys.argv.remove("--noserial")
    elif "--sitl" in sys.argv:
        # connect to sitl
        connection_string = "--master=tcp:127.0.0.1:5760 --load-module horizon,map,graph"
        sys.argv.remove("--sitl")
    else:
        # default try to connect to a serial device, most used case
        start_time = time.time()
        serial_device = find_serial_device()
        print("Wait for serial device")
        while not serial_device and time.time() - start_time < 100:
            print(".", end="", flush=True)
            time.sleep(1)
            serial_device = find_serial_device()
        if not serial_device:
            print("Serial device not found, mavproxy not launched.")
            sys.exit(1)
        connection_string = f"--master=/dev/{serial_device} --load-module graph,message"
        print(f"Run mavproxy with arguments: {connection_string}")

    # run mavproxy master
    mavproxy = "mavproxy.py"

    # pass the rest of the arguments as is
    if len(sys.argv) > 1 :
        other_options =  ' '.join(sys.argv[1:])

    # run mavproxy
    os.system(f"{mavproxy} {connection_string} --console {other_options}")
