"""
Handle user notifications and decisions, such as whether to add an unrecognized person to the database.
"""
import os
import face_recognition
from FaceDatabaseManager import FaceDatabaseManager
class UserInteractionManager:
    def __init__(self, database_manager: FaceDatabaseManager):
        self.user_response = False
        self.database_manager = database_manager

    def notify_unrecognized_presence(self, filename):
        print(f"Notification: An unidentified person was detected and saved as {filename}. Please check immediately.")
        user_input = input("Do you want to add this person to the family photos? (True/False)")
        self.user_response = user_input 
        return self.user_response

    def handle_user_decision(self, image_path,user_response):
        """
        Handles the user's decision to add or ignore an unrecognized face.
        """

        if user_response == "True":
            new_path = os.path.join(self.database_manager.known_faces_dir, os.path.basename(image_path))
            os.rename(image_path, new_path)
            image = face_recognition.load_image_file(new_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                self.database_manager.known_face_encodings.append(face_encodings[0])
                self.database_manager.known_face_names.append(os.path.splitext(os.path.basename(new_path))[0])
                print(f"Added new member from {os.path.basename(new_path)} to family photos.")
                print(f"Removed {os.path.basename(image_path)} from unknown faces.")
                
                
        else:
            print("this will trigger the security feature which will be implemented later.")
