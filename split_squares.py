from imutils.contours import sort_contours
import numpy as np
import cv2
import sys
import os
# Other
from constants import IMAGE_PATH, SQUARES_FOLDER


def process_image(original_img):
    """
    Performs basic processing on the loaded image
    :param original_img: Original image loaded from IMAGE_PATH
    :return: Processed image
    """
    # Converting the image to grayscale
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)

    # de-noising the image and applying the threshold
    blur = cv2.GaussianBlur(gray, (9, 9), 0)
    thresh = cv2.adaptiveThreshold(blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # de-noising the image again so contours can be found more easily
    kernel = np.ones((3, 3))
    thresh = cv2.erode(thresh, kernel)
    thresh = cv2.dilate(thresh, kernel)

    return thresh


def process_sudoku(sudoku_img, field_area):
    """
    Does all processing and function calls related to finding squares and splitting the sudoku grid into 81(9x9) images.
    """
    original_img = sudoku_img.copy()
    processed_img = process_image(original_img)

    # Detecting lines
    lines = cv2.HoughLinesP(processed_img, 1, np.pi / 180, 120, np.array([]), minLineLength=100, maxLineGap=20)

    for line in lines:
        for x1, y1, x2, y2 in line:
            # Drawing lines over the grid
            cv2.line(original_img, (x1, y1), (x2, y2), (255, 0, 0), 2)

    # Grayscaling and applying threshold to find squares more easily
    gray = cv2.cvtColor(original_img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # Finding all of the contours
    cnts, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    squares = []
    # Filtering only the squares(9x9)
    for c in cnts:
        area = cv2.contourArea(c)
        if field_area / 130 < area < field_area / 70:  # check if contour is valid size(square size)
            squares.append(c)

    sudoku_rows = sort_squares(squares)
    split_squares(sudoku_img, sudoku_rows)


def sort_squares(squares):
    """
    Sorts contours of sudoku squares in proper order
    :return: A 9x9 array with properly sorted square contours
    """
    # Sorting from top to bottom
    (boxes, _) = sort_contours(squares, method='top-to-bottom')

    sudoku_rows = []
    row = []
    for (i, c) in enumerate(boxes, 1, ):
        row.append(c)
        if i % 9 == 0:
            # Sorts the row from left to right every 9 iterations and resets it
            (row, _) = sort_contours(row, method="left-to-right")
            sudoku_rows.append(row)
            row = []

    return sudoku_rows


def split_squares(sudoku_img, sudoku_rows):
    """
    Splits the sudoku grid as 81 images of each square and saves them ordered as they appear on the grid

    :param sudoku_img: cropped image of the sudoku grid
    :param sudoku_rows: 'square' sudoku contours sorted in proper order
    """
    gray_sudoku = cv2.cvtColor(sudoku_img, cv2.COLOR_BGR2GRAY)

    if not os.path.exists(SQUARES_FOLDER):
        os.makedirs(SQUARES_FOLDER)
    i = 1
    for row in sudoku_rows:
        for cnt in row:
            x, y, w, h = cv2.boundingRect(cnt)
            square_img = gray_sudoku[y: y + h, x: x + w]
            # Resize images to 28x28 to fit the model
            square_img = cv2.resize(square_img, (28, 28))
            print(f'[*] Saving square: {i}')
            cv2.imwrite(f'{SQUARES_FOLDER}/{i}.jpg', square_img)
            i += 1


def get_squares():
    """
    Combines all functions in the split_squares module to extract sudoku grid from an image and split it to 81 images of
    each square
    """
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        print('[!] Image not found!')
        sys.exit(0)

    # Processing the image
    processed_img = process_image(image.copy())

    # Finding only extreme outer contours
    contours, _ = cv2.findContours(processed_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Getting the contour with the largest area(the sudoku grid)
    max_cnt_area = 0
    largest_cnt = 0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area > max_cnt_area:
            max_cnt_area = area
            largest_cnt = cnt

    # Selecting and cropping part of the image that is the sudoku grid
    x, y, w, h = cv2.boundingRect(largest_cnt)
    sudoku_image = image[y: y + h, x: x + w]
    # Getting squares
    process_sudoku(sudoku_image, max_cnt_area)



