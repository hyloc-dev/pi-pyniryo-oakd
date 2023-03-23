# Connect to brain API
# import api
# api = API()

from pyniryo import *

# ROBOT CALIBRATION & BOOT
robot_ip_address = "10.10.10.10" # this is assuming you are on Niryo hotspot

# Connect to robot 

robot = NiryoRobot(robot_ip_address)

# Calibrate   
robot.calibrate_auto()

# Talk to the brain API and have the lift go to a set height
# api.lift_go_to(500)

def release():
    robot.release_with_tool()
def grab():
    robot.grasp_with_tool()
def home():
    robot.move_to_home_pose()

home()

# Look to evaluate
x,y,z,a,b,c = 0.3, 0.0, 0.20, -0.1, 0.5, 0.0
robot.move_pose(x,y,z,a,b,c)
# eval = camera.eval_dome_remove()
# if eval == 1:
#	continue
# elif eval == 0:
#	break

x,y,z,a,b,c = 0.4, 0.0, 0.20, -0.1, 0.3, 0.0
robot.move_pose(x,y,z,a,b,c)

release()

x,y,z,a,b,c = 0.4, 0.0, 0.16, -0.1, 0.3, 0.0
robot.move_pose(x,y,z,a,b,c) # lower

grab()

for i in range(3):
	z += 0.01
	robot.move_pose(x,y,z,a,b,c) # higher
z += 0.02
robot.move_pose(x,y,z,a,b,c) # higher

for i in range(2):
	x -= 0.07
	robot.move_pose(x,y,z,a,b,c) 

z -= 0.03
robot.move_pose(x,y,z,a,b,c)
b = 0.7
robot.move_pose(x,y,z,a,b,c)
release()
