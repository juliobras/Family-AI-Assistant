from chore_detection import ChoreDetection
import os
import cv2
import numpy as np

class Chore_Recognizer_System:
    def __init__(self):
        """
        Initializes the Chore Recognizer System.

        This sets up the system by loading the trained model for chore detection and preparing the storage for analysis results.
        """
        print("Initializing the Chore Recognizer")

        # Path to the trained model directory
        self.model_path = '/Users/julio/Home AI Assistant/trained_models 88.00_accuracy'
        # Initialize the Chore Detection model with the given model path
        self.chore_detector_trained_model = ChoreDetection(model_path=self.model_path)
        # Dictionary to hold the classification results for interaction with Alexa
        self.alexa_response = {"Clean": [], "Messy": []}
        # Directory where the current photos for analysis are stored
        self.current_photos = "src/database/chore_photos"
        # Counter for tracking the number of processed frames
        self.count = 0

    def save_current_frame(self, frame):
        """
        Saves the given frame as a JPEG file in the system's photo directory.

        :param frame: The camera frame to save.
        :return: The file path of the saved image.
        """
        self.count += 1
        filename = f"mylocation{self.count}.jpg"
        file_path = os.path.join(self.current_photos, filename)
        cv2.imwrite(file_path, frame)  # Save the image to disk
        return file_path
    
    def predict_chore(self):
        """
        Predicts the chore state (Clean or Messy) for each stored image in the current photo directory.

        The function updates the alexa_response dictionary with the filename and confidence score for each analyzed image.

        :return: A dictionary containing the list of filenames categorized under 'Clean' or 'Messy' with their confidence scores.
        """
        # Iterate over each file in the current photo directory
        for filename in os.listdir(self.current_photos):
            try:
                base_filename, file_ext = os.path.splitext(filename)
                # Process only supported image formats
                if file_ext.lower() not in ['.jpg', '.jpeg', '.png']:
                    continue  # Skip unsupported file formats

                image_path = os.path.join(self.current_photos, filename)
                # Predict the class (Clean or Messy) for the image
                class_prediction, confidence_score = self.chore_detector_trained_model.predict(image_path)

                # Update the alexa_response dictionary with the result
                if class_prediction == "Clean":
                    if base_filename not in self.alexa_response["Clean"]:
                        self.alexa_response["Clean"].append(f"{base_filename} with confidence score {round((np.float64(confidence_score) * 100),2)}%")
                else:
                    if base_filename not in self.alexa_response["Messy"]:
                        self.alexa_response["Messy"].append(f"{base_filename} with confidence score {round((np.float64(confidence_score) * 100),2)}%")
                    
            except Exception as e:
                print(f"Error processing file {filename}: {e}")
                continue  # Skip to the next file if an error occurs
        print(self.alexa_response)
        return self.alexa_response

# Demonstrate usage of the Chore Recognizer System
if __name__ == "__main__":
    chore_recognizer_system = Chore_Recognizer_System()
    # Optionally call predict_chore to test the functionality
    # chore_recognizer_system.predict_chore()
