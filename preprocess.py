import cv2
import numpy as np
from utils import DigitDetector
from solver import Solution

height = 450
width = 450
model = DigitDetector()

def constructBoard(numbers):
    board = []
    k = 0
    for i in range(9):
        row = []
        for j in range(9):
            row.append(numbers[k])
            k += 1
        board.append(row)
    return board

def preProcess(img):
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, 1, 1, 11, 2)
    return imgThreshold

def largestContour(contours):
    largest = np.array([])
    maxArea = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 50:
            perimeter = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * perimeter, True)
            if area > maxArea and len(approx) == 4:
                largest = approx
                maxArea = area
    return largest, maxArea

def reorder(points):
    points = points.reshape((4, 2))
    newPoints = np.zeros((4, 1, 2), dtype=np.int32)
    add = points.sum(1)
    newPoints[0] = points[np.argmin(add)]
    newPoints[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    newPoints[1] = points[np.argmin(diff)]
    newPoints[2] = points[np.argmax(diff)]
    return newPoints

def splitBoxes(img):
    rows = np.vsplit(img, 9)
    boxes = []
    for r in rows:
        cols = np.hsplit(r, 9)
        for grid in cols:
            resized_grid = cv2.resize(grid, (28, 28))  # Resize to 28x28 pixels
            boxes.append(resized_grid)
    return boxes

def getPrediction(boxes, model):
    result = []
    for image in boxes:
        img = np.asarray(image)
        img = img[4: img.shape[0] - 4, 4:img.shape[1] - 4]
        img = cv2.resize(img, (28, 28))
        img = img / 255.0
        img = img.reshape(1, 28, 28, 1)

        predictions = model.predict(img)
        classIndex = np.argmax(predictions, axis=-1)
        probValue = np.amax(predictions)
        if probValue > 0.8:
            result.append(classIndex[0] + 1)  # Adjust by adding 1
        else:
            result.append(0)
    return result

def displayNumbers(img, board, color=(255, 255, 255)):
    secW = int(img.shape[1] / 9)
    secH = int(img.shape[0] / 9)
    for y in range(9):
        for x in range(9):
            if board[y][x] != 0:
                cv2.putText(img, str(board[y][x]),
                            (x * secW + int(secW / 2) - 10, int((y + 0.8) * secH)),
                            cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, color, 2, cv2.LINE_AA)
    return img
