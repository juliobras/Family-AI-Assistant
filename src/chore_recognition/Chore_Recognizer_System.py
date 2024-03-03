
from chore_detection import ChoreDetection
import os


class Chore_Recognizer_System:
    def __init__(self):
        print("Initializing the Chore Recognizer")

        self.model_path = '/Users/julio/Home AI Assistant/trained_models 88.00_accuracy'  # Specify the exact path to your saved model
        self.chore_detector_trained_model = ChoreDetection(model_path= self.model_path)
        self.current_photos = '/Users/julio/Home AI Assistant/data/test2'  # Update this path to the directory containing your images
        self.alexa_response = {"Clean": [], "Messy": []}
 
    def predict_chore(self):
        # Ensure alexa_response is correctly formatted to hold the results
        self.alexa_response = {"Clean": [], "Messy": []}  # Resetting or initializing the response structure
        
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
                    self.alexa_response["Clean"].append(base_filename)
                else:
                    self.alexa_response["Messy"].append(base_filename)
                    
            except Exception as e:  # Consider a more specific exception based on your model's error types
                print(f"Error processing file {filename}: {e}")
                continue  # Skip this file and move to the next one
        print(self.alexa_response)
        return self.alexa_response

    # def predict_chore(self):
    #     for filename in os.listdir(self.current_photos):
    #         # Split the filename from its extension
    #         base_filename, _ = os.path.splitext(filename)
    #         # Construct the full path to the image
    #         image_path = os.path.join(self.current_photos, filename)
    #         # Predict the class and confidence score using the model
    #         class_prediction, confidence_score = self.chore_detector_trained_model.predict(image_path)
    #         # Append the result to alexa_response without file extension in the message
    #         if class_prediction == "Clean":
    #             self.alexa_response["Clean"].append(base_filename)
    #         else:
    #             self.alexa_response["Messy"].append(base_filename)
 
    #     return self.alexa_response

           
# Example of how to use the class for prediction
if __name__ == "__main__":
    test = Chore_Recognizer_System()
    #test.predict_chore()

    

    