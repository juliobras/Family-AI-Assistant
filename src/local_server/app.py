from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/checkwhoshome', methods=['POST'])
def check_whos_home():
    request_data = request.get_json()  # Get the JSON payload from the Alexa request
    person = request_data.get('request', {}).get('intent', {}).get('slots', {}).get('Person', {}).get('value', None)

    # Simulated logic for checking if a person is at home
    people_at_home = ["James", "Julio"]  # Replace with your actual logic to determine who is at home

    response_data = {
        "version": "1.0",
        "response": {
            "outputSpeech": {
                "type": "PlainText",
            },
            "shouldEndSession": True
        }
    }  # Initialize response data

    if person:  # If a specific person is asked for
        if person in people_at_home:
            response_data["response"]["outputSpeech"]["text"] = f"Yes, {person} is currently at home."
        else:
            response_data["response"]["outputSpeech"]["text"] = f"No, {person} is not at home right now."
    else:  # If no specific person is mentioned in the query
        response_data["response"]["outputSpeech"]["text"] = "There is no one at home right now." if not people_at_home else f"The following people are currently at home: {', '.join(people_at_home)}"
        response_data["people_at_home"] = people_at_home  # Add people at home list

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True, port=5009)





