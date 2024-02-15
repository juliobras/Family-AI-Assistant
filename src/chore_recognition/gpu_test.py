import tensorflow as tf

if tf.config.list_physical_devices('GPU'):
    print("GPUs available: ", tf.config.list_physical_devices('GPU'))
else:
    print("No GPUs were found.")


import tensorflow as tf

gpus = tf.config.experimental.list_physical_devices('GPU')
if gpus:
    try:
        # Currently, memory growth needs to be the same across GPUs
        for gpu in gpus:
            tf.config.experimental.set_memory_growth(gpu, True)
        logical_gpus = tf.config.experimental.list_logical_devices('GPU')
        print(len(gpus), "Physical GPUs,", len(logical_gpus), "Logical GPUs")
    except RuntimeError as e:
        # Memory growth must be set before GPUs have been initialized
        print(e)

# import tensorflow as tf
# print(tf.config.list_physical_devices('GPU'))
