#!/usr/bin/env python3

import cam_grab
import time
from pathlib import Path
import cv2
import depthai as dai
from pyniryo import *

# Booting and Calibrating Robot

robot_ip_address = "169.254.200.200"
robot = NiryoRobot(robot_ip_address)
robot.calibrate_auto()
def release():
    robot.release_with_tool()
def grab():
    robot.grasp_with_tool()
def home():
    robot.move_to_home_pose()
    
# home
home()
# Initial mvt
robot.move_pose(0.2,0,0.25,0.0,0.9,0.0)
cam_grab.cam_grab()

# left angle
robot.move_pose(0.3,0.2,0.25,-0.5,0.3,-0.8)
cam_grab.cam_grab()
#
home()
# right angle
robot.move_pose(0.25,-0.2,0.25,0.0,0.3,0.8)
cam_grab.cam_grab()


