from FaceDatabaseManager import FaceDatabaseManager
from FaceRecognizer import FaceRecognizer
from UserInteractionManager import UserInteractionManager
import threading
from Camera import SharedLaptopCamera

shared_camera = SharedLaptopCamera()

class Face_Recognizer_System:
    def __init__(self):
        print("Initializing the Face Recognizer System")
        self.database_manager = FaceDatabaseManager()
        self.database_manager.load_known_faces()
        self.user_interaction_manager = UserInteractionManager(self.database_manager)
        self.face_recognizer = FaceRecognizer(self.user_interaction_manager,shared_camera)
        self.recognizer_thread = threading.Thread(target=self.face_recognizer.identify_faces)
        self.recognizer_thread.start()


    def monitor_recognized_people(self):
        #while True:
            current_people = list(self.face_recognizer.currently_recognized_queue.queue)

            #time.sleep(5)  # Check every 10 seconds
          
            return current_people


if __name__ == "__main__":
     Face_Recognizer_System()

    
    

