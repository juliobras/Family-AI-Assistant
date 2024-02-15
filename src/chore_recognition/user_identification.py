import cv2
import os

# Function to create a profile for a family member
def create_profile(name):
    # Create a directory for the user's profile
    profile_dir = f"profiles/{name}"
    os.makedirs(profile_dir, exist_ok=True)
    print(f"Profile created for {name}")

# Function to recognize faces
def recognize_faces():
    # Load pre-trained face recognition model
    # Replace 'face_recognition_model.xml' with the path to your pre-trained model
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    face_recognizer.read('face_recognition_model.xml')

    # Initialize webcam
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Perform face detection
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

        for (x, y, w, h) in faces:
            # Recognize the face
            id_, confidence = face_recognizer.predict(gray[y:y+h, x:x+w])

            # Check if the face matches any known profiles
            if confidence < 50:
                # Known user
                # Replace 'profiles' with the directory where user profiles are stored
                name = "User"  # Get the name associated with id_
                cv2.putText(frame, f"{name}", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
            else:
                # Unknown user
                print("Unknown person detected!")

            # Draw rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

        # Display the frame
        cv2.imshow('Video', frame)

        # Exit loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    # Example usage
    create_profile("John")
    create_profile("Jane")
    recognize_faces()
