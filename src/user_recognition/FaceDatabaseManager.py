import cv2
import os
import face_recognition
from datetime import datetime

class FaceDatabaseManager:
    """
    Manages a database of facial encodings, allowing for the loading of known faces and saving images of unrecognized faces.
    """
    def __init__(self):
        """
        Initializes the FaceDatabaseManager with directories for known and unknown faces.
        """
        # Lists to store known face encodings and their corresponding names
        self.known_face_encodings = []
        self.known_face_names = []
        # Directory containing known faces images
        self.known_faces_dir = "src/database/user_reco_photos/family_member_photos"
        # Directory to store images of unrecognized faces
        self.unknown_faces_dir = "src/database/user_reco_photos/unknown_faces"

    def load_known_faces(self):
        """
        Loads face encodings and names from the known faces directory and updates internal lists.
        """
        name_set = set()  # To avoid duplicates, we keep track of names already loaded
        for filename in os.listdir(self.known_faces_dir):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                # Extract the base name to use as the identity (remove file extension and numeric suffix)
                name = os.path.splitext(filename)[0]
                base_name = ''.join(filter(str.isalpha, name))

                image_path = os.path.join(self.known_faces_dir, filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)

                if face_encodings:
                    # Add the encoding and name only if this name hasn't been processed yet
                    if base_name not in name_set:
                        self.known_face_encodings.append(face_encodings[0])
                        self.known_face_names.append(base_name)
                        name_set.add(base_name)  # Mark this name as processed

    def save_unrecognized_face(self, frame, location):
        """
        Saves an image of an unrecognized face to the unknown faces directory.

        :param frame: The frame from which the face is to be extracted.
        :param location: The bounding box of the face in the format (top, right, bottom, left).
        :return: The file path of the saved image.
        """
        # Generate a timestamp for the filename
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        top, right, bottom, left = location
        # Extract the face image from the frame using the given location
        face_image = frame[top:bottom, left:right]
        filename = f"unidentified_person-{timestamp}.jpg"
        file_path = os.path.join(self.unknown_faces_dir, filename)
        cv2.imwrite(file_path, face_image)  # Save the extracted face image to disk

        print(f"Saved an image of an unidentified person as {filename}")
        return file_path
