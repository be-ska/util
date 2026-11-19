#!/usr/bin/env python3
# fmt: off
# Thrust test: ramp PWM via MAV_CMD_DO_MOTOR_TEST and log telemetry per step.
# At each PWM step, wait SETTLE_S to skip current spike, sample BATTERY_STATUS
# and ESC_TELEMETRY_1_TO_4 while user measures thrust, then write averaged row.

import sys
import csv
import time
import threading
import os
from typing import List
from pymavlink import mavutil

# --- Connection ---
SERIAL_PORT = ""
SERIAL_BAUD = 115200

# --- Motor test ---
MOTOR_INDEX = 1            # 1-based motor index
THROTTLE_TYPE = 1          # 1 = PWM, 0 = percent
PWM_START = 1050
PWM_END = 2000
PWM_STEP = 50

# --- Timing ---
SETTLE_S = 2.0             # discard samples for this long after each command
COMMAND_REFRESH_S = 2.0    # re-send motortest periodically to keep motor running
COMMAND_TIMEOUT_S = 5      # motortest timeout (>= COMMAND_REFRESH_S)

CSV_FILE = "thrust_test.csv"

# --- Shared state ---
state_lock = threading.Lock()
samples_rpm: List[float] = []
samples_volt: List[float] = []
samples_curr: List[float] = []
sampling = False
current_pwm = 0
stop_flag = False

def find_serial_device():
    # List all devices in /dev directory
    dev_list = os.listdir('/dev')

    # Filter devices that partially match the name requirement
    serial_devices = [dev for dev in dev_list if 'tty.usbmodem1' in dev]

    if serial_devices:
        print(f"\nSerial device found: {serial_devices[0]}")
        return serial_devices[0]
    else:
        # Relax serial filter
        serial_devices = [dev for dev in dev_list if 'tty.usb' in dev]

    if serial_devices:
        print(f"Serial device found: {serial_devices[0]}")
        return serial_devices[0]
    else:
        return None

def send_motortest(master, pwm: int, timeout_s: int = COMMAND_TIMEOUT_S) -> None:
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,  # confirmation
        MOTOR_INDEX,
        THROTTLE_TYPE,
        pwm,
        timeout_s,
        0, 0, 0,
    )


def stop_motor(master) -> None:
    try:
        master.mav.command_long_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
            0,
            MOTOR_INDEX,
            THROTTLE_TYPE,
            1000 if THROTTLE_TYPE == 1 else 0,
            1,
            0, 0, 0,
        )
    except Exception:
        pass


def receiver_loop(master) -> None:
    while not stop_flag:
        msg = master.recv_match(blocking=True, timeout=0.5)
        if msg is None:
            continue
        mtype = msg.get_type()
        if mtype == "BATTERY_STATUS":
            try:
                v = msg.voltages[0] / 1000.0   # mV -> V
                c = msg.current_battery / 100.0  # cA -> A
            except Exception:
                continue
            with state_lock:
                if sampling:
                    samples_volt.append(v)
                    samples_curr.append(c)
        elif mtype == "ESC_TELEMETRY_1_TO_4":
            try:
                rpm = float(msg.rpm[MOTOR_INDEX - 1])
            except Exception:
                continue
            with state_lock:
                if sampling:
                    samples_rpm.append(rpm)


def keepalive_loop(master) -> None:
    while not stop_flag:
        time.sleep(COMMAND_REFRESH_S)
        pwm = current_pwm
        if pwm > 0 and not stop_flag:
            try:
                send_motortest(master, pwm)
            except Exception:
                pass


def avg(values: List[float]) -> float:
    return sum(values) / len(values) if values else float("nan")


def main():
    global sampling, current_pwm, stop_flag


    if len(sys.argv) > 1:
        port = sys.argv[1] 
    else:
        dev = find_serial_device()
        if dev is None:
            print("No device found")
            return
        port = "/dev/" + dev

    print(f"Connecting to {port} @ {SERIAL_BAUD}...")
    master = mavutil.mavlink_connection(port, baud=SERIAL_BAUD)
    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(f"Connected to system {master.target_system}, component {master.target_component}")

    # Request streams (best effort; some autopilots stream by default)
    try:
        master.mav.request_data_stream_send(
            master.target_system,
            master.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL,
            10,  # Hz
            1,
        )
    except Exception:
        pass

    rx = threading.Thread(target=receiver_loop, args=(master,), daemon=True)
    rx.start()
    ka = threading.Thread(target=keepalive_loop, args=(master,), daemon=True)
    ka.start()

    try:
        input("Press Enter to START the thrust test (Ctrl+C to abort)... ")
    except (KeyboardInterrupt, EOFError):
        stop_flag = True
        print("\nAborted before start.")
        return

    aborted = False
    with open(CSV_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["pwm", "rpm", "volt", "curr", "thrust_gf"])

        try:
            for pwm in range(PWM_START, PWM_END + 1, PWM_STEP):
                # Send command and let it settle (no sampling during spike)
                with state_lock:
                    samples_rpm.clear()
                    samples_volt.clear()
                    samples_curr.clear()
                    sampling = False
                current_pwm = pwm
                send_motortest(master, pwm)
                print(f"\nPWM={pwm}: settling {SETTLE_S:.1f}s ...")
                time.sleep(SETTLE_S)

                # Begin sampling while user measures thrust
                with state_lock:
                    samples_rpm.clear()
                    samples_volt.clear()
                    samples_curr.clear()
                    sampling = True

                raw = input(f"Enter thrust in gf for PWM={pwm} (non-number to stop): ").strip()

                with state_lock:
                    sampling = False
                    rpm_vals = list(samples_rpm)
                    volt_vals = list(samples_volt)
                    curr_vals = list(samples_curr)

                try:
                    thrust = float(raw)
                except ValueError:
                    print("Non-number input -> stopping motor and exiting.")
                    aborted = True
                    break

                rpm_a = avg(rpm_vals)
                volt_a = avg(volt_vals)
                curr_a = avg(curr_vals)
                writer.writerow([
                    pwm,
                    f"{rpm_a:.1f}",
                    f"{volt_a:.3f}",
                    f"{curr_a:.3f}",
                    f"{thrust:.2f}",
                ])
                f.flush()
                print(
                    f"  saved: rpm={rpm_a:.1f} (n={len(rpm_vals)})  "
                    f"volt={volt_a:.3f} (n={len(volt_vals)})  "
                    f"curr={curr_a:.3f} (n={len(curr_vals)})  thrust={thrust:.2f} gf"
                )

        except KeyboardInterrupt:
            print("\nInterrupted by user.")
            aborted = True

    current_pwm = 0
    stop_motor(master)
    stop_flag = True
    time.sleep(0.3)
    print(f"\n{'Aborted' if aborted else 'Done'}. CSV saved to {CSV_FILE}")


if __name__ == "__main__":
    main()
