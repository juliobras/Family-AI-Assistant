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
import sys
sys.path.append('/Users/julio/Home AI Assistant/Family-AI-Assistant/src/cameras')
#from Camera import SharedLaptopCamera
from Camera import CameraManager
import threading




class FaceRecognizer:
    def __init__(self, interaction_manager: UserInteractionManager, shared_camera:CameraManager):
        
        # Initialize with instances of FaceDatabaseManager and UserInteractionManager.
        # face_history (deque): Deque object storing the history of face identifications.
        # history_length (int): Number of past frames to remember for smoothing face identification.
        
        self.history_length = 10
        self.interaction_manager = interaction_manager
        self.face_history = deque(maxlen=self.history_length)
        self.currently_recognized = {}
        self.currently_recognized_queue = queue.Queue()
        self.recognized_names_set = set()
        self.shared_camera = shared_camera
        self.lock = threading.Lock()
       


    def cleanup_recognized_users(self):
            """
            Cleans up users from the recognition tracking structures if they have not been seen for over 5 seconds.

            This method iterates through all users currently stored in the 'currently_recognized' dictionary,
            checks how long it has been since they were last recognized, and removes them from all tracking
            structures if they haven't been seen in the last 5 seconds. This helps ensure that the system's
            record of recognized users is up-to-date and accurate, reflecting only those users who are currently
            present or have recently been seen.

            Attributes:
                currently_recognized (dict): A dictionary mapping user identifiers to the datetime of their last sighting.
                currently_recognized_queue (queue.Queue): A queue that maintains the order in which users were recognized.
                recognized_names_set (set): A set containing all users who have been recognized and are still considered present.
            """
            # Iterate over a list copy of the currently recognized users to avoid modification during iteration
            for user, last_seen in list(self.currently_recognized.items()):
                # Calculate the time elapsed since the user was last seen
                time_since_seen = (datetime.datetime.now() - last_seen).total_seconds()

                # Check if the user has not been seen for more than 5 seconds
                if time_since_seen > 5:
                    # Remove the user from the currently recognized dictionary
                    del self.currently_recognized[user]

                    # Safely remove the user from the recognition queue
                    # Note: This assumes the user is in the queue; consider try-except block for safety
                    if user in self.currently_recognized_queue.queue:
                        self.currently_recognized_queue.queue.remove(user)

                    # Remove the user from the set of recognized names
                    # Note: No action is taken if the user is not present in the set
                    self.recognized_names_set.discard(user)  # Changed from remove() to discard() for safe removal




    def identify_faces(self):
       
        
        #self.currently_recognized_queue = queue.Queue()
        self.cleanup_recognized_users()
        


        #video_capture = cv2.VideoCapture(0)
        process_this_frame = True
        
        while True:
                    self.cleanup_recognized_users()
                    frame = self.shared_camera.get_frame()
                    if frame is None:
                        continue  # Skip the rest of the loop if no frame is available
                    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
                    if process_this_frame:
                        face_locations = face_recognition.face_locations(small_frame)
                        face_encodings = face_recognition.face_encodings(small_frame, face_locations)
                        

                        face_names = []
                        for face_encoding, face_location in zip(face_encodings, face_locations):
                            matches = face_recognition.compare_faces(self.interaction_manager.database_manager.known_face_encodings, face_encoding,tolerance=0.8)
                            name = "Unknown"
                            self.cleanup_recognized_users()
                            
                            if True not in matches:
                                        with self.lock:
                                            print("User not recognized")
                                        
                                            print(name)
                                            #entering the unknown
                                            unknown_matches = face_recognition.compare_faces(self.interaction_manager.database_manager.unknown_face_encodings, face_encoding,tolerance=0.8)
                                            self.cleanup_recognized_users()
                                            if True not in unknown_matches:
                                                print("not in the unknown")
                                                full_frame_location = tuple(map(lambda x: x * 4, face_location))  # Adjust back to full frame size
                                                            
                                                saved_image_path = self.interaction_manager.database_manager.save_unrecognized_face(frame, full_frame_location)
                                                            #print("User not recognized")
                                                            #self.user_response = self.interaction_manager.notify_unrecognized_presence(saved_image_path)
                                                        
                                                            #WILL NEED TO WORK ON AN ALEXA SKILL TO GET THE USER RESPONSE
                                                            #self.interaction_manager.handle_user_decision(saved_image_path,self.user_response)
                                                pass
                                            else:
                                                 print("Found in the unknown folder")

                                                

                            else:
                                    print("User recognized")
                                    
                                    self.cleanup_recognized_users()
                                    face_distances = face_recognition.face_distance(self.interaction_manager.database_manager.known_face_encodings, face_encoding)
                                    best_match_index = face_distances.argmin()
                                    if matches[best_match_index]:
                                        name = self.interaction_manager.database_manager.known_face_names[best_match_index]
                                        if name not in self.recognized_names_set:
                                            with self.lock:
                                               
                                                self.recognized_names_set.add(name)
                                                self.currently_recognized_queue.put(name)
                                                self.face_history.appendleft(name)  # Add the most recently identified name to the left side of the deque



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

                    
            

                       
                    