import cv2
import threading
import copy

class SharedLaptopCamera:
    def __init__(self):
        """
        Initializes the SharedLaptopCamera instance.
        This sets up the camera resource, starts the background thread for updating the frame,
        and initializes the lock for thread-safe frame access.
        """
        # Initialize the camera capture device.
        self.cap = cv2.VideoCapture(0)  # 0 for the default camera
        self.current_frame = None
        self.running = True
        
        # Thread lock for synchronizing access to the current frame.
        self.frame_lock = threading.Lock()

        # Start the background camera thread to continuously update the frame.
        threading.Thread(target=self.update_frame, daemon=True).start()
        
    def get_frame(self):
        """
        Retrieves the latest frame captured by the camera.

        Returns:
            A deep copy of the current frame to ensure the original frame is not modified elsewhere.
        """
        with self.frame_lock:
            return copy.deepcopy(self.current_frame)
        
    def update_frame(self):
        """
        Background thread method to continuously update the current frame from the camera.
        This method runs in a loop as long as the 'running' flag is True.
        """
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                with self.frame_lock:
                    # Update the current frame with the latest from the camera.
                    self.current_frame = frame

    def stop_camera(self):
        """
        Stops the camera capture by ending the frame update loop and releasing the camera resource.
        """
        self.running = False
        self.cap.release()


