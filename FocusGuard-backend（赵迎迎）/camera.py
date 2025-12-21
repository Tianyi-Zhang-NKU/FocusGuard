# backend/camera.py
import cv2
import threading
import time


class Camera:
    def __init__(self, src=0):
        self.src = src
        self.cap = None
        self.running = False
        self.thread = None
        self.lock = threading.Lock()
        self.latest_frame = None

    def start(self):
        if self.running:
            return

        print("📷 Opening camera:", self.src)
        self.cap = cv2.VideoCapture(self.src, cv2.CAP_DSHOW)

        if not self.cap.isOpened():
            raise RuntimeError("❌ Cannot open camera")

        self.running = True
        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )
        self.thread.start()

        print("✅ Camera thread started")

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret and frame is not None:
                with self.lock:
                    self.latest_frame = frame
            else:
                time.sleep(0.03)

        self.cap.release()
        print("📷 Camera released")

    def read(self):
        with self.lock:
            if self.latest_frame is None:
                return None
            return self.latest_frame.copy()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)
