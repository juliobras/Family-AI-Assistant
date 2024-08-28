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
        Initializes the ChoreDetection class instance.
        
        :param model_path: Optional path to a pre-trained model file. If provided and the file exists,
                           the model from this file will be loaded; otherwise, a new model will be initialized.
        """
        if model_path and os.path.exists(model_path):
            self.model = load_model(model_path)  # Load the pre-trained model if specified and exists
        else:
            self.model = self.initialize_model()  # Initialize a new model if no path provided or file does not exist

    def initialize_model(self):
        """
        Initializes a new ResNet50 model for chore detection, modifying the top layers to suit our binary classification task.
        
        :return: A compiled Keras model ready for training or inference.
        """
        # Load ResNet50 as the base model, excluding its top layer (which is specific to ImageNet classes)
        base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))
        x = base_model.output
        x = GlobalAveragePooling2D()(x)  # Add a global average pooling layer to reduce dimensions
        x = Dense(1024, activation='relu')(x)  # Add a dense layer to learn more complex features
        predictions = Dense(1, activation='sigmoid')(x)  # Output layer for binary classification

        model = Model(inputs=base_model.input, outputs=predictions)

        # Freeze all layers of the base model to prevent their weights from being updated during the first training phase
        for layer in base_model.layers:
            layer.trainable = False

        # Compile the model with appropriate loss function and optimizer for binary classification
        model.compile(optimizer=Adam(learning_rate=0.0001), loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def preprocess_image(self, image_path):
        """
        Loads and preprocesses an image file to be suitable for model prediction.

        :param image_path: Path to the image file.
        :return: A numpy array representing the preprocessed image.
        """
        img = image.load_img(image_path, target_size=(224, 224))  # Load and resize the image
        img_array = image.img_to_array(img)  # Convert the image to a numpy array
        img_array_expanded = np.expand_dims(img_array, axis=0)  # Add a batch dimension
        return preprocess_input(img_array_expanded)  # Preprocess the image as per ResNet50's requirements

    def predict(self, image_path):
        """
        Predicts the class (Clean or Messy) of the room shown in the image.

        :param image_path: Path to the image file.
        :return: A tuple containing the class prediction and confidence score.
        """
        preprocessed_image = self.preprocess_image(image_path)
        preds = self.model.predict(preprocessed_image)
        class_prediction = 'Clean' if preds[0] < 0.4 else 'Messy'
        confidence_score = preds[0] if class_prediction == 'Messy' else 1 - preds[0]
        return class_prediction, np.float64(confidence_score)

    def fine_tune(self, train_images, train_labels, val_images, val_labels, epochs=10, learning_rate=0.00001):
        """
        Fine-tunes the pre-trained model with additional training on a new dataset,
        typically to improve accuracy on a specific task.

        :param train_images: Numpy array of training images.
        :param train_labels: Numpy array of training labels.
        :param val_images: Numpy array of validation images.
        :param val_labels: Numpy array of validation labels.
        :param epochs: Number of training epochs.
        :param learning_rate: Learning rate for the optimizer.
        :return: The history object containing recorded training and validation statistics.
        """
        # Unfreeze some of the top layers of the model for fine-tuning
        for layer in self.model.layers[-20:]:
            layer.trainable = True

        # Re-compile the model to apply the new learning rate
        self.model.compile(optimizer=Adam(learning_rate=learning_rate), 
                           loss='binary_crossentropy', 
                           metrics=['accuracy', 'AUC', 'Precision', 'Recall'])

        # Train the model on the new dataset
        history = self.model.fit(train_images, train_labels, 
                                 batch_size=32, 
                                 epochs=epochs, 
                                 validation_data=(val_images, val_labels))
        return history

# Example usage
if __name__ == "__main__":
    model_path = '/path/to/your/model'  # Specify the path to your saved model
    chore_detector = ChoreDetection(model_path=model_path)

    test_image_path = '/path/to/test/image.jpg'  # Specify the test image path
    class_prediction, confidence_score = chore_detector.predict(test_image_path)
    print(f"The room is predicted to be {class_prediction} with a confidence of {confidence_score:.2f}")
