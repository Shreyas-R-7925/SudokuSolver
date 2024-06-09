# Preprocessing of the image 

import cv2 
import matplotlib.pyplot as plt
import os 
import numpy as np

height = 450
width = 450 

def preProcess(img):
    # Preprocessing involves three steps
    # 1) Converting the image to grayscale
    # 2) Applying Gaussian Blur to smoothen the image and reduce the noise
    # 3) Adaptive Thresholding to separate objects or regions from the background based on intensity differences.
    
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    imgBlur = cv2.GaussianBlur(imgGray, (5,5), 1)
    imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, 1, 1, 11, 2)
    return imgThreshold

def largestContour(contours):
    largest = np.array([])
    maxArea = 0

    for i in contours:
        area = cv2.contourArea(i)
        # area < 50 then it is noise
        if area > 50:
            perimeter = cv2.arcLength(i, True) 
            #finding out corners 
            approx = cv2.approxPolyDP(i, 0.02*perimeter, True)
            if area > maxArea and len(approx) == 4:
                largest = approx 
                maxArea = area
    
    return largest, maxArea 

def reorder(points):
    points = points.reshape((4, 2))
    newPoints = np.zeros((4, 1, 2), dtype=np.int32)
    add  = points.sum(1) 
    newPoints[0] = points[np.argmin(add)]
    newPoints[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    newPoints[1] = points[np.argmin(diff)]
    newPoints[2] = points[np.argmax(diff)]
    return newPoints


# Loading the image 
image_path = "images/img1.jpg" 

# Checking if the image path is correct or not 
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
        cv2.drawContours(imageCopy, contours, -1, (0,255, 0), 3)
        plt.imshow(cv2.cvtColor(imageCopy, cv2.COLOR_BGR2RGB))  # Show the contour-detected image
        # plt.title('Contour Detected Image')
        # plt.show()

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
            # plt.imshow(cv2.cvtColor(imgBigContour, cv2.COLOR_BGR2RGB))
            # plt.title('Largest detected Contour')
            # plt.show()
            # plt.imshow(cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2RGB))
            # plt.title('Sudoku Contour')
            # plt.show()

        

