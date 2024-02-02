import numpy as np
import tensorflow as tf
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
import platform
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import legacy

# Check the platform
if platform.system() == 'Darwin':  # Darwin is the system name for macOS
    # Check for ARM architecture (M1/M2 chips)
    if platform.machine().startswith('arm') or platform.machine().startswith('aarch64'):
        optimizer = legacy.Adam()
    else:
        optimizer = Adam()
else:
    optimizer = Adam()

class ChoreDetection:
    def __init__(self, num_classes=2):
        self.base_model = ResNet50(weights='imagenet', include_top=False)
        self.model = self._build_model(num_classes)
        self._compile_model()

    

    def _build_model(self, num_classes):
        for layer in self.base_model.layers:
            layer.trainable = False
        x = GlobalAveragePooling2D()(self.base_model.output)
        x = Dense(1024, activation='relu')(x)
        predictions = Dense(num_classes, activation='sigmoid' if num_classes == 2 else 'softmax')(x)
        model = Model(inputs=self.base_model.input, outputs=predictions)
        return model

    def _compile_model(self):
        self.model.compile(optimizer=optimizer,
                           loss='binary_crossentropy',
                           metrics=['accuracy'])

    def preprocess_image(self, image_path):
        try:
            img = image.load_img(image_path, target_size=(224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array = preprocess_input(img_array)
            return img_array
        except Exception as e:
            print(f"An error occurred while preprocessing the image: {e}")
            return None

    def predict(self, image_path):
        preprocessed_image = self.preprocess_image(image_path)
        if preprocessed_image is not None:
            preds = self.model.predict(preprocessed_image)
            predicted_class = 'clean' if preds[0][0] < 0.5 else 'messy'
            return predicted_class
        else:
            return "Error processing image"

if __name__ == "__main__":
    chore_detector = ChoreDetection()
    image_path = '/Users/julio/Documents/Home AI Assistant/Family-AI-Assistant/data/images/rooms/clean/bathroom/3EsdScyAFuw.jpg'  # Update this to the correct path
    prediction = chore_detector.predict(image_path)
    print(f"The messy room is predicted as: {prediction}")
    image_path = '/Users/julio/Documents/Home AI Assistant/Family-AI-Assistant/data/images/rooms/clean/bathroom/3EsdScyAFuw.jpg'  # Update this to the correct path
    prediction = chore_detector.predict(image_path)
    print(f"The clean room is predicted as: {prediction}")
