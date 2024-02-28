#!/usr/bin/python3
# coding=utf8
import sys
sys.path.append('/home/pi/ArmPi/')
import time
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board

AK = ArmIK()

# Global variable for the target position
target_position = (0, 0, 0)

# Function to move the arm to the target position
def move_to_target():
    global target_position
    x, y, z = target_position
    result = AK.setPitchRangeMoving((x, y, z), -90, -90, 0)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)

if __name__ == '__main__':
    # Set the target position
    target_position = (-15 + 0.5, 12 - 0.5, 1.5)
    # Move the arm to the target position
    move_to_target()