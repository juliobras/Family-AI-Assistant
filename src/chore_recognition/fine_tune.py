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

# Directory containing your dataset
photos_directory = "/home/julio/Documents/Family-AI-Assistant/data/fine_tuning_balanced"

# Define a threshold for the model performance
ACCURACY_THRESHOLD = 0.8899999856948853 # Change this to your desired threshold

def train_tune(photos_directory, accuracy_threshold=ACCURACY_THRESHOLD):
    # Initialize ChoreDetection, assuming no path provided to load a pre-trained model
    chore_detector = ChoreDetection()
    
    # Prepare data
    train_images, train_labels, val_images, val_labels, test_images, test_labels = get_data_ready_for_training(photos_directory)
    
    # Train or fine-tune the model
    chore_detector.fine_tune(train_images, train_labels, val_images, val_labels)
    
    # Evaluate the model on the testing set
    evaluation_results = chore_detector.model.evaluate(test_images, test_labels)
    test_loss = evaluation_results[0]  # Assuming the first value is always loss
    test_acc = evaluation_results[1]  # Assuming the second value is always accuracy
    print(f"Test accuracy: {test_acc}, Test loss: {test_loss}")
 
    
    # Check if the model performed better than the threshold
    if test_acc > accuracy_threshold:
        global ACCURACY_THRESHOLD
        ACCURACY_THRESHOLD = test_acc
        # Create a directory for the trained model based on its accuracy
        model_save_directory = f'src/chore_recognition/trained_models/Model:{test_acc*100:.2f}_accuracy'
        if not os.path.exists(model_save_directory):
            os.makedirs(model_save_directory)
        # Save the trained model
        chore_detector.model.save(model_save_directory)
        print(f"Model performed well and was saved to {model_save_directory}")
    else:
        # If model performance is below the threshold, do not save and display a message
        print("Model underperformed and will not be saved.")

def get_data_ready_for_training(data_directory, image_size=(224, 224), validation_split=0.23, test_split=0.2):
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
    train_tune(photos_directory, ACCURACY_THRESHOLD)

if __name__ == "__main__":
    main()



