import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
from LABConfig import *
from Camera import Camera
import numpy as np

class CircleDetector:
    def __init__(self):
        self.target_color = 'black'
        self.camera = Camera()
        self.camera.camera_open()
        self.size = (640, 480)

    def process_frame(self, frame):
        frame_resize = cv2.resize(frame, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        return frame_lab

    def detect_circles(self, frame_lab):
        frame_mask = cv2.inRange(frame_lab, color_range[self.target_color][0], color_range[self.target_color][1])
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
        circles = cv2.HoughCircles(closed, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=70, param2=20, minRadius=15, maxRadius=400)

        detected_circles = []
        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                center_x, center_y = i[0], i[1]
                detected_circles.append((center_x, center_y))
        return detected_circles

    def run(self):
        while True:
            img = self.camera.frame
            if img is not None:
                frame_lab = self.process_frame(img)
                circles = self.detect_circles(frame_lab)
                if circles:
                    print("Detected circles:", circles)
                    # Extract coordinates and perform further actions here
                cv2.imshow('Frame', img)
                key = cv2.waitKey(1)
                if key == 27:  # ESC key to break
                    break

        self.camera.camera_close()
        cv2.destroyAllWindows()

if __name__ == '__main__':
    circledetect = CircleDetector()
    circledetect.run()
