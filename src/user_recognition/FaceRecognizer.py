"""
Deals with the identification of faces, including encoding and matching faces against known ones. 
This class would use face recognition libraries and manage the logic for identifying whether a face is known or unknown.
"""
import cv2
import face_recognition
from UserInteractionManager import UserInteractionManager
from collections import deque
import datetime
import queue
class FaceRecognizer:
    def __init__(self, interaction_manager: UserInteractionManager):
        """
        Initialize with instances of FaceDatabaseManager and UserInteractionManager.
        face_history (deque): Deque object storing the history of face identifications.
        history_length (int): Number of past frames to remember for smoothing face identification.
        """
        self.history_length = 10
        self.interaction_manager = interaction_manager
        self.face_history = deque(maxlen=self.history_length)
        self.currently_recognized = {}
        self.currently_recognized_queue = queue.Queue()
        self.recognized_names_set = set()


    def cleanup_recognized_users(self):
        for user, last_seen in list(self.currently_recognized.items()):
            if (datetime.datetime.now() - last_seen).total_seconds() > 5:
                del self.currently_recognized[user]
                self.currently_recognized_queue.queue.remove(user) 
                self.recognized_names_set.remove(user)  # Add this line



    def identify_faces(self):
        """
        Capture video from the default webcam and identify faces.
        """
        self.currently_recognized_queue = queue.Queue()
        self.cleanup_recognized_users()
        

        video_capture = cv2.VideoCapture(0)
        process_this_frame = True

        while True:
                self.cleanup_recognized_users()
                ret, frame = video_capture.read()
                small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                if process_this_frame:
                    face_locations = face_recognition.face_locations(small_frame)
                    face_encodings = face_recognition.face_encodings(small_frame, face_locations)

                    face_names = []
                    for face_encoding, face_location in zip(face_encodings, face_locations):
                        matches = face_recognition.compare_faces(self.interaction_manager.database_manager.known_face_encodings, face_encoding)
                        name = "Unknown"
                        self.cleanup_recognized_users()

                        if True not in matches:
                            self.cleanup_recognized_users()
                            # Save and notify about unrecognized face
                            full_frame_location = tuple(map(lambda x: x * 4, face_location))  # Adjust back to full frame size
                            
                            saved_image_path = self.interaction_manager.database_manager.save_unrecognized_face(frame, full_frame_location)
                            print("User not recognized")
                            #self.user_response = self.interaction_manager.notify_unrecognized_presence(saved_image_path)
                          
                            """WILL NEED TO WORK ON AN ALEXA SKILL TO GET THE USER RESPONSE."""
                            #self.interaction_manager.handle_user_decision(saved_image_path,self.user_response)

                        else:
                            self.cleanup_recognized_users()
                            face_distances = face_recognition.face_distance(self.interaction_manager.database_manager.known_face_encodings, face_encoding)
                            best_match_index = face_distances.argmin()
                            if matches[best_match_index]:
                                name = self.interaction_manager.database_manager.known_face_names[best_match_index]
                                if name not in self.recognized_names_set:
                                    self.recognized_names_set.add(name)
                                    self.currently_recognized_queue.put(name)


                                self.currently_recognized[name] = datetime.datetime.now()

                        self.cleanup_recognized_users()
                        face_names.append(name)


                process_this_frame = not process_this_frame

                # Display the results
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

                #cv2.imshow('Video', frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

         

        video_capture.release()
        cv2.destroyAllWindows()
