#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class ColorDetector:
    def __init__(self, target_colors=('red', 'green', 'blue')):
        self.target_colors = target_colors
        self.camera = Camera.Camera()
        self.camera.camera_open()
        self.size = (640, 480)

    def getAreaMaxContour(self, contours):
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

    def process_frame(self, frame):
        frame_resize = cv2.resize(frame, self.size, interpolation=cv2.INTER_NEAREST)
        frame_gb = cv2.GaussianBlur(frame_resize, (11, 11), 11)
        frame_lab = cv2.cvtColor(frame_gb, cv2.COLOR_BGR2LAB)
        return frame_lab

    def draw_contours(self, frame, frame_lab, color):
        frame_mask = cv2.inRange(frame_lab, color_range[color][0], color_range[color][1])
        opened = cv2.morphologyEx(frame_mask, cv2.MORPH_OPEN, np.ones((6, 6), np.uint8))
        closed = cv2.morphologyEx(opened, cv2.MORPH_CLOSE, np.ones((6, 6), np.uint8))
        contours = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2]
        areaMaxContour, area_max = self.getAreaMaxContour(contours)

        if area_max > 2500:
            rect = cv2.minAreaRect(areaMaxContour)
            box = np.int0(cv2.boxPoints(rect))
            cv2.drawContours(frame, [box], -1, (0, 255, 0), 4)
            center_x, center_y = convertCoordinate(np.mean(box[:, 0]), np.mean(box[:, 1]), self.size) # This is what is breaking your code
            
            cv2.putText(frame, color, (box[0][0], box[0][1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), ) # 10 thickness
            cv2.putText(frame, f'x: {center_x:.2f}, y: {center_y:.2f}', (box[0][0], box[0][1] - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 1)

            return color, (center_x, center_y)

        return None, (0, 0)

    def run(self):
        while True:
            img = self.camera.frame
            if img is not None:
                frame = img.copy()
                frame_lab = self.process_frame(frame)

                for color in self.target_colors:
                    if color in color_range:
                        color, (cX, cY) = self.draw_contours(frame, frame_lab, color)
                        if color is not None:
                            cv2.destroyAllWindows()
                            return color, (cX, cY)

                cv2.imshow('Frame', frame)
                key = cv2.waitKey(1)
                if key == 27:  # ESC key to break
                    break

        self.camera.camera_close()
        cv2.destroyAllWindows()

        # Return None and (0, 0) if no block was detected
        return None, (0, 0)
##########################################################################

        

##########################################################################

class Moving:
    def __init__(self):
        self.AK = ArmIK()
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        self.rotation_angle = 0

    def initMove(self):
        Board.setBusServoPulse(1, 500 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def open_hand(self):
        Board.setBusServoPulse(1, 500 - 280, 500)
        time.sleep(0.8)

    def close_hand(self):
        Board.setBusServoPulse(1, 500, 500)
        time.sleep(1)

    def move_to_block(self, x, y, z):
        self.open_hand()
        result = self.AK.setPitchRangeMoving((x, y, z), -90, -90, 1000)
        if result == False:
            print("Unreachable 0")
        else:
            servo2_angle = getAngle(-2, 18, self.rotation_angle)
            Board.setBusServoPulse(2, servo2_angle, 500)
            time.sleep(2.8)
            self.close_hand()

    def move_to_final_location(self, color):
        x, y, z = self.coordinate[color]  # Get coordinates from dictionary using color
        result = self.AK.setPitchRangeMoving((x, y, z + 10), -90, -90, 1000)
        if result == False:
            print("Unreachable 1")
        else:
            time.sleep(result[2]/1000)
        self.lower_block(x, y, z)

    def lower_block(self, x, y, z):
        result = self.AK.setPitchRangeMoving((x, y, z), -90, -90, 1000)
        if result == False:
            print("Unreachable 2")
        else:
            time.sleep(result[2]/1000)
            self.open_hand()
        

    def pick_up_block(self, x, y, z, color):
        self.move_to_block(x, y, z)
        self.move_to_final_location(color) 
        self.AK.setPitchRangeMoving((x, y, z + 12), -90, -90, 0, 1000)
        time.sleep(1)
        self.initMove()
        time.sleep(1.5)
        self.close_hand()



##########################################################################

if __name__ == '__main__':

    detector = ColorDetector(target_colors=('red', 'green', 'blue'))
    moving = Moving()
    while True:
        color, (x, y) = detector.run()
        if color is not None:
            print(f"Detected a {color} block at ({x}, {y})")
            moving.pick_up_block(x, y, 1.5, color)
        else:
            print("No block detected")