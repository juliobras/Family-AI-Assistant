import cv2
import face_recognition
import os
from collections import deque
from datetime import datetime

class UserIdentification:
    """
    A class for identifying known and unknown users through facial recognition.

    Attributes:
        photos_path (str): Directory path containing photos of known family members.
        unknown_faces_path (str): Directory path for storing photos of unknown faces.
        known_face_encodings (list): List of face encodings for known family members.
        known_face_names (list): List of names corresponding to known family members.
        face_history (deque): Deque object storing the history of face identifications.
        history_length (int): Number of past frames to remember for smoothing face identification.
    """

    def __init__(self, photos_path="src/user_recognition/family_member_photos", unknown_faces_path="src/user_recognition/unknown_faces", history_length=10):
        """
        Initializes the UserIdentification class with paths and history length.
        """
        self.photos_path = photos_path
        self.unknown_faces_path = unknown_faces_path
        self.known_face_encodings = []
        self.known_face_names = []
        self.face_history = deque(maxlen=history_length)
        self.load_known_faces()
        self.add_to_family  = False

    def load_known_faces(self):
        """
        Loads and encodes faces from the known faces directory.
        """
        for filename in os.listdir(self.photos_path):
            if filename.endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(self.photos_path, filename)
                image = face_recognition.load_image_file(image_path)
                face_encodings = face_recognition.face_encodings(image)
                if face_encodings:
                    self.known_face_encodings.append(face_encodings[0])
                    self.known_face_names.append(os.path.splitext(filename)[0])
        return self.known_face_encodings, self.known_face_names

    def save_unrecognized_face(self, frame, location):
        """
        Saves an image of an unrecognized face.
        """
        top, right, bottom, left = location
        face_image = frame[top:bottom, left:right]
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        filename = f"unidentified-{timestamp}.jpg"
        file_path = os.path.join(self.unknown_faces_path, filename)
        cv2.imwrite(file_path, face_image)
        print(f"Saved an image of an unidentified person as {filename}")
        return file_path

    def notify_unrecognized_presence(self, filename):
        """
        Placeholder method for notifying about an unrecognized presence.
        """
        #this will eventually call another function to send a notification to the user
        print(f"Notification: An unidentified person was detected and saved as {filename}. Please check immediately.")
        self.add_to_family = input("Do you want to add this person to the family photos? (True/False)") 
       

    def handle_user_decision(self, image_path, add_to_family):
        """
        Handles the user's decision to add or ignore an unrecognized face.
        """
        if add_to_family is True:
            new_path = os.path.join(self.photos_path, os.path.basename(image_path))
            os.rename(image_path, new_path)
            image = face_recognition.load_image_file(new_path)
            face_encodings = face_recognition.face_encodings(image)
            if face_encodings:
                self.known_face_encodings.append(face_encodings[0])
                self.known_face_names.append(os.path.splitext(os.path.basename(new_path))[0])
                print(f"Added new member from {os.path.basename(new_path)} to family photos.")
                
                os.remove(image_path)
                print(f"Removed {os.path.basename(image_path)} from unknown faces.")
        else:
            print("this will trigger the security feature which will be implemented later.")

            

    def identify_faces(self):
        """
        Identifies faces in video from the default webcam, checks against known faces,
        and handles unknown faces according to user settings.
        """
        video_capture = cv2.VideoCapture(0)
        process_this_frame = True

        while True:
            ret, frame = video_capture.read()
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            if process_this_frame:
                face_locations = face_recognition.face_locations(small_frame)
                face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                face_names = []
                for face_encoding, face_location in zip(face_encodings, face_locations):
                    matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                    name = "Unknown"

                    if True not in matches:
                        if self.face_history and any(face_dict['name'] != 'Unknown' for frame in self.face_history for face_dict in frame):
                            recent_names = [face_dict['name'] for frame in self.face_history for face_dict in frame]
                            name = max(set(recent_names), key=recent_names.count)
                            if name != 'Unknown':
                                face_names.append(name)
                                continue
                        original_location = tuple(map(lambda x: x * 4, face_location))
                        saved_image_path = self.save_unrecognized_face(frame, original_location)
                        self.user_input = self.notify_unrecognized_presence(os.path.basename(saved_image_path))
                        print(self.add_to_family)
                        self.handle_user_decision(saved_image_path, self.user_input)
                        
                        

                    else:
                        face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                        best_match_index = face_distances.argmin()
                        if matches[best_match_index]:
                            name = self.known_face_names[best_match_index]

                    face_names.append(name)

                self.face_history.appendleft([{'location': face_location, 'name': name} for face_location, name in zip(face_locations, face_names)])

            process_this_frame = not process_this_frame

            for (top, right, bottom, left), name in zip(face_locations, face_names):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4
                # Check if the face is recognized or not and set the box color
                if name == "Unknown":
                    box_color = (0, 0, 255)  # Red for unknown face
                else:
                    box_color = (0, 255, 0)  # Green for recognized face

                # Draw a box around the face
                cv2.rectangle(frame, (left, top), (right, bottom), box_color, 2)
                # Draw a label with a name below the face
                cv2.rectangle(frame, (left, bottom - 35), (right, bottom), box_color, cv2.FILLED)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(frame, name, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)

            cv2.imshow('Video', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        video_capture.release()
        cv2.destroyAllWindows()



if __name__ == "__main__":
    user_identifier = UserIdentification()
    user_identifier.identify_faces()

