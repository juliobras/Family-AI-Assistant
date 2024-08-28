import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
from datetime import datetime
import re
import cv2

# Custom module imports
sys.path.append('/Users/julio/Pictures/Family-AI-Assistant/src/user_recognition')
sys.path.append('/Users/julio/Pictures/Family-AI-Assistant/src/chore_recognition')
sys.path.append('/Users/julio/Pictures/Family-AI-Assistant/src/cameras')
sys.path.append('/Users/julio/Pictures/Family-AI-Assistant/src/Google_Integration')

from FaceDatabaseManager import FaceDatabaseManager
from FaceRecognizer import FaceRecognizer
from UserInteractionManager import UserInteractionManager
from Chore_Recognizer_System import Chore_Recognizer_System
from Camera import SharedLaptopCamera
from custom_calendar import GoogleCalendar

# Initialize Flask app and enable CORS for cross-origin requests
app = Flask(__name__)
CORS(app)

# Initialize system components
database_manager = FaceDatabaseManager()
shared_camera = SharedLaptopCamera()
chore_recognizer = Chore_Recognizer_System()
#google_calendar = GoogleCalendar()

def format_event(event):
    """
    Converts a Google Calendar event to a more human-readable format.
    :param event: Google Calendar event object.
    :return: Dictionary with formatted event details.
    """
    # Process and format the event date and time for display
    event_time_str = event['start'].get('dateTime') or event['start'].get('date')
    event_time_str = re.sub(r'[-+]\d{2}:\d{2}', '', event_time_str)
    event_time = datetime.fromisoformat(event_time_str)
    human_readable_time = event_time.strftime('%I:%M %p').lstrip("0").replace(" 0", " ")

    human_readable_date = event_time.strftime('%B %d').rstrip("0").replace(" 0", " ")
    day = event_time.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    human_readable_date = f"{human_readable_date}{suffix}"

    return {"summary": event['summary'], "start": f"{human_readable_time}"}

def initialize_face_recognizer_system():
    """
    Initializes and starts the face recognizer system.
    """
    global user_interaction_manager, face_recognizer
    database_manager.load_known_faces()
    user_interaction_manager = UserInteractionManager(database_manager)
    face_recognizer = FaceRecognizer(user_interaction_manager, shared_camera)
    recognizer_thread = threading.Thread(target=face_recognizer.identify_faces)
    recognizer_thread.daemon = True
    recognizer_thread.start()
    print("Face Recognizer System initialized")

######### Check who is home
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


@app.route('/get_todays_events', methods=['GET'])
def get_todays_events():
    """
    Flask route to fetch today's events from the Google Calendar.
    """
    events = google_calendar.get_events_for_today()
    events_list = [format_event(event) for event in events] if events else []
    message = "Here are your events for today:" if events else "You have no events scheduled for today."
    return jsonify({"events": events_list, "message": message})

if __name__ == '__main__':
    initialize_face_recognizer_system()
    app.run(debug=True, port=5009)



def initialize_face_recognizer_system():
    global user_interaction_manager, face_recognizer,database_manager
    database_manager.load_known_faces()
    user_interaction_manager = UserInteractionManager(database_manager)
    face_recognizer = FaceRecognizer(user_interaction_manager,shared_camera)
    recognizer_thread = threading.Thread(target=face_recognizer.identify_faces)
    recognizer_thread.daemon = True  # Ensure thread closes when main program exits
    recognizer_thread.start()

  
    print("Face Recognizer System initialized")



######### Check who is home
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

######### Check House Status
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
######### Add Calendar Event    
@app.route('/add_calendar_event', methods=['POST'])
def add_calendar_event():
    request_data = request.get_json()
    # Extract event details from the request data
    summary = request_data['summary']
    start_time = request_data['start_time']
    end_time = request_data['end_time']
    description = request_data.get('description', '')
    location = request_data.get('location', '')

   
    created_event = google_calendar.add_event_to_calendar(summary, start_time, end_time, description, location)
    response_data = {
            "version": "1.0",
            "response": {
                "outputSpeech": {
                    "type": "PlainText",
                },
                "shouldEndSession": True
            }
        }  
    response_data["event_added"] = f"Event '{summary}' added successfully to your calendar."  
    
    return jsonify(response_data), 200

######### Todays Events
@app.route('/get_todays_events', methods=['GET'])
def get_todays_events():
    # Create an instance of your GoogleCalendar class
    google_calendar = GoogleCalendar()
    
    # Use the method to fetch events for today
    events = google_calendar.get_events_for_today()

    # Format the events into a response
    if not events:
        # No events found for today
        response_data = {
            "events": [],
            "message": "You have no events scheduled for today."
        }
    else:
        # Assuming 'events' is the original list of events from the Google Calendar API response
        # Each event is a dictionary with 'summary' and 'start' keys
        events_list = [format_event(event) for event in events]
        response_data = {
            "events": events_list,
            "message": "Here are your events for today:"
        }
    # Return a JSON response with the events data
    return jsonify(response_data), 200

if __name__ == '__main__':
  
    initialize_face_recognizer_system()  # Initialize system components
    app.run(debug=True, port=5009)  # Start the Flask server




