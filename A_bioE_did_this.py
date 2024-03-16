import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
import numpy as np
import time
import threading

##########################################################

class CircleDetector:
    def __init__(self):
        self.target_color = 'black'
        self.camera = Camera.Camera()
        self.camera.camera_open()
        self.size = (640, 480)
        self.center_x = None
        self.center_y = None

    def process_frame(self, frame):
        frame_resize = cv2.resize(frame, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        return frame_lab

    def draw_circles(self, frame, frame_lab):
        frame_mask = cv2.inRange(frame_lab, color_range[self.target_color][0], color_range[self.target_color][1])
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
        circles = cv2.HoughCircles(closed, cv2.HOUGH_GRADIENT, dp=1, minDist=50, param1=70, param2=20, minRadius=15, maxRadius=400)

        if circles is not None:
            circles = np.uint16(np.around(circles))
            for i in circles[0, :]:
                self.center_x, self.center_y = convertCoordinate(i[0], i[1], self.size)
                cv2.circle(frame, (i[0], i[1]), i[2], (0, 255, 0), 2)
                cv2.circle(frame, (i[0], i[1]), 2, (0, 0, 255), 3)
                cv2.putText(frame, self.target_color, (i[0], i[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 1)
                cv2.putText(frame, f'x: {self.center_x:.2f}, y: {self.center_y:.2f}', (i[0], i[1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 1)

    def get_circle_center(self):
        return self.center_x, self.center_y


    def run(self):
        try:
            while True:
                img = self.camera.frame
                if img is not None:
                    frame = img.copy()
                    frame_lab = self.process_frame(frame)
                    self.draw_circles(frame, frame_lab)
                    cv2.imshow('Frame', frame)
                    key = cv2.waitKey(1)
                    if key == 27:  # ESC key to break
                        break

                    if self.center_x is not None and self.center_y is not None:
                        return self.center_x, self.center_y
        finally:
            self.camera.camera_close()
            cv2.destroyAllWindows()

###########################################################

class Interpreter:
    def __init__(self):
        pass

    def interpolate_servoH(self, CV_H):
        CV_H_values = [-8, 0, 8]
        Servo_H_values = [540, 500, 450]
        return np.interp(CV_H, CV_H_values, Servo_H_values)

    def interpolate_servoV(self, CV_V):
        CV_V_values = [0, 240]  # Adjust these values based on your setup
        Servo_V_values = [130, 100]  # Adjust these values based on your setup
        return np.interp(CV_V, CV_V_values, Servo_V_values)

    def run(self, center_x, center_y):
        ServoH = self.interpolate_servoH(center_x)
        ServoV = self.interpolate_servoV(center_y)
        return ServoH, ServoV


class Moving:
    def __init__(self):
        self.servo_horizontal = 500  # Initial position for horizontal servo
        self.servo_vertical = 100    # Initial position for vertical servo

    def open_hand(self):
        Board.setBusServoPulse(1, 500 - 450, 500)
        time.sleep(0.8)

    def close_hand(self):
        Board.setBusServoPulse(1, 500, 500)
        time.sleep(0.8)

    def fire(self):
        self.open_hand()

    def move_to_target(self, servo_horizontal, servo_vertical):
        Board.setBusServoPulse(6, servo_horizontal, 500)
        Board.setBusServoPulse(3, servo_vertical, 500)

def run_interpreter_and_move(interpreter, moving, circledetect):
    center_x, center_y = circledetect.run()
    servoH, servoV = interpreter.run(center_x, center_y)
    moving.move_to_target(int(servoH), int(servoV))
    moving.fire()
    moving.close_hand()

if __name__ == '__main__':
    circledetect = CircleDetector()
    interpreter = Interpreter()
    moving = Moving()
    moving.close_hand()

    run_interpreter_and_move(interpreter, moving, circledetect)

    print("Done")
