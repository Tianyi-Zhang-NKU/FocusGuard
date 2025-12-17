import cv2
import mediapipe as mp
import sys

print("Python-Version:", sys.version)
print("OpenCV-Version:", cv2.__version__)
print("MediaPipe-Version:", mp.__version__)

print("\nTrying to access the camera...")
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Cannot open camera. Check if it is connected and not used by another application.")
else:
    print("Success! Camera is accessible.")
    print("Trying to read a frame...")
    success, frame = cap.read()
    if success:
        print("Success! A frame was read from the camera.")
        print("Frame dimensions:", frame.shape)
    else:
        print("Error: Could not read a frame from the camera.")
    cap.release()

print("\nTest finished.")

