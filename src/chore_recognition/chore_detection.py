import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
import os


class ChoreDetection:
    def __init__(self, model_path=None):
        """
        Initializes the ChoreDetection model.
        
        :param model_path: Optional; path to a pre-trained model.
        """
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)
        else:
            self.model = self.initialize_model()

    def initialize_model(self):
        """
        Initializes the ResNet50 model for chore detection.
        
        :return: Compiled Keras model.
        """
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)
        x = Dense(1024, activation='relu')(x)
        predictions = Dense(1, activation='sigmoid')(x)
        model = Model(inputs=base_model.input, outputs=predictions)
        
        for layer in base_model.layers:
            layer.trainable = False
            
        model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def preprocess_image(self, image_path):
        """
        Preprocesses the image for model prediction.

        :param image_path: Path to the image file.
        :return: Preprocessed image array.
        """
        img = image.load_img(image_path, target_size=(224, 224))
        img_array = image.img_to_array(img)
        img_array_expanded = np.expand_dims(img_array, axis=0)
        return preprocess_input(img_array_expanded)

    def predict(self, image_path):
        """
        Predicts whether the room in the image is clean or messy.

        :param image_path: Path to the image file.
        :return: Tuple of class prediction and confidence score.
        """
        preprocessed_image = self.preprocess_image(image_path)
        preds = self.model.predict(preprocessed_image)
        class_prediction = 'Clean' if preds[0] < 0.5 else 'Messy'
        confidence_score = preds[0] if class_prediction == 'Messy' else 1 - preds[0]
        return class_prediction, np.float64(confidence_score)

    def fine_tune(self, train_images, train_labels, val_images, val_labels, epochs=10, learning_rate=0.00001):
        """
        Fine-tunes the model with custom images and labels.

        :param train_images: Array of training images.
        :param train_labels: Array of training labels.
        :param val_images: Array of validation images.
        :param val_labels: Array of validation labels.
        :param epochs: Number of epochs for fine-tuning.
        :param learning_rate: Learning rate for the fine-tuning optimizer.
        :return: Training history object.
        """
        # Unfreeze the top layers of the model
        for layer in self.model.layers[-20:]:
            layer.trainable = True

        self.model.compile(optimizer=Adam(learning_rate=learning_rate), 
                           loss='binary_crossentropy', 
                           metrics=['accuracy', 'AUC', 'Precision', 'Recall'])

        history = self.model.fit(train_images, train_labels, 
                                 batch_size=32, 
                                 epochs=epochs, 
                                 validation_data=(val_images, val_labels))
        return history

# Example of how to use the class for prediction
if __name__ == "__main__":
    model_path = '/home/julio/Music/trained_models/model.h5'  # Specify the exact path to your saved model
    chore_detector = ChoreDetection(model_path=model_path)

    folder = '/home/julio/Documents/Family-AI-Assistant/data/test2'  # Update this path to the directory containing your images

    for filename in os.listdir(folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            image_path = os.path.join(folder, filename)
            class_prediction, confidence_score = chore_detector.predict(image_path)
            print(f"The room in {filename} is predicted to be: {class_prediction} with confidence {confidence_score:.2f}")
