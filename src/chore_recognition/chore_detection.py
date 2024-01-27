import numpy as np
import tensorflow as tf
from tensorflow.keras.applications.resnet50 import ResNet50, preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D


"""
This class is designed to handle the loading of a ResNet50 model, 
modifying it for a binary classification task, and making predictions.
"""
class ChoreDetection:
    def __init__(self, num_classes=2):
        # Initialize the ResNet50 model with weights pre-trained on ImageNet and without the top layer
        self.base_model = ResNet50(weights='imagenet', include_top=False)
        self.model = self._build_model(num_classes)

    #This private method adds a new top layer to the ResNet50 base for binary classification.
    def _build_model(self, num_classes):
        # Freeze the layers of the base model
        for layer in self.base_model.layers:
            layer.trainable = False

        # Create new layers for binary classification
        x = GlobalAveragePooling2D()(self.base_model.output)
        x = Dense(1024, activation='relu')(x)
        predictions = Dense(1, activation='sigmoid')(x)  # Use sigmoid for binary classification

        # Create a new model with the new top layer
        model = Model(inputs=self.base_model.input, outputs=predictions)
        return model

    #It loads and preprocesses the image to the format required by ResNet50.
    def preprocess_image(self, image_path):
        # Load the image and preprocess it for the model
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        return img_array
     
    #This method runs the prediction on the preprocessed image and returns 'clean' or 'messy' based on the output of the model.
    def predict(self, image_path):
        # Preprocess the image and run the prediction
        preprocessed_image = self.preprocess_image(image_path)
        preds = self.model.predict(preprocessed_image)
        # Convert predictions to 'clean' or 'messy'
        predicted_class = 'clean' if preds[0][0] < 0.5 else 'messy'
        return predicted_class

# The following code is for testing the class functionality
# It should be removed or commented out in the actual module
if __name__ == "__main__":
    # Instantiate the class
    chore_detector = ChoreDetection()

    # Predict the class of an image file
    image_path = 'resources/messy_room.png'  # Update this to the correct path
    prediction = chore_detector.predict(image_path)

    # Print the prediction
    print(f"The room is predicted as: {prediction}")
