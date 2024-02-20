from FaceDatabaseManager import FaceDatabaseManager
from FaceRecognizer import FaceRecognizer
from UserInteractionManager import UserInteractionManager
import cv2


class Face_Recognizer_System:
    # Initialize the classes
    print("Initializing the Face Recognizer System")
    database_manager = FaceDatabaseManager()
    database_manager.load_known_faces()
    user_interaction_manager = UserInteractionManager(database_manager)
    face_recognizer = FaceRecognizer(user_interaction_manager)
    face_recognizer.identify_faces()

if __name__ == "__main__":
    # Start the main loop
    Face_Recognizer_System()
    

