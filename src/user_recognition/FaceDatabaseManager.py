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
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(self.known_faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])

    def save_unrecognized_face(self, frame, location):
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        top, right, bottom, left = location
        face_image = frame[top:bottom, left:right]
        filename = f"unidentified_person-{timestamp}.jpg"
        file_path = os.path.join(self.unknown_faces_dir, filename)
        cv2.imwrite(file_path, face_image)
        print(f"Saved an image of an unidentified person as {filename}")
        return file_path
