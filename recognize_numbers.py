from glob import glob
import numpy as np
import pickle
import keras
import cv2
import re
# Other
from split_squares import get_squares
from constants import SQUARES_FOLDER, MODEL_FILE, LABELS


# Initializing the extract_squares module
get_squares()

# Gets all square images paths and sorts them in order as they were saved
all_img_files = sorted(glob(f'{SQUARES_FOLDER}/*.jpg'), key=lambda x: int(re.findall(r'\d+', x)[0]))

# Load model and binarized labels
model = keras.models.load_model(MODEL_FILE)
with open(LABELS, "rb") as f:
    lb = pickle.load(f)


def process_img(image):
    """
    Cleans up the image in several steps to make it easier for the model to recognize digits
    """
    original_img = image.copy()
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    # Blur the image and perform Non-local means denoising to the gaussian noise
    blur = cv2.GaussianBlur(gray, (3, 3), 0)
    dst = cv2.fastNlMeansDenoising(blur, None, 3, 3, 9)

    thresh = cv2.adaptiveThreshold(dst, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 9, 2)

    # Further image cleanup by erasing smaller black spots
    kernel = np.ones((2, 2))
    thresh = cv2.erode(thresh, kernel)
    # If there are any outer lines left over, remove them
    thresh[:2, :] = 0
    thresh[-2:, :] = 0
    thresh[:, -2:] = 0
    thresh[:, :2] = 0
    # Make the number object bigger again
    thresh = cv2.dilate(thresh, kernel)

    return thresh


def predict_value(square_img):
    """
    Recognizing the number that's in the square
    """
    square_img = square_img / 255
    square_img = square_img.reshape((1, 28, 28, 1))
    prediction = model.predict(square_img)
    predicted = lb.inverse_transform(prediction)[0]
    return predicted


def form_sudoku_grid():
    """
    :return: sudoku grid, ordered as it was on the picture and represented as array of 9x9
    """
    count_y = 0
    sudoku_row = []
    sudoku_grid = []
    # Going through all square images and checking if they are empty or not
    for n, img in enumerate(all_img_files, start=1):

        image = cv2.imread(img)
        processed_img = process_img(image)
        if processed_img[8:19, 8:19].sum() > 4335:  # = 255*17
            # If the square contains a number, recognize it
            sudoku_row.append(predict_value(processed_img))
            count_y += 1
        else:
            # If the square is empty, mark it as 0
            sudoku_row.append(0)

        if n % 9 == 0:
            # Every 9 iterations append row to the grid and reset it
            sudoku_grid.append(sudoku_row)
            sudoku_row = []

    print(f'Found {count_y} numbers. \n')
    return sudoku_grid

