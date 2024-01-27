# train_model.py

from chore_detection import ChoreDetection
from tensorflow.keras.optimizers import Adam
import tensorflow as tf

# Instantiate the ChoreDetection class
chore_detector = ChoreDetection()

# Compile the model
chore_detector.model.compile(
    optimizer=Adam(learning_rate=0.0001),
    loss='binary_crossentropy',
    metrics=['accuracy']
)

# Assume you have a function to get your data ready for training
# It should return train_images, train_labels, val_images, val_labels
train_images, train_labels, val_images, val_labels = get_data_ready_for_training()

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
