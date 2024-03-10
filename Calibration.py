import numpy as np
import cv2

# Define the dimensions of checkerboard
CHECKERBOARD = (5,3)

# Arrays to store object points and image points from all images
objpoints = [] # 3d points in real world space
imgpoints = [] # 2d points in image plane

# Prepare grid and points to display
objp = np.zeros((1, CHECKERBOARD[0] * CHECKERBOARD[1], 3), np.float32)
objp[0,:,:2] = np.mgrid[0:CHECKERBOARD[0], 0:CHECKERBOARD[1]].T.reshape(-1, 2)

# Multiply the grid by 41.5mm, which is the size of your squares
objp = objp * 41.5

# Open the camera
cap = cv2.VideoCapture(0)

distances = []

while True:
    ret, img = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH + cv2.CALIB_CB_FAST_CHECK + cv2.CALIB_CB_NORMALIZE_IMAGE)

    # If found, add object points, image points
    if ret == True:
        objpoints.append(objp)
        imgpoints.append(corners)

        # Draw and display the corners
        cv2.drawChessboardCorners(img, CHECKERBOARD, corners, ret)

        # Calibrate the camera
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

        # Calculate and print the distance
        distance = np.sqrt(np.sum(np.square(tvecs[-1]))) / 1000
        distances.append(distance)

        # If we have 50 distances, break the loop
        if len(distances) == 50:
            break

    cv2.imshow('img',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# Print the average distance
print("Average estimated distance: ", np.mean(distances), " meters")