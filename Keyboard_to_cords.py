import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

class Moving:
    def __init__(self):
        self.AK = ArmIK()
        self.x = 0
        self.y = 8
        self.z = 24

    def initMove(self):
        Board.setBusServoPulse(1, 500 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 8, 24), -90, -90, 1500)

    def move_arm_with_keyboard(self):
        while True:
            key = input("Enter a key: ")
            if key == 'w':
                self.y += 2
            elif key == 's':
                self.y -= 2
            elif key == 'a':
                self.x -= 2
            elif key == 'd':
                self.x += 5
            elif key == 'q':
                self.z -= 2
            elif key == 'e':
                self.z += 2
            elif key == 'x':
                break

            result = self.AK.setPitchRangeMoving((self.x, self.y, self.z), -90, -90, 1000)
            if result:
                print(f'x: {self.x}, y: {self.y}, z: {self.z}')
                time.sleep(result[2]/1000)

if __name__ == '__main__':
    moving = Moving()
    moving.initMove()
    moving.move_arm_with_keyboard()