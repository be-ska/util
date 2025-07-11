# send motortest command using pymavlink
import time
from pymavlink import mavutil
import sys

# write me a motortest helper function that send the mavlink message, pwm as argument

def send_motortest(master, throttle_value):
    master.mav.command_long_send(
        master.target_system,
        master.target_component,
        mavutil.mavlink.MAV_CMD_DO_MOTOR_TEST,
        0,  # Confirmation
        1,  # Motor index (1-8)
        1,  # Throttle type (0=Percentage, 1=PWM)
        throttle_value,  # Throttle value 
        20,  # Timeout in seconds
        0, 0, 0, 0  # Unused parameters
    )
    

# Create the connection
# run mavproxy with argument: --out=udp:localhost:14551
master = mavutil.mavlink_connection('udp:localhost:14551')
master.wait_heartbeat()

# if argument is --loop cycle between 0 and 100
if len(sys.argv) > 1 and sys.argv[1] == '--loop':
    while True:
        # Send the motor test command
        send_motortest(master, 100)
        time.sleep(20)

# else wait the percentage input from user and send it
else:
    while True:
        user_input = input("Enter throttle value (1000-2000): ")
        try:
            throttle_value = int(user_input)
            # prevent typos
            if throttle_value < 1000 or throttle_value > 2200:
                print("Invalid input. Please enter a number between 0 and 100.")
                throttle_value = 0
        except ValueError:
            # stop motor if value error
            print("Invalid input. Please enter a number between 0 and 100.")
            throttle_value = 0
        send_motortest(master, throttle_value)

