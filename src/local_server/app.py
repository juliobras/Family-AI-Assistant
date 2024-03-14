
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
sys.path.append('/Users/julio/Home AI Assistant/Family-AI-Assistant/src/user_recognition')
sys.path.append('/Users/julio/Home AI Assistant/Family-AI-Assistant/src/chore_recognition')
sys.path.append('/Users/julio/Home AI Assistant/Family-AI-Assistant/src/cameras')
from FaceDatabaseManager import FaceDatabaseManager
from FaceRecognizer import FaceRecognizer
from UserInteractionManager import UserInteractionManager
from Chore_Recognizer_System import Chore_Recognizer_System  
from Camera import SharedLaptopCamera  # Assume the class above is saved as laptop_camera.py



# Later, you can stop the camera when your application is closing or when you don't need it anymore.
# camera.stop_camera()

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# Global variables for system components
database_manager = FaceDatabaseManager()
user_interaction_manager = None
face_recognizer = None
# Initialize global shared camera
shared_camera = SharedLaptopCamera()

chore_recognizer = Chore_Recognizer_System()

def initialize_face_recognizer_system():
    global user_interaction_manager, face_recognizer,database_manager
    database_manager.load_known_faces()
    user_interaction_manager = UserInteractionManager(database_manager)
    face_recognizer = FaceRecognizer(user_interaction_manager,shared_camera)
    recognizer_thread = threading.Thread(target=face_recognizer.identify_faces)
    recognizer_thread.daemon = True  # Ensure thread closes when main program exits
    recognizer_thread.start()

  
    print("Face Recognizer System initialized")
    # while True:
    #         current_people = list(face_recognizer.currently_recognized_queue.queue)
    #         print(current_people)
    #         print(f"Currently recognized people are: {', '.join(current_people)}")
    #         time.sleep(5)  # Check every 10 seconds

@app.route('/checkwhoshome', methods=['POST'])
def check_whos_home():
    people_at_home = list(face_recognizer.currently_recognized_queue.queue)  # Retrieve the current list of recognized people
    request_data = request.get_json()  # Get the JSON payload from the Alexa request
    person = request_data.get('request', {}).get('intent', {}).get('slots', {}).get('Person', {}).get('value', None)
    response_data = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
            },
            "shouldEndSession": True
        }
    }  

    if person:  # If a specific person is asked for
        if person in people_at_home:
            response_data["response"]["outputSpeech"]["text"] = f"Yes, {person} is currently at home."
        else:
            response_data["response"]["outputSpeech"]["text"] = f"No, {person} is not at home right now."
    else:  # If no specific person is mentioned in the query
        response_data["response"]["outputSpeech"]["text"] = "There is no one at home right now." if not people_at_home else f"The following people are currently at home: {', '.join(people_at_home)}"
        response_data["people_at_home"] = people_at_home  # Add people at home list

    return jsonify(response_data)

@app.route('/house_status', methods=['POST'])    
def house_status():
    last_frame = shared_camera.get_frame() # Get the last frame from the camera
    chore_recognizer.save_current_frame(last_frame)

    house_status = chore_recognizer.predict_chore()

    response_data = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
            },
            "shouldEndSession": True
        }
    }  
    response_data["house_status"] = house_status  
   

    return house_status
    

if __name__ == '__main__':
  
    initialize_face_recognizer_system()  # Initialize system components
    app.run(debug=True, port=5009)  # Start the Flask server




