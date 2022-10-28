from skimage import io
import cv2
import numpy as np
import imutils
from tensorflow.keras.models import load_model


# Read image
input_size = 48
classes = np.arange(0, 10)
model = load_model('./src/model-OCR.h5')

## cv2.imshow("Input Image", img)


def get_perspective(img, location, height=900, width=900):
    """Takes an image and location os interested region.
        And return the only the selected region with a perspective transformation"""
    pts1 = np.float32([location[0], location[3], location[1], location[2]])
    pts2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])

    # Apply Perspective Transform Algorithm
    matrix = cv2.getPerspectiveTransform(pts1, pts2)
    result = cv2.warpPerspective(img, matrix, (width, height))
    return result


def find_board(img):
    """Takes an image as input and finds a sudoku board inside of the image"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 13, 20, 20)
    edged = cv2.Canny(bfilter, 30, 180)
    keypoints = cv2.findContours(
        edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)

    newimg = cv2.drawContours(img.copy(), contours, -1, (0, 255, 0), 3)
    # cv2.imshow("Contour", newimg)

    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:15]
    location = None

    # Finds rectangular contour
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 15, True)
        if len(approx) == 4:
            location = approx
            break
    result = get_perspective(img, location)
    return result, location


def split_boxes(board):
    """Takes a sudoku board and split it into 81 cells. 
        each cell contains an element of that board either given or an empty cell."""
    rows = np.vsplit(board, 9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 9)
        for box in cols:
            box = cv2.resize(box, (input_size, input_size))/255.0
            cv2.imshow("Splitted block", box)
            cv2.waitKey(0)
            boxes.append(box)
    cv2.destroyAllWindows()
    return boxes


def displayNumbers(img, numbers, color=(0, 255, 0)):
    """Displays 81 numbers in an image or mask at the same position of each cell of the board"""
    W = int(img.shape[1]/9)
    H = int(img.shape[0]/9)
    for i in range(9):
        for j in range(9):
            if numbers[(j*9)+i] != 0:
                cv2.putText(img, str(numbers[(j*9)+i]), (i*W+int(W/2)-int((W/4)), int(
                    (j+0.7)*H)), cv2.FONT_HERSHEY_COMPLEX, 2, color, 2, cv2.LINE_AA)
    return img


def main():
    img = cv2.imread('./data/image3.jpg')

    # extract board from input image
    board, location = find_board(img)

    gray = cv2.cvtColor(board, cv2.COLOR_BGR2GRAY)
    # print(gray.shape)
    rois = split_boxes(gray)
    rois = np.array(rois).reshape(-1, input_size, input_size, 1)

    # get prediction
    prediction = model.predict(rois)
    # print(prediction)

    predicted_numbers = []
    # get classes from prediction
    for i in prediction:
        # returns the index of the maximum number of the array
        index = (np.argmax(i))
        predicted_number = classes[index]
        predicted_numbers.append(predicted_number)

    # print("\nThe extracted numbers are ")
    # print(predicted_numbers)
    # print("\n")
    predicted_number_np = np.array(predicted_numbers)
    np.savetxt('./data/output.txt', predicted_number_np, fmt='%d')


if __name__ == "__main__":
    main()
