import sys
sys.path.append('/home/pi/ArmPi/')
import cv2
import Camera
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *
import keyboard

class Moving:
    def __init__(self):
        self.AK = ArmIK()
        self.coordinate = {
            'red':   (-15 + 0.5, 12 - 0.5, 1.5),
            'green': (-15 + 0.5, 6 - 0.5,  1.5),
            'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
        }
        self.rotation_angle = 0
        self.x = 0
        self.y = 10
        self.z = 10

    def initMove(self):
        Board.setBusServoPulse(1, 500 - 50, 300)
        Board.setBusServoPulse(2, 500, 500)
        self.AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)

    def move_arm_with_keyboard(self):
        while True:
            if keyboard.is_pressed('w'):  # if key 'w' is pressed 
                self.y += 5
            elif keyboard.is_pressed('s'):  # if key 's' is pressed 
                self.y -= 5
            elif keyboard.is_pressed('a'):  # if key 'a' is pressed 
                self.x -= 5
            elif keyboard.is_pressed('d'):  # if key 'd' is pressed 
                self.x += 5
            elif keyboard.is_pressed('q'):  # if key 'q' is pressed 
                self.z -= 5
            elif keyboard.is_pressed('e'):  # if key 'e' is pressed 
                self.z += 5
            elif keyboard.is_pressed('x'):  # if key 'x' is pressed 
                break

            result = self.AK.setPitchRangeMoving((self.x, self.y, self.z), -90, -90, 0, 1000)
            if result:
                print(f'x: {self.x}, y: {self.y}, z: {self.z}')
                time.sleep(result[2]/1000)

if __name__ == '__main__':
    moving = Moving()
    moving.initMove()
    moving.move_arm_with_keyboard()