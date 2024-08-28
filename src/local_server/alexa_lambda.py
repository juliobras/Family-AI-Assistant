# -*- coding: utf-8 -*-

import logging
import json
import requests
import ask_sdk_core.utils as ask_utils

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

############################# Set up the logger. ############################ 
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
server = "https://2bbd-205-185-108-13.ngrok-free.app"

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Welcome to the Home AI Assistant. You can ask who is at home."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )
############################# Check Who is At home ############################ 
class CheckWhoIsHomeIntentHandler(AbstractRequestHandler):
    """Handler for Check Who Is Home Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("CheckWhoIsHome")(handler_input)

    def handle(self, handler_input):
        # Here you would implement your logic to check who is currently at home
        # For example, making a request to your Home AI system's API
        # Replace 'your_home_ai_system_endpoint' with your actual endpoint
        # API endpoint URL
        data = {
                "request": {
                    "intent": {
                        "name": "CheckWhoIsHome",
                        "confirmationStatus": "NONE",
                        "slots": {
                            "__Conjunction": {
                                "name": "__Conjunction",
                                "confirmationStatus": "NONE"
                            },
                            "Person": {
                                "name": "NONE",
                                "confirmationStatus": "NONE"
                            }
                        }
                    }
                }
            }

        # Headers
        headers = {"Content-Type": "application/json"}

        url = f"{server}/checkwhoshome"
        
        # Make the HTTP GET request to your Home AI system
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            data = response.json()  # Assuming your endpoint returns JSON with a list of names
            people_at_home = data.get('people_at_home', [])
            if people_at_home:
                names = ', '.join(people_at_home)
                speak_output = f"The following people are currently at home: {names}"
            else:
                speak_output = "There is no one at home right now."
        else:
            speak_output = "Sorry, I'm having trouble checking who is at home. Please try again later."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )
############################# House Status ############################ 
class HouseStatusHandler(AbstractRequestHandler):
    def can_handle(self, handler_input):
        # Ensures this handler responds to the correct intent
        return ask_utils.is_intent_name("House_Status")(handler_input)

    def handle(self, handler_input):
        # Prepare headers and the URL for the HTTP request to your Flask app
        headers = {"Content-Type": "application/json"}
        url = f"{server}/house_status"

        # Make the HTTP POST request to your Flask app
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            # Parse the JSON response from your Flask app
            data = response.json()
            
            # Extract lists of clean and messy rooms
            clean_rooms = data.get('Clean', [])
            messy_rooms = data.get('Messy', [])
            
            # Construct the speech output based on the lists of rooms
            rooms_status = []
            if clean_rooms:
                # Join the names of clean rooms into a string
                clean_rooms_list = ', '.join(clean_rooms)
                rooms_status.append(f"The following rooms are clean: {clean_rooms_list}")
            if messy_rooms:
                # Join the names of messy rooms into a string
                messy_rooms_list = ', '.join(messy_rooms)
                rooms_status.append(f"The following rooms are messy: {messy_rooms_list}")

            # Combine all pieces of the speech output
            if rooms_status:
                speak_output = ' and '.join(rooms_status)
            else:
                speak_output = "I could not find any room status right now."
        else:
            # Handle the case where the Flask app did not return a 200 OK response
            speak_output = "Sorry, I'm having trouble checking the room statuses. Please try again later."
        
        # Build and return the response for the Alexa skill
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

############################# Calendar ############################         
from ask_sdk_model.dialog import DelegateDirective

class AddCalendarEventIntentHandler(AbstractRequestHandler):
    """Handler for Add Calendar Event Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AddCalendarEventIntent")(handler_input)

    def handle(self, handler_input):
        current_intent = handler_input.request_envelope.request.intent

        # Check if all necessary slots are filled
        if not current_intent.slots["summary"].value:
            return (
                handler_input.response_builder
                .add_directive(DelegateDirective(updated_intent=current_intent))
                .response
            )

        summary = current_intent.slots['summary'].value
        date = current_intent.slots['date'].value if current_intent.slots['date'].value else None
        start_time = current_intent.slots['start_time'].value if current_intent.slots['start_time'].value else None
        end_time = current_intent.slots['end_time'].value if current_intent.slots['end_time'].value else None
        location = current_intent.slots['location'].value if current_intent.slots['location'].value else None

        # Check if any of the slots are missing and delegate back to Alexa if necessary
        if not date or not start_time or not end_time:
            # Automatically delegate the dialog to Alexa to collect missing slots
            return (
                handler_input.response_builder
                .add_directive(DelegateDirective(updated_intent=current_intent))
                .response
            )

        # Prepare the data to send to your backend service for processing
        data = {
            "summary": summary,
            "date": date,
            "start_time": start_time,
            "end_time": end_time,
            "location": location
        }

        # Specify the endpoint for adding a calendar event
        url = f"{server}/add_calendar_event"

        # Send the request to your service
        headers = {"Content-Type": "application/json"}
        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            speak_output = "Your event has been added to the calendar."
        else:
            speak_output = "I am unable to add the event to the calendar at the moment. Please try again later."
        
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

########### Todays Events ##################

class GetTodaysEventsIntentHandler(AbstractRequestHandler):
    """Handler for Get Today's Events Intent."""
    def can_handle(self, handler_input):
        # Check if the intent matches GetTodaysEventsIntent
        return ask_utils.is_intent_name("GetTodaysEventsIntent")(handler_input)

    def handle(self, handler_input):
        # Prepare headers for the HTTP request to your Flask app
        headers = {"Content-Type": "application/json"}
        url = f"{server}/get_todays_events"  # Replace {server} with your actual server URL

        # Make the HTTP GET request to your Flask app
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            # Parse the JSON response from your Flask app
            data = response.json()
            events = data['events']

            # Construct the speech output based on the events list
            if not events:
                speak_output = data['message']  # "You have no events scheduled for today."
            else:
                speak_output = "Here are your events for today: "
                for event in events:
                    # Assume each event is a dictionary with 'summary' and 'start'
                    event_name = event['summary']
                    start_time = event['start']
                    speak_output += f"{event_name} at {start_time}, "
                speak_output = speak_output.rstrip(', ')  # Removes the trailing comma
        else:
            # Handle the case where the Flask app did not return a 200 OK response
            speak_output = "Sorry, I'm having trouble retrieving your events. Please try again later."

        # Build and return the response for the Alexa skill
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


############################ Native to Alexa ############################ 
class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        speak_output = "You can say, who is at home, to find out who is currently at home."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

class FallbackIntentHandler(AbstractRequestHandler):
    """Single handler for Fallback Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        speech = "Sorry, I don't know that. You can say, who is at home?"
        return handler_input.response_builder.speak(speech).ask(speech).response

class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # No additional cleanup logic required at this point.
        return handler_input.response_builder.response

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handler."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)
        speak_output = "Sorry, I had trouble doing what you asked. Please try again."
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# Build the skill.
sb = SkillBuilder()

# Add the handler to the skill builder.
sb.add_request_handler(AddCalendarEventIntentHandler())
sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(CheckWhoIsHomeIntentHandler())
sb.add_request_handler(HouseStatusHandler())
sb.add_request_handler(GetTodaysEventsIntentHandler()) 

#Built in Alexa
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())
sb.add_exception_handler(CatchAllExceptionHandler())





# Handler function that AWS Lambda calls.
lambda_handler = sb.lambda_handler()
