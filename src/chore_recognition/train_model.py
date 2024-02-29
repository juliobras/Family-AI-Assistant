from chore_detection import ChoreDetection
from tensorflow.keras.optimizers.legacy import Adam
import tensorflow as tf
import sklearn as sklearn
from sklearn.model_selection import train_test_split
import numpy as np
import os
from PIL import Image
import tensorflow as tf
# Instantiate the ChoreDetection class
chore_detector = ChoreDetection()

photos_directory = '/Users/julio/Home AI Assistant/Family-AI-Assistant/data/images/rooms'
# Compile the model
chore_detector.model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

def get_data_ready_for_training(data_directory, image_size=(224, 224), validation_split=0.2, test_split=0.1):
    """
    Prepare and balance the data for training, considering the organization of clean and messy images,
    and split into training, validation, and testing sets.

    Parameters:
    - data_directory: Path to the dataset.
    - image_size: Target size for each image.
    - validation_split: Fraction of data for validation (applied after separating test data).
    - test_split: Fraction of data for testing.

    Returns:
    - train_images, train_labels: Training images and labels.
    - val_images, val_labels: Validation images and labels.
    - test_images, test_labels: Testing images and labels.
    """
    images, labels = [], []

    # Process 'clean' images from subfolders
    clean_directory = os.path.join(data_directory, 'clean')
    for room_type in os.listdir(clean_directory):
        room_path = os.path.join(clean_directory, room_type)
        if os.path.isdir(room_path):
            for image_file in os.listdir(room_path):
                image_path = os.path.join(room_path, image_file)
                image = Image.open(image_path).resize(image_size)
                images.append(np.array(image))
                labels.append('clean')  # Label all these images as 'clean'

    # Process 'messy' images
    messy_directory = os.path.join(data_directory, 'messy')
    for image_file in os.listdir(messy_directory):
        image_path = os.path.join(messy_directory, image_file)
        image = Image.open(image_path).resize(image_size)
        images.append(np.array(image))
        labels.append('messy')  # Label all these images as 'messy'

    # Convert lists to numpy arrays
    images = np.array(images)
    labels = np.array(labels)

    # Scale images
    images = images.astype('float32') / 255.0

    # Convert labels to binary (0 for clean, 1 for messy)
    labels = np.where(labels == 'clean', 0, 1)

    # Balancing the dataset
    clean_indices = np.where(labels == 0)[0]
    messy_indices = np.where(labels == 1)[0]
    min_count = min(len(clean_indices), len(messy_indices))
    np.random.shuffle(clean_indices)
    np.random.shuffle(messy_indices)
    balanced_indices = np.concatenate([clean_indices[:min_count], messy_indices[:min_count]])

    balanced_images = images[balanced_indices]
    balanced_labels = labels[balanced_indices]

    # First split: separate out a test set
    initial_images, test_images, initial_labels, test_labels = train_test_split(
        balanced_images, balanced_labels, test_size=test_split, random_state=42)

    # Second split: separate the remaining data into training and validation sets
    train_images, val_images, train_labels, val_labels = train_test_split(
        initial_images, initial_labels, test_size=validation_split / (1 - test_split), random_state=42)

    return train_images, train_labels, val_images, val_labels, test_images, test_labels

train_images, train_labels, val_images, val_labels, test_images, test_labels = get_data_ready_for_training(photos_directory)

# Train the model
chore_detector.model.fit(
    train_images,
    train_labels,
    batch_size=32,
    epochs=10,
    validation_data=(val_images, val_labels)
)

# Save the trained model
chore_detector.model.save('/home/julio/Documents/Family-AI-Assistant/models_directory/chore_detaction_model/chore_detector_model.h5')

# If using `tf.data.Dataset` API or generators, you would adapt the `.fit` call accordingly
