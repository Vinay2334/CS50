import cv2
import numpy as np
import os
import sys
import tensorflow as tf

from sklearn.model_selection import train_test_split

EPOCHS = 30
IMG_WIDTH = 30
IMG_HEIGHT = 30
NUM_CATEGORIES = 43
TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) not in [2, 3]:
        sys.exit("Usage: python traffic.py data_directory [model.h5]")

    images, labels = load_data(sys.argv[1])

    x_train, x_test, y_train, y_test = train_test_split(
        np.array(images), np.array(labels), test_size=TEST_SIZE, random_state=42
    )

    x_train, x_test = x_train / 255.0, x_test / 255.0

    # Convert labels to categorical AFTER splitting
    y_train = tf.keras.utils.to_categorical(y_train, num_classes=NUM_CATEGORIES)
    y_test = tf.keras.utils.to_categorical(y_test, num_classes=NUM_CATEGORIES)

    # Get a compiled neural network
    model = get_model()

    # Fit model on training data
    model.fit(x_train, y_train, epochs=EPOCHS, validation_data=(x_test, y_test))

    # Evaluate neural network performance
    test_loss, test_accuracy = model.evaluate(x_test, y_test, verbose=2)
    print(f"\nTest Accuracy: {test_accuracy:.4f}, Test Loss: {test_loss:.4f}")

    model.summary()

    # Save model to file
    if len(sys.argv) == 3:
        filename = sys.argv[2]
        model.save(filename)
        print(f"Model saved to {filename}.")


def load_data(data_dir):
    """
    Load image data from directory `data_dir`.

    Assume `data_dir` has one directory named after each category, numbered
    0 through NUM_CATEGORIES - 1. Inside each category directory will be some
    number of image files.

    Return tuple `(images, labels)`. `images` should be a list of all
    of the images in the data directory, where each image is formatted as a
    numpy ndarray with dimensions IMG_WIDTH x IMG_HEIGHT x 3. `labels` should
    be a list of integer labels, representing the categories for each of the
    corresponding `images`.
    """
    images, labels = [], []
    for root, dirs, files in os.walk(data_dir):
        category = os.path.basename(root)
        if category.isdigit():
            category = int(category)
            for file in files:
                file_path = os.path.join(root, file)
                image = cv2.imread(file_path)
                if image is not None:
                    resized_image = cv2.resize(image, (IMG_WIDTH, IMG_HEIGHT))
                    images.append(resized_image)
                    labels.append(category)
                else:
                    print(f"Warning: Unable to read image {file_path}")

    return images, labels


def get_model():
    """
    Returns a compiled convolutional neural network model. Assume that the
    `input_shape` of the first layer is `(IMG_WIDTH, IMG_HEIGHT, 3)`.
    The output layer should have `NUM_CATEGORIES` units, one for each category.
    """
    model = tf.keras.models.Sequential([
        tf.keras.layers.Conv2D(
            32, (3, 3), activation="relu", input_shape=(IMG_WIDTH, IMG_HEIGHT, 3)
        ),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Conv2D(64, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Conv2D(128, (3, 3), activation="relu"),
        tf.keras.layers.MaxPooling2D(pool_size=(2, 2)),
        tf.keras.layers.Flatten(),
        tf.keras.layers.Dense(512, activation="relu"),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(NUM_CATEGORIES, activation="softmax")
    ])

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )

    return model


if __name__ == "__main__":
    main()
