import cv2
import threading

class SharedLaptopCamera:
    def __init__(self):
        # Initialize the camera
        self.cap = cv2.VideoCapture(0)  # 0 for the default camera
        self.current_frame = None
        self.running = True
        self.lock = threading.Lock()  # Protect concurrent access to current_frame

        # Start the background camera thread
        threading.Thread(target=self.update_frame, args=(), daemon=True).start()

    def update_frame(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.lock:
                    self.current_frame = frame

    def get_frame(self):
        with self.lock:
            return self.current_frame

    def stop_camera(self):
        self.running = False
        self.cap.release()

# You can instantiate this class in your app.py and import it where needed.
