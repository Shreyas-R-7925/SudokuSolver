import cv2
import matplotlib.pyplot as plt
import os
import numpy as np
from utils import DigitDetector
from solver import *

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
    # Preprocessing involves three steps
    # 1) Converting the image to grayscale
    # 2) Applying Gaussian Blur to smoothen the image and reduce the noise
    # 3) Adaptive Thresholding to separate objects or regions from the background based on intensity differences.
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

image_path = "images/img6.jpg"

if not os.path.exists(image_path):
    print(f"Error: {image_path} doesn't exist.")
else:
    image = cv2.imread(image_path)
    image = cv2.resize(image, (height, width))
    imgBlank = np.zeros((height, width, 3), np.uint8)
    imgThreshold = preProcess(image)
    if image is None:
        print(f"Error in displaying the image {image}")
    else:
        imageCopy = image.copy()
        imgBigContour = image.copy()
        contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cv2.drawContours(imageCopy, contours, -1, (0, 255, 0), 3)
        plt.imshow(cv2.cvtColor(imageCopy, cv2.COLOR_BGR2RGB))
        plt.show()

        largest, maxArea = largestContour(contours)
        if largest.size != 0:
            largest = reorder(largest)
            cv2.drawContours(imgBigContour, largest, -1, (0, 0, 255), 25)
            point1 = np.float32(largest)
            point2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
            matrix = cv2.getPerspectiveTransform(point1, point2)
            imgWarpColored = cv2.warpPerspective(image, matrix, (width, height))
            imgDetectedDigits = imgBlank.copy()
            imgWarpColored = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)

            imgSolvedDigits = imgBlank.copy()
            boxes = splitBoxes(imgWarpColored)
            for i in range(0, 1):
                plt.imshow(cv2.cvtColor(boxes[i], cv2.COLOR_BGR2RGB))
                plt.title("Sample")
                plt.show()

            numbers = getPrediction(boxes, model)
            board = constructBoard(numbers)

            solution = Solution()
            solution.solveSudoku(board)
            solution.printBoard(board)
            solvedImage = displayNumbers(imgWarpColored.copy(), board, color=(0, 255, 0))
            plt.imshow(cv2.cvtColor(solvedImage, cv2.COLOR_BGR2RGB))
            plt.title('Solved Sudoku')
            plt.show()
