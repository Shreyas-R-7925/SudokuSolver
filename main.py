from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
import uvicorn
import numpy as np
from io import BytesIO
from PIL import Image
import cv2
import tensorflow as tf
from fastapi.middleware.cors import CORSMiddleware
from utils import DigitDetector
from preprocess import preProcess, largestContour, reorder, splitBoxes, getPrediction, displayNumbers, constructBoard
from solver import Solution

app = FastAPI()

origins = [
    "http://localhost", 
    "http://localhost:5173",
] 

app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

height = 450
width = 450
model = DigitDetector()

def read_file_as_image(data) -> np.ndarray:
    image = np.array(Image.open(BytesIO(data)))
    return image

@app.post("/solve")
async def solve(file: UploadFile = File(...)):
    print(f"Received file: {file.filename}")
    image = read_file_as_image(await file.read())
    image = cv2.resize(image, (height, width))
    imgBlank = np.zeros((height, width, 3), np.uint8)
    imgThreshold = preProcess(image)

    imageCopy = image.copy()
    imgBigContour = image.copy()
    contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest, maxArea = largestContour(contours)
    if largest.size != 0:
        largest = reorder(largest)
        cv2.drawContours(imgBigContour, largest, -1, (0, 0, 255), 25)
        point1 = np.float32(largest)
        point2 = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
        matrix = cv2.getPerspectiveTransform(point1, point2)
        imgWarpColored = cv2.warpPerspective(image, matrix, (width, height))
        imgWarpColored = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)

        boxes = splitBoxes(imgWarpColored)
        numbers = getPrediction(boxes, model)
        board = constructBoard(numbers)

        solution = Solution()
        solution.solveSudoku(board)
        solvedImage = displayNumbers(imgWarpColored.copy(), board, color=(0, 255, 0))

        buf = BytesIO()
        solvedImage = Image.fromarray(solvedImage)
        solvedImage.save(buf, format="JPEG")
        byte_im = buf.getvalue()

        return StreamingResponse(BytesIO(byte_im), media_type="image/jpeg")
    else:
        return {"error": "Sudoku grid not found"}

if __name__ == "__main__":
    uvicorn.run(app, host='localhost', port=8080)
