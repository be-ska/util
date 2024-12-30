import serial
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import time

# Set up the serial connection
sim = True
serial_port = '/dev/tty.usbserial-0001'  # Replace with your port
baud_rate = 115200  # Set the correct baud rate
if not sim:
    ser = serial.Serial(serial_port, baud_rate)
    ser.flushInput()

# Initialize empty lists to store the data
time_data = []
y1_data = []
y2_data = []

# Start time for x-axis reference
start_time = time.time()

# Function to read and update data
def update(frame):
    global time_data, y1_data, y2_data
    try:
        if (sim):
            numbers = [time.time(), -time.time(), time.time(), time.time()/2]
            print(time.time())
        else:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            # Split the line into float numbers
            numbers = [float(x) for x in line.split(',')]

        # Update the lists
        if len(numbers) == 4:  # Assuming two numbers
            current_time = time.time() - start_time
            time_data.append(current_time)
            y1_data.append(numbers[0])
            y2_data.append(numbers[1])

            # Limit data to the last 100 points
            if len(time_data) > 100:
                time_data = time_data[-100:]
                y1_data = y1_data[-100:]
                y2_data = y2_data[-100:]

        # Clear the current plot and plot the new data
        # ax1.cla()
        # ax2.cla()
        
        # Plot the first dataset
        ax1.plot(time_data, y1_data, 'r-', label="Y1 Data")
        # ax1.set_xlabel("Time (s)")
        # ax1.set_ylabel("Y1 Values", color='r')
        # ax1.tick_params(axis='y', labelcolor='r')
        
        # Plot the second dataset
        ax2.plot(time_data, y2_data, 'b-', label="Y2 Data")
        # ax2.set_ylabel("Y2 Values", color='b')
        # ax2.tick_params(axis='y', labelcolor='b')
    except Exception as e:
        print(f"Error: {e}")

# Set up the plot
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()  # Create a second y-axis
ani = animation.FuncAnimation(fig, update, interval=50)

# Show the plot
plt.show()

# Close the serial port when done
ser.close()
