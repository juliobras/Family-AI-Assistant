import cv2
import threading
import copy
# class SharedLaptopCamera:
#     def __init__(self):
#         # Initialize the camera
#         self.cap = cv2.VideoCapture(0)  # 0 for the default camera
#         self.current_frame = None
#         self.running = True
        

#         # Start the background camera thread
#         threading.Thread(target=self.update_frame, args=(), daemon=True).start()
      
#         self.frame_lock = threading.Lock()


#     def get_frame(self):
#         with self.frame_lock:
#             # Return a deep copy of the frame to ensure it doesn't get modified
#             return copy.deepcopy(self.current_frame)
        
#     def update_frame(self):
#         while self.running:
#             ret, frame = self.cap.read()
#             if ret:
#                 with self.frame_lock:
#                     self.current_frame = frame

#     """def get_frame(self):
#         with self.frame_lock:
#             return self.current_frame"""

#     def stop_camera(self):
#         self.running = False
#         self.cap.release()

# # You can instantiate this class in your app.py and import it where needed.
import cv2
from threading import Thread
from queue import Queue

class Camera:
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.cap = cv2.VideoCapture(camera_id)
        self.q = Queue(maxsize=1)  # Ensuring only one frame is in the queue
        self.running = True
        self.thread = Thread(target=self._capture_loop)
        self.thread.start()

    def _capture_loop(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                if not self.q.empty():
                    self.q.get()  # Remove the old frame
                self.q.put(frame)

    def get_frame(self):
        return self.q.get() if not self.q.empty() else None

    def release(self):
        self.running = False
        if self.thread.is_alive():
            self.thread.join()
        self.cap.release()

class CameraManager:
    def __init__(self, camera_ids):
        self.cameras = {cid: Camera(cid) for cid in camera_ids}

    def get_frame(self, camera_id):
        return self.cameras[camera_id].get_frame() if camera_id in self.cameras else None

    def release_all(self):
        for camera in self.cameras.values():
            camera.release()

if __name__ == "__main__":
    camera_manager = CameraManager([0, 1,2])  # Initialize with your camera IDs

    try:
        while True:
            for cam_id in camera_manager.cameras:
                frame = camera_manager.get_frame(cam_id)
                if frame is not None:
                    cv2.imshow(f'Camera {cam_id}', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):  # Break the loop if 'q' is pressed
                break
    finally:
        camera_manager.release_all()
        cv2.destroyAllWindows()
