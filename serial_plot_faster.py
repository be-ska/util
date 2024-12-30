import sys
import time
import numpy as np
import pyqtgraph as pg
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import serial

# Simulation flag
sim = False

# Set up the serial connection
serial_port = '/dev/tty.usbserial-0001'  # Replace with your port
baud_rate = 115200  # Set the correct baud rate
if not sim:
    ser = serial.Serial(serial_port, baud_rate)
    ser.flushInput()

# Initialize empty lists to store the data
time_data = []
y1_data = []
y2_data = []
y3_data = []

# Start time for x-axis reference
start_time = time.time()

# Create a PyQt application
app = QApplication(sys.argv)

# Set up the plot window
win = pg.GraphicsLayoutWidget(show=True, title="Real-Time Data Plot")
win.resize(800, 600)
win.setWindowTitle('Real-Time Plotting')

# Create a single plot item
plot = win.addPlot(title="Y1 and Y2 Data")

# Initialize the plot curves for both datasets
curve1 = plot.plot(pen='r', name="Y1 Data")  # Red line for Y1 data
curve2 = plot.plot(pen='y', name="Y2 Data")  # Blue line for Y2 data
curve3 = plot.plot(pen='g', name="Y3 Data")  # Blue line for Y2 data

# Update function for real-time plotting
def update():
    global time_data, y1_data, y2_data, y3_data
    try:
        if sim:
            # Simulated data
            numbers = [time.time(), -time.time(), time.time(), time.time() / 2]
        else:
            # Read a line from the serial port
            line = ser.readline().decode('utf-8').strip()
            numbers = [float(x) for x in line.split(',')]

        # Update the lists
        if len(numbers) >= 2:  # Assuming at least two numbers
            current_time = time.time() - start_time
            time_data.append(current_time)
            y1_data.append(numbers[0])
            y2_data.append(numbers[1])
            y3_data.append(numbers[2])

            # Limit data to the last 100 points
            if len(time_data) > 100:
                time_data = time_data[-100:]
                y1_data = y1_data[-100:]
                y2_data = y2_data[-100:]
                y3_data = y3_data[-100:]

            # Update the plot data
            curve1.setData(time_data, y1_data)
            curve2.setData(time_data, y2_data)
            curve3.setData(time_data, y3_data)

    except Exception as e:
        print(f"Error: {e}")

# Timer for updating the plot
timer = QTimer()
timer.timeout.connect(update)
timer.start(50)  # Update every 50 ms for 20 Hz

# Start the PyQt event loop
sys.exit(app.exec_())
