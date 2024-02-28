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
        frame_resize = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_NEAREST)
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
            cv2.drawContours(frame, [box], -1, (0, 255, 0), 2)

            # Calculate the center of the contour
            M = cv2.moments(areaMaxContour)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])

            # Display the coordinates at the center of the contour
            cv2.putText(frame, f"({cX}, {cY})", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

    def run(self):
        while True:
            img = self.camera.frame
            if img is not None:
                frame = img.copy()
                frame_lab = self.process_frame(frame)

                for color in self.target_colors:
                    if color in color_range:
                        self.draw_contours(frame, frame_lab, color)

                cv2.imshow('Frame', frame)
                key = cv2.waitKey(1)
                if key == 27:  # ESC key to break
                    break

        self.camera.camera_close()
        cv2.destroyAllWindows()

##########################################################################




##########################################################################

if __name__ == '__main__':
    detector = ColorDetector(target_colors=('red', 'green', 'blue'))
    detector.run()