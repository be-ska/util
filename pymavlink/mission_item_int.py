from pymavlink import mavutil
import time

def connect_to_sitl(connection_string="tcp:127.0.0.1:5762"):
    """Connect to ArduPilot SITL."""
    print(f"Connecting to SITL at {connection_string}...")
    master = mavutil.mavlink_connection(connection_string)
    master.wait_heartbeat()
    print("Heartbeat received. Connected to SITL.")
    return master

def send_mission_item_int(master, seq, x, y, z, command=mavutil.mavlink.MAV_CMD_NAV_WAYPOINT, frame=mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, autocontinue=True):
    """Send a single MISSION_ITEM_INT message."""
    master.mav.mission_item_int_send(
        master.target_system,  # Target system ID
        master.target_component,  # Target component ID
        seq,  # Sequence number
        frame,  # MAV_FRAME
        command,  # Command
        0,  # Current (not used in SITL for mission items)
        int(autocontinue),  # Autocontinue
        0, 0, 0, 0,  # Params 1-4
        int(x * 1e7),  # Latitude (degrees * 1e7)
        int(y * 1e7),  # Longitude (degrees * 1e7)
        z  # Altitude (meters)
    )
    print(f"Sent MISSION_ITEM_INT seq {seq} to ({x}, {y}, {z}).")

def send_mission_sequence(master, mission_items):
    """Send a sequence of mission items to SITL."""
    print("Sending mission count...")
    # master.mav.mission_count_send(master.target_system, master.target_component, len(mission_items))

    for i, item in enumerate(mission_items):
        # msg = master.recv_match(type='MISSION_REQUEST', blocking=True)
        # if msg.seq == i:
            send_mission_item_int(master, i, *item)

    print("Mission items sent.")

def print_text_messages(master):
    """Continuously print any received text messages."""
    print("Listening for text messages...")
    while True:
        msg = master.recv_match(type='STATUSTEXT', blocking=True)
        if msg:
            print(f"[STATUSTEXT] {msg.text}")

def main():
    # Connect to SITL
    master = connect_to_sitl()

    # Define mission items as tuples of (latitude, longitude, altitude)
    mission_items = [
        (47.397742, 8.545594, 10),  # Waypoint 1
        (47.397872, 8.545788, 15),  # Waypoint 2
        (47.397942, 8.545200, 20),  # Waypoint 3
        (47.397742, 8.545594, 10),  # Waypoint 1
        (47.397872, 8.545788, 15),  # Waypoint 2
        (47.397942, 8.545200, 20),  # Waypoint 3
        (47.397742, 8.545594, 10),  # Waypoint 1
        (47.397872, 8.545788, 15),  # Waypoint 2
        (47.397942, 8.545200, 20),  # Waypoint 3
        (47.397742, 8.545594, 10),  # Waypoint 1
        (47.397872, 8.545788, 15),  # Waypoint 2
        (47.397942, 8.545200, 20),  # Waypoint 3
    ]

    # Send the mission items
    send_mission_sequence(master, mission_items)

    print("Mission uploaded successfully.")

    # Start listening for text messages
    print_text_messages(master)

if __name__ == "__main__":
    main()
