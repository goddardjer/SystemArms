import cv2
import numpy as np

# Open the video capture
cap = cv2.VideoCapture(0)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Convert the frame to HSV color space
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Define range for bright, more red shade of orange color in HSV
    lower_orange = np.array([0, 100, 100])  # Increase the lower bound of hue
    upper_orange = np.array([20, 255, 255])  # Decrease the upper bound of hue

    # Threshold the HSV image to get only bright, more red shade of orange colors
    mask_orange = cv2.inRange(hsv, lower_orange, upper_orange)

    # Bitwise-AND mask and original frame
    res_orange = cv2.bitwise_and(frame, frame, mask=mask_orange)

    # Convert the orange masked frame to grayscale
    gray = cv2.cvtColor(res_orange, cv2.COLOR_BGR2GRAY)

    # Apply Gaussian blur to the grayscale frame
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Threshold the frame to reveal light regions in the blurred frame
    thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

    # Perform a series of dilations to remove any small blobs of noise from the thresholded frame
    thresh = cv2.dilate(thresh, None, iterations=2)

    # Find contours in the threshold frame
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if len(cnts) == 2 else cnts[1]

    # Calculate the area of the frame
    frame_area = frame.shape[0] * frame.shape[1]

    # Filter contours based on their size relative to the frame
    cnts = [c for c in cnts if frame_area * 1/10 < cv2.contourArea(c) < frame_area * 1/3]

    # If there are any contours
    if cnts:
        # Find the largest contour
        c = max(cnts, key=cv2.contourArea)

        # Compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # Draw the contour and center of the shape on the frame
        cv2.drawContours(frame, [c], -1, (0, 255, 0), 2)
        cv2.circle(frame, (cX, cY), 7, (255, 255, 255), -1)

        # Get the HSV value of the center of the contour
        hsv_value = hsv[cY, cX]

        # Display the HSV value at the center of the contour
        cv2.putText(frame, str(hsv_value), (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    # Display the resulting frame
    cv2.imshow('Frame', frame)

    # Break the loop on 'q' key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture and destroy all windows
cap.release()
cv2.destroyAllWindows()