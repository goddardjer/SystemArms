#!/usr/bin/python3
# coding=utf8

import sys
sys.path.append('/home/pi/ArmPi/')

import cv2
import time
import Camera
import threading
import math
from LABConfig import *
from ArmIK.Transform import *
from ArmIK.ArmMoveIK import *
import HiwonderSDK.Board as Board
from CameraCalibration.CalibrationConfig import *

servo1 = 500

AK = ArmIK()

# Function to move the arm to the target position
def move_to_target(x, y, z, pitch1, pitch2):
    result = AK.setPitchRangeMoving((x, y, z), pitch1, pitch2, 1000)
    if result == False:
        print("Unreachable")
    else:
        time.sleep(result[2]/1000)

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Move the robotic arm to a specified position.')
    parser.add_argument('x', type=float, help='X coordinate')
    parser.add_argument('y', type=float, help='Y coordinate')
    parser.add_argument('z', type=float, help='Z coordinate')
    parser.add_argument('pitch1', type=int, help='Pitch 1')
    parser.add_argument('pitch2', type=int, help='Pitch 2')
    args = parser.parse_args()

    

    # Move the arm to the target position
    move_to_target(args.x, args.y, args.z, args.pitch1, args.pitch2)