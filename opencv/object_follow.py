import cv2
import numpy as np
import time

# Global variables
trackers = []  # List to store trackers
drawing = False  # Flag to indicate whether the user is drawing a rectangle
start_point = (0, 0)  # Starting point of the rectangle
end_point = (0, 0)  # Ending point of the rectangle
bounding_box = None

def click_and_draw(event, x, y, flags, param):
    global drawing, start_point, end_point
    if event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            end_point = (x, y)  # Update the end point while moving the mouse
        else:
            start_point = (x, y)

# Create a window and set the mouse callback function
cv2.namedWindow('Tracking')
cv2.setMouseCallback('Tracking', click_and_draw)

# Initialize the video capture object
cap = cv2.VideoCapture(0)

while True:
    # Capture a new frame
    ret, frame = cap.read()
    
    if not ret or frame is None:
        print("Failed to grab frame.")
        break  # Break the loop if the frame capture fails

    # Initialize the tracker only when the rectangle is drawn
    if bounding_box is not None:
        tracker = cv2.TrackerCSRT_create()  # Use CSRT tracker for better accuracy
        if ret:
            tracker.init(frame, bounding_box)  # Initialize the tracker with the drawn rectangle
            trackers.append(tracker)  # Add the tracker to the list
            bounding_box = None # Restore bounding box

    # Draw the rectangle if it is being drawn
    if drawing:
        cv2.rectangle(frame, start_point, end_point, (255, 0, 0), 2)  # Draw the rectangle on the frame

    # Update all trackers
    for i, tracker in enumerate(trackers):
        ok, bbox = tracker.update(frame)
        if ok:
            (x, y, w, h) = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2, 1)
        else:
            # If tracking failed, display a failure message
            cv2.putText(frame, f"Tracking failure {i + 1}", (100, 80 + 30 * i), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 0, 255), 2)

    # Display the frame with tracking information
    cv2.imshow('Tracking', frame)

    # Check if a key is pressed
    key = cv2.waitKey(1)
    # Set start and stop point
    if key == ord('s'):
        if drawing:
            drawing = False # Stop drawing
            if abs((end_point[0] - start_point[0]) * (end_point[1] - start_point[1])) > 30:
                bounding_box = (start_point[0], start_point[1], end_point[0] - start_point[0], end_point[1] - start_point[1])  # Set the bounding box
                print(f'Detected bounding box: {bounding_box}')
            else:
                print("Bounding Box too small")
        else:
            drawing = True  # Start drawing
            end_point = start_point
    # Delete last tracker if 'd' is pressed
    if key == ord('d'):
        if trackers:
            trackers.pop()
    # Break the loop if the 'q' key is pressed
    if key == ord('q'):
        break

# Release the capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()
