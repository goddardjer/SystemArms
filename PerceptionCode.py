#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import time
import numpy as np
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *


class ColorTracker:
    def __init__(self):
        self.range_rgb = {
            'red': (0, 0, 255),
            'blue': (255, 0, 0),
            'green': (0, 255, 0),
            'black': (0, 0, 0),
            'white': (255, 255, 255),
        }
        self.target_color = ('red',)
        self.camera = Camera.Camera()
        self.camera.camera_open()

    def set_target_color(self, target_color):
        self.target_color = target_color

    def resize_and_blur(self, img):
        size = (640, 480)
        frame_resize = cv2.resize(img, size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        return frame_gb

    def convert_to_lab(self, img):
        return cv2.cvtColor(img, cv2.COLOR_BGR2LAB)

    def draw_bounding_box(self, img):
        frame_gb = self.resize_and_blur(img)
        frame_lab = self.convert_to_lab(frame_gb)
        for color in self.target_color:
            frame_mask = cv2.inRange(frame_lab, self.range_rgb[color][0], self.range_rgb[color][1])
            opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
            closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
            contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
            areaMaxContour, area_max = self.get_area_max_contour(contours)
            if area_max > 2500:
                rect = cv2.minAreaRect(areaMaxContour)
                box = np.int0(cv2.boxPoints(rect))
                cv2.drawContours(img, [box], -1, self.range_rgb[i], 2)
                cv2.putText(img, i, (min(box[0, 0], box[2, 0]), box[2, 1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.range_rgb[i], 1)
        return img

    @staticmethod
    def get_area_max_contour(contours):
        contour_area_temp = 0
        contour_area_max = 0
        area_max_contour = None
        for c in contours:
            contour_area_temp = math.fabs(cv2.contourArea(c))
            if contour_area_temp > contour_area_max:
                contour_area_max = contour_area_temp
                if contour_area_temp > 300:
                    area_max_contour = c
        return area_max_contour, contour_area_max

    def run(self):
        while True:
            img = self.camera.frame
            if img is not None:
                frame = img.copy()
                frame = self.draw_bounding_box(frame)
                cv2.imshow('Frame', frame)
                cv2.waitKey(1)


def main():
    # Instantiate the class
    tracker = ColorTracker()

    # Set the target color
    tracker.set_target_color('blue',)

    # Run the color tracking
    tracker.run()

# Call the main function
if __name__ == '__main__':
    main()