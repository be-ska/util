import cv2
import numpy as np
import time

# --- Global State Variables ---
trackers = []  # List to store trackers
drawing = False  # Flag to indicate whether the user is drawing a rectangle
start_point = None  # Starting point of the rectangle
end_point = None  # Ending point of the rectangle
bounding_box = None  # Latest bounding box to initialize a tracker

# --- Mouse Callback for Drawing Bounding Boxes ---
def click_and_draw(event, x, y, flags, param):
    global drawing, start_point, end_point, bounding_box

    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        start_point = (x, y)
        end_point = (x, y)

    elif event == cv2.EVENT_MOUSEMOVE and drawing:
        end_point = (x, y)

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        end_point = (x, y)
        # Define the bounding box
        x0, y0 = start_point
        x1, y1 = end_point
        w, h = abs(x1 - x0), abs(y1 - y0)
        if w > 10 and h > 10:
            bounding_box = (min(x0, x1), min(y0, y1), w, h)
            print(f"New bounding box defined: {bounding_box}")
        else:
            print("Bounding box too small, ignored.")


# --- Video Setup ---
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise IOError("Cannot open webcam")

cv2.namedWindow("Tracking")
cv2.setMouseCallback("Tracking", click_and_draw)

# --- Main Loop ---
while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # Initialize a new tracker when a new box is defined
    if bounding_box is not None:
        # Use legacy tracker if needed
        try:
            tracker = cv2.legacy.TrackerCSRT_create()
        except AttributeError:
            tracker = cv2.TrackerCSRT_create()  # For older OpenCV versions

        tracker.init(frame, bounding_box)
        trackers.append(tracker)
        bounding_box = None  # Reset after adding tracker

    # Draw the rectangle while drawing
    if drawing and start_point and end_point:
        cv2.rectangle(frame, start_point, end_point, (255, 0, 0), 2)

    # Update and visualize all trackers
    for i, tracker in enumerate(trackers):
        ok, bbox = tracker.update(frame)
        if ok:
            (x, y, w, h) = [int(v) for v in bbox]
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(
                frame,
                f"Tracker {i+1}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1,
            )
        else:
            cv2.putText(
                frame,
                f"Tracking failure {i+1}",
                (100, 80 + 30 * i),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 0, 255),
                2,
            )

    cv2.imshow("Tracking", frame)

    key = cv2.waitKey(1) & 0xFF

    if key == ord("d") and trackers:
        trackers.pop()
        print("Removed last tracker")

    elif key == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
