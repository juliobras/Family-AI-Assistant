"""
This class would be responsible for interacting with the file system to load known faces and save images of unrecognized faces.
"""
import cv2
import os
import face_recognition
from datetime import datetime
class FaceDatabaseManager:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.known_faces_dir="src/user_recognition/family_member_photos"
        self.unknown_faces_dir="src/user_recognition/unknown_faces"

    def load_known_faces(self):
        name_set = set()  # To keep track of names already loaded
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # Process name: strip numerical suffixes after a standard identifier (e.g., "Julio1" becomes "Julio")
                name = os.path.splitext(filename)[0]  # Remove file extension
                base_name = ''.join(filter(str.isalpha, name))  # Remove numeric characters
                image_path = os.path.join(self.known_faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    # Only add new encodings if the base name has not been added before
                    if base_name not in name_set:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(base_name)  # Use the base name without numbers
                        name_set.add(base_name)  # Remember that we've added this person

    def save_unrecognized_face(self, frame, location):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        top, right, bottom, left = location
        face_image = frame[top:bottom, left:right]
        filename = f"unidentified_person-{timestamp}.jpg"
        file_path = os.path.join(self.unknown_faces_dir, filename)
        cv2.imwrite(file_path, face_image)
        print(f"Saved an image of an unidentified person as {filename}")
        return file_path
    
  
