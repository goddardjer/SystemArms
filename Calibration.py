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

# Multiply the grid by 75mm, which is the size of your squares
objp = objp * 75

# Open the camera
cap = cv2.VideoCapture(0)

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

        # Print the parameters
        print("Retval: ", ret)
        print("Camera matrix : \n", mtx)
        print("Distortion coefficient : \n", dist)
        print("Rotation Vectors : \n", rvecs)
        print("Translation vectors : \n", tvecs)

        # Calculate and print the distance
        distance = np.sqrt(np.sum(np.square(tvecs[-1])))
        print("Estimated distance: ", distance)

        # Break the loop
        #break

    cv2.imshow('img',img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()