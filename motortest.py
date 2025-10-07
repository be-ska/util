#!/usr/bin/env python3
# fmt: off
# send motortest command using pymavlink
import sys
import time
import signal
from typing import Optional
from pymavlink import mavutil

# Motor test parameters:
# param1: motor index (1-8 for specific motor, or 0 for all depending on firmware)
# param2: throttle type (0 = percent, 1 = PWM)
# param3: throttle value (percent 0-100 or PWM 1000-2000)
# param4: timeout (seconds)
# param5-7: unused (0)

MOTOR_INDEX = 1               # change if you need a different motor
THROTTLE_TYPE = 1             # 1 = PWM, 0 = Percent
PWM_MIN = 1000
PWM_MAX = 2000
PERCENT_MIN = 0
PERCENT_MAX = 100
DEFAULT_TIMEOUT_S = 20

running = True


def send_motortest(
    master: mavutil.mavlink_connection,
    value: int,
    timeout_s: int = DEFAULT_TIMEOUT_S,
    motor_index: int = MOTOR_INDEX,
    throttle_type: int = THROTTLE_TYPE,
) -> None:
    """
    Send MAV_CMD_DO_MOTOR_TEST with given value (PWM or Percent per throttle_type).
    """
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,  # confirmation
        motor_index,
        throttle_type,
        value,
        timeout_s,
        0,
        0,
        0,
    )
    # Try to receive COMMAND_ACK (non-fatal if not received)
    try:
        ack = master.recv_match(type="COMMAND_ACK", blocking=True, timeout=1.0)
        if ack and getattr(ack, "command", None) == mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST:
            result = ack.result
            if result != mavutil.mavlink.MAV_RESULT_ACCEPTED:
                print(f"Warning: COMMAND_ACK result={result} (not accepted)")
    except Exception:
        # Ignore ack issues for robustness
        pass


def validate_value(raw: str) -> Optional[int]:
    """
    Validate and convert input string to an int within allowed range
    based on THROTTLE_TYPE. Returns None if invalid.
    """
    try:
        val = int(raw)
    except ValueError:
        return None

    if THROTTLE_TYPE == 1:
        if PWM_MIN <= val <= PWM_MAX:
            return val
    else:
        if PERCENT_MIN <= val <= PERCENT_MAX:
            return val
    return None


def stop_motor(master: mavutil.mavlink_connection) -> None:
    """
    Send safe stop command (0% or PWM_MIN) with short timeout.
    """
    if THROTTLE_TYPE == 1:
        value = PWM_MIN
    else:
        value = 0
    try:
        send_motortest(master, value, timeout_s=1)
    except Exception:
        pass


def usage():
    mode = "PWM 1000-2000" if THROTTLE_TYPE == 1 else "percent 0-100"
    print(
        "Usage:\n"
        "  python motortest.py                 # interactive mode\n"
        "  python motortest.py --loop [VAL]    # loop mode; optional value\n"
        f"Notes: Input range is {mode} (THROTTLE_TYPE={THROTTLE_TYPE})."
    )


def main():
    global running

    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        usage()
        return

    # Create the connection
    # run mavproxy with argument: --out=udp:localhost:14551
    master = mavutil.mavlink_connection("udp:localhost:14551")
    print("Waiting for heartbeat...")
    master.wait_heartbeat()
    print(
        f"Connected to system {master.target_system}, component {master.target_component}"
    )

    # Loop mode: either fixed value provided or keep sending a default
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        print("Entering loop mode. Press Ctrl+C to stop.")
        val = 0
        while True:
            try:
                val = val + 10
                send_motortest(master, val, timeout_s=3, throttle_type=0)
                # Sleep slightly less than timeout to keep it alive
                time.sleep(2)
                if val >= 100:
                    val = 0

            except KeyboardInterrupt:
                break

        stop_motor(master)
        print("Exited loop mode.")
        return

    # Interactive mode
    rng_label = (
        f"{PWM_MIN}-{PWM_MAX} (PWM)"
        if THROTTLE_TYPE == 1
        else f"{PERCENT_MIN}-{PERCENT_MAX} (percent)"
    )
    print("Interactive mode. Type 'q' to quit.")
    while True:
        try:
            user_input = input(f"Enter throttle value {rng_label}: ").strip()
            if user_input.lower() in {"q", "quit", "exit"}:
                break

            val = validate_value(user_input)
            if val is None:
                print(f"Invalid input. Enter {rng_label}.")
                stop_motor(master)
                continue

            # Use a shorter timeout so it stops soon after next command
            send_motortest(master, val)

        except KeyboardInterrupt:
            print("\nStopping motor")
            break
        except EOFError:
            # e.g., Ctrl+D
            break
        except Exception as e:
            print(f"Error: {e}")

    stop_motor(master)
    print("Done.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Double-safety on abrupt exit outside main loop
        try:
            # Best-effort connection to stop motor if possible
            master = mavutil.mavlink_connection("udp:localhost:14551")
            master.wait_heartbeat(timeout=1)
            stop_motor(master)
        except Exception:
            pass
        print("\nExited.")
