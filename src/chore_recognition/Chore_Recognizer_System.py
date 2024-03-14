
from chore_detection import ChoreDetection
import os
import cv2
import numpy as np

class Chore_Recognizer_System:
    def __init__(self):
        print("Initializing the Chore Recognizer")

        self.model_path = '/Users/julio/Home AI Assistant/trained_models 88.00_accuracy'  # Specify the exact path to your saved model
        self.chore_detector_trained_model = ChoreDetection(model_path= self.model_path)
        self.alexa_response = {"Clean": [], "Messy": []}
        self.current_photos = "/Users/julio/Home AI Assistant/Family-AI-Assistant/src/database/chore_photos" 
        self.count = 0
        self.file_path = None

    def save_current_frame(self, frame):
        self.count += 1
        filename = f"mylocation{self.count}.jpg"
        self.file_path = os.path.join(self.current_photos, filename)
        cv2.imwrite(self.file_path, frame)
        
        return self.file_path
    
    def predict_chore(self):
        # Ensure alexa_response is correctly formatted to hold the results
       
        
        for filename in os.listdir(self.current_photos):
            try:
                base_filename, file_ext = os.path.splitext(filename)
                # Ensure only supported image formats are processed
                if file_ext.lower() not in ['.jpg', '.jpeg', '.png']:  # Add or remove formats as needed
                    continue  # Skip unsupported file formats
                
                image_path = os.path.join(self.current_photos, filename)
                
                # Ensure any necessary preprocessing is applied within predict method
                class_prediction, confidence_score = self.chore_detector_trained_model.predict(image_path)
                
                if class_prediction == "Clean":
                    if  base_filename not in self.alexa_response["Clean"]:
                        self.alexa_response["Clean"].append(f"{base_filename}")# with confidence score {round((np.float64(confidence_score) * 100),2 )}%")
                else:
                    if  base_filename not in self.alexa_response["Messy"]:
                        self.alexa_response["Messy"].append(f"{base_filename}")# with confidence score {round((np.float64(confidence_score) * 100),2 )}%")
                    
            except Exception as e:  # Consider a more specific exception based on your model's error types
                print(f"Error processing file {filename}: {e}")
                continue  # Skip this file and move to the next one
        print(self.alexa_response)
        return self.alexa_response

  

           
# Example of how to use the class for prediction
if __name__ == "__main__":
    test = Chore_Recognizer_System()
    #test.predict_chore()

    

    