import serial
import time
import struct

start_time = 0

def get_time_in_ms():
    # Get current time in milliseconds (as uint32_t)
    now = time.time()
    return int((now - start_time) * 1000) & 0xFFFFFFFF  # Mask to ensure it's 32 bits

def calculate_crc_mpeg2(data):
    """Calculates MPEG2 CRC32"""
    crc = 0xFFFFFFFF
    poly = 0x04C11DB7

    # Append 0x00 to data until its length is divisible by 4
    while len(data) % 4 != 0:
        data += b'\x00'

    for byte in data:
        crc ^= (byte << 24)
        for _ in range(8):
            if crc & 0x80000000:
                crc = (crc << 1) ^ poly
            else:
                crc <<= 1
        crc &= 0xFFFFFFFF  # Keep CRC to 32 bits

    return crc

def create_packet_heartbeat():
    # Packet structure
    header1 = 0x77
    operation = 0xAC
    length = 0x08
    sender_id = 0x01
    receiver_id = 0x00
    packet_id = 0x01  # Heartbeat

#   State:
#       FC_RateMode         = 0     1 long red blink
#       FC_RateSafeMode     = 1     1 long red blink
#       FC_AttitudeMode     = 2     1 fast green blink
#       FC_AltitudeMode     = 3     2 fast green blink
#       FC_GPSRateMode      = 4     3 fast green blink
#       FC_GPSWaypointMode  = 5     4 fast green blink
#       FC_GPSWP_ABMode     = 6     1 long red blink
#       FC_GoHomeMode       = 7     2 fast red blink
#       FC_FailSafeMode     = 8     2 fast red blink
#       FC_SettingMode      = 9     1 fast red blink
#       FC_CalibrationMode  = 10    3 fast orange blink
#
#   Error:
#       0   Flight Controller green - GPS green
#       4   Flight Controller green - GPS red
#       no packet: all red

    state = 10
    error = 0
    uav = 0

    # Get current time in ms
    current_time_ms = get_time_in_ms() 
    current_time_ms = 0

    payload = struct.pack('<I', current_time_ms) + bytes([error, 0x00, state, uav])

    # Build the packet without the CRC
    packet = struct.pack('BBBBBB', header1, operation, length, sender_id, receiver_id, packet_id) + payload

    # Calculate CRC (from byte 2 to last payload byte)
    crc_data = packet[1:]  # Starting from byte 2
    crc = calculate_crc_mpeg2(crc_data)

    # Append CRC to the packet (4 bytes in little-endian format)
    packet += struct.pack('<I', crc)

    return packet

def create_radio_packet():
    # Second packet structure (radio controller data)
    header1 = 0x77
    operation = 0xAC
    length = 0x50  # Length = 80 in decimal (0x50 in hex)
    sender_id = 0x01
    receiver_id = 0x00
    packet_id = 0x10  # Radio controller data (16 in decimal, 0x10 in hex)
    
    # Payload: all 0x00, with length = 80
    payload = bytes([0x05] * 80)
    
    # Build the packet
    packet = struct.pack('BBBBBB', header1, operation, length, sender_id, receiver_id, packet_id) + payload

    # Calculate CRC (from byte 2 to last payload byte)
    crc_data = packet[1:]  # Starting from byte 2
    crc = calculate_crc_mpeg2(crc_data)

    # Append CRC to the packet (4 bytes in little-endian format)
    packet += struct.pack('<I', crc)

    return packet

def create_gcs_heartbeat_packet():
    # Third packet structure (Packet ID 19, Length 10, all payload 0)
    header1 = 0x77
    operation = 0xAC
    length = 0x08  # Length = 8
    sender_id = 0xFF # APP
    receiver_id = 0x00
    packet_id = 0x01  # Packet ID 1
    
    # Payload: all 0x00, with length = 8
    payload = bytes([0x00] * 8)

    # Build the packet
    packet = struct.pack('BBBBBB', header1, operation, length, sender_id, receiver_id, packet_id) + payload

    # Calculate CRC (from byte 2 to last payload byte)
    crc_data = packet[1:]  # Starting from byte 2
    crc = calculate_crc_mpeg2(crc_data)

    # Append CRC to the packet (4 bytes in little-endian format)
    packet += struct.pack('<I', crc)

    return packet

def create_radio_data_packet():
    # Fourth packet structure (Packet ID 3, Length 32, all payload 0)
    header1 = 0x77
    operation = 0xAC
    length = 0x20  # Length = 32 in decimal (0x20 in hex)
    sender_id = 0x01
    receiver_id = 0x00
    packet_id = 0x03  # Packet ID 3 (0x03 in hex)
    
    # Payload: all 0x00, with length = 32
    payload = bytes([0x02] * 32)
    
    # Build the packet
    packet = struct.pack('BBBBBB', header1, operation, length, sender_id, receiver_id, packet_id) + payload

    # Calculate CRC (from byte 2 to last payload byte)
    crc_data = packet[1:]  # Starting from byte 2
    crc = calculate_crc_mpeg2(crc_data)

    # Append CRC to the packet (4 bytes in little-endian format)
    packet += struct.pack('<I', crc)

    return packet

def create_custom_packet_1():
    # Custom packet structure as specified
    
    custom_packet = bytes([0x77,0xAC,0x08,0xFF,0x00,0x01,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0xC1,0x14,0x2C,0x85])
    
    # Return the custom packet
    return custom_packet

def send_packet(serial_port):
    # Open serial port
    with serial.Serial(serial_port, 115200, timeout=1) as ser:
        first = True
        while(True):
            heartbeat = create_packet_heartbeat()
            gcs_heartbeat = create_gcs_heartbeat_packet()
            if first:
                print(f"Sending packet heartbeat: {heartbeat.hex()}\n")
                first = False
            ser.write(heartbeat)
            time.sleep(0.5)
            ser.write(gcs_heartbeat)
            time.sleep(0.1)
            

if __name__ == "__main__":
    start_time = time.time()
    # Replace 'COM3' with your serial port name (e.g., '/dev/ttyUSB0' on Linux)
    try:
        send_packet('/dev/tty.usbserial-57490134651')
    except KeyboardInterrupt:
        print("Exiting.")