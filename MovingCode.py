import cv2
import time
import threading
import math
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

AK = ArmIK()

# Initial position setup
def initMove():
    Board.setBusServoPulse(1, servo1 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)


# Function to pick up a block at the specified coordinates
def pick_up_block(x, y, z, color):
    set_rgb(color)
    result = AK.setPitchRangeMoving((x, y - 2, 5), -90, -90, 0)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)
        Board.setBusServoPulse(1, servo1 - 280, 500)
        servo2_angle = getAngle(x, y, rotation_angle)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)
        AK.setPitchRangeMoving((x, y, 2), -90, -90, 0, 1000)
        time.sleep(2)
        Board.setBusServoPulse(1, servo1, 500)
        time.sleep(1)
        Board.setBusServoPulse(2, 500, 500)
        AK.setPitchRangeMoving((x, y, 12), -90, -90, 0, 1000)
        time.sleep(1)
        initMove()
        time.sleep(1.5)
        set_rgb('None')

if __name__ == '__main__':
    initMove()
    pick_up_block(-15 + 0.5, 12 - 0.5, 1.5, 'red')