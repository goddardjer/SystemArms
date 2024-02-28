#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
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

coordinate = {
        'red':   (-15 + 0.5, 12 - 0.5, 1.5),
        'green': (-15 + 0.5, 6 - 0.5,  1.5),
        'blue':  (-15 + 0.5, 0 - 0.5,  1.5),
    }

# Initial position setup
def initMove():
    Board.setBusServoPulse(1, 500 - 50, 300)
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((0, 10, 10), -30, -30, -90, 1500)


rotation_angle = 0

# Function to pick up a block at the specified coordinates
def pick_up_block(x, y, z, color):
    # Pick up the block
    result = AK.setPitchRangeMoving((200, 200, 1.5), -90, -90, 0)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)
        Board.setBusServoPulse(1, 500 - 280, 500)
        servo2_angle = getAngle(200, 200, rotation_angle)
        Board.setBusServoPulse(2, servo2_angle, 500)
        time.sleep(0.8)
        AK.setPitchRangeMoving((200, 200, 2), -90, -90, 0, 1000)
        time.sleep(2)
        Board.setBusServoPulse(1, 500, 500)
        time.sleep(1)

    # Move to the target location
    result = AK.setPitchRangeMoving((x, y, z + 10), -90, -90, 0)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)

    # Lower the block
    result = AK.setPitchRangeMoving((x, y, z), -90, -90, 0)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)
        Board.setBusServoPulse(1, 500 - 280, 500)
        time.sleep(0.8)

    # Release the block
    Board.setBusServoPulse(1, 500, 500)
    time.sleep(1)

    # Return to the initial position
    Board.setBusServoPulse(2, 500, 500)
    AK.setPitchRangeMoving((x, y, z + 12), -90, -90, 0, 1000)
    time.sleep(1)
    initMove()
    time.sleep(1.5)

if __name__ == '__main__':
    initMove()
    pick_up_block(-15 + 0.5, 12 - 0.5, 1.5, 'red')