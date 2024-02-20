from chore_detection import ChoreDetection
import numpy as np
import tensorflow as tf
from sklearn.model_selection import train_test_split
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.models import Model, load_model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.optimizers import Adam
import numpy as np
import os


class FineTune:
    def __init__(self, chore_detection, photos_directory, accuracy_threshold):
        self.chore_detection = chore_detection
        self.photos_directory = photos_directory
        self.accuracy_threshold = accuracy_threshold

    def train_tune(self):
        # Prepare data
        train_images, train_labels, val_images, val_labels, test_images, test_labels = self.get_data_ready_for_training(self.photos_directory)
        
        # Train or fine-tune the model
        self.chore_detection.fine_tune(train_images, train_labels, val_images, val_labels)
        
        # Evaluate the model on the testing set
        evaluation_results = self.chore_detection.model.evaluate(test_images, test_labels)
        test_loss, test_acc = evaluation_results  # Assuming the first value is always loss and the second is accuracy
        print(f"Test accuracy: {test_acc}, Test loss: {test_loss}")
    
        # Check if the model performed better than the threshold
        if test_acc > self.accuracy_threshold:
            self.accuracy_threshold = test_acc  # Update the accuracy threshold
            model_save_directory = f'src/chore_recognition/trained_models/Model_{test_acc*100:.2f}_accuracy'
            if not os.path.exists(model_save_directory):
                os.makedirs(model_save_directory)
            self.chore_detection.model.save(model_save_directory)
            print(f"Model performed well and was saved to {model_save_directory}")
        else:
            print("Model underperformed and will not be saved.")

    def get_data_ready_for_training(self, data_directory, image_size=(224, 224), validation_split=0.23, test_split=0.2):
        images, labels = [], []
        for condition in ['clean', 'messy']:
            directory = os.path.join(data_directory, condition)
            for filename in os.listdir(directory):
                if filename.lower().endswith(('png', 'jpg', 'jpeg')):
                    filepath = os.path.join(directory, filename)
                    img = image.load_img(filepath, target_size=image_size)
                    img_array = image.img_to_array(img)
                    images.append(img_array)
                    labels.append(1 if condition == 'messy' else 0)

        images = np.array(images)
        labels = np.array(labels)

        # Preprocess the images
        images = preprocess_input(images)

        # Split the dataset
        train_images, test_images, train_labels, test_labels = train_test_split(images, labels, test_size=test_split + validation_split, stratify=labels)
        val_images, test_images, val_labels, test_labels = train_test_split(test_images, test_labels, test_size=test_split / (test_split + validation_split), stratify=test_labels)

        return train_images, train_labels, val_images, val_labels, test_images, test_labels

def main():
    # Assuming ChoreDetection is a class you've defined elsewhere and you have an instance of it
    chore_detection_instance = ChoreDetection()  # You need to define this before or import if it's defined elsewhere
    photos_directory = "/home/julio/Documents/Family-AI-Assistant/data/fine_tuning_balanced"
    accuracy_threshold = 0.89  # Change this to your desired threshold
    
    fine_tuner = FineTune(chore_detection_instance, photos_directory, accuracy_threshold)
    fine_tuner.train_tune()

if __name__ == "__main__":
    main()
