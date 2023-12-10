from pathlib import Path
import sys
import cv2
import depthai as dai
import numpy as np
import time


from pyniryo import *

# ROBOT CALIBRATION & BOOT

# robot_ip_address = "10.0.0.32"

robot_ip_address = "10.10.10.10" #if on hotspot ; pw is niryorobot

# Connect to robot 

robot = NiryoRobot(robot_ip_address)

# Calibrate   
robot.calibrate_auto()

def release():
    robot.release_with_tool()
def grab():
    robot.grasp_with_tool()
def home():
    robot.move_to_home_pose()

# Look to evaluate and check if we're in frame
x,y,z,a,b,c = 0.33, 0.0, 0.20, -0.1, 0.8, 0.0
robot.move_pose(x,y,z,a,b,c) 

# EVAL 

# Get argument first
nnPath = str((Path(__file__).parent / Path('../models/mobilenet-ssd_openvino_2021.4_6shave.blob')).resolve().absolute())
if len(sys.argv) > 1:
    nnPath = sys.argv[1]

if not Path(nnPath).exists():
    import sys
    raise FileNotFoundError(f'Required file/s not found, please run "{sys.executable} install_requirements.py"')

# MobilenetSSD label texts
labelMap = ["dome_cover"]

syncNN = True

# Create pipeline
pipeline = dai.Pipeline()

# Define sources and outputs
monoLeft = pipeline.create(dai.node.MonoCamera)
monoRight = pipeline.create(dai.node.MonoCamera)
stereo = pipeline.create(dai.node.StereoDepth)
spatialDetectionNetwork = pipeline.create(dai.node.MobileNetSpatialDetectionNetwork)
imageManip = pipeline.create(dai.node.ImageManip)

xoutManip = pipeline.create(dai.node.XLinkOut)
nnOut = pipeline.create(dai.node.XLinkOut)
depthRoiMap = pipeline.create(dai.node.XLinkOut)
xoutDepth = pipeline.create(dai.node.XLinkOut)

xoutManip.setStreamName("right")
nnOut.setStreamName("detections")
depthRoiMap.setStreamName("boundingBoxDepthMapping")
xoutDepth.setStreamName("depth")

# Properties
imageManip.initialConfig.setResize(300, 300)
# The NN model expects BGR input. By default ImageManip output type would be same as input (gray in this case)
imageManip.initialConfig.setFrameType(dai.ImgFrame.Type.BGR888p)

monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

# StereoDepth
stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)

# Define a neural network that will make predictions based on the source frames
spatialDetectionNetwork.setConfidenceThreshold(0.5)
spatialDetectionNetwork.setBlobPath(nnPath)
spatialDetectionNetwork.input.setBlocking(False)
spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
spatialDetectionNetwork.setDepthLowerThreshold(100)
spatialDetectionNetwork.setDepthUpperThreshold(5000)

# Linking
monoLeft.out.link(stereo.left)
monoRight.out.link(stereo.right)

imageManip.out.link(spatialDetectionNetwork.input)
if syncNN:
    spatialDetectionNetwork.passthrough.link(xoutManip.input)
else:
    imageManip.out.link(xoutManip.input)

spatialDetectionNetwork.out.link(nnOut.input)
spatialDetectionNetwork.boundingBoxMapping.link(depthRoiMap.input)

stereo.rectifiedRight.link(imageManip.inputImage)
stereo.depth.link(spatialDetectionNetwork.inputDepth)
spatialDetectionNetwork.passthroughDepth.link(xoutDepth.input)

# Connect to device and start pipeline
with dai.Device(pipeline) as device:

    # Output queues will be used to get the rgb frames and nn data from the outputs defined above
    previewQueue = device.getOutputQueue(name="right", maxSize=4, blocking=False)
    detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
    depthRoiMapQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
    depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

    rectifiedRight = None
    detections = []

    startTime = time.monotonic()
    counter = 0
    fps = 0
    color = (0, 255, 0)

    list_of_dist = []
    # while True:
    t_end = time.time() + 5
    while time.time() < t_end:
        inRectified = previewQueue.get()
        inDet = detectionNNQueue.get()
        inDepth = depthQueue.get()

        counter += 1
        currentTime = time.monotonic()
        if (currentTime - startTime) > 1:
            fps = counter / (currentTime - startTime)
            counter = 0
            startTime = currentTime

        rectifiedRight = inRectified.getCvFrame()

        depthFrame = inDepth.getFrame() # depthFrame values are in millimeters

        depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
        depthFrameColor = cv2.equalizeHist(depthFrameColor)
        depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

        detections = inDet.detections
        if len(detections) != 0:
            boundingBoxMapping = depthRoiMapQueue.get()
            roiDatas = boundingBoxMapping.getConfigData()

            for roiData in roiDatas:
                roi = roiData.roi
                roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
                topLeft = roi.topLeft()
                bottomRight = roi.bottomRight()
                xmin = int(topLeft.x)
                ymin = int(topLeft.y)
                xmax = int(bottomRight.x)
                ymax = int(bottomRight.y)
                cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

        # If the rectifiedRight is available, draw bounding boxes on it and show the rectifiedRight
        height = rectifiedRight.shape[0]
        width = rectifiedRight.shape[1]
        for detection in detections:
            # Denormalize bounding box
            x1 = int(detection.xmin * width)
            x2 = int(detection.xmax * width)
            y1 = int(detection.ymin * height)
            y2 = int(detection.ymax * height)

            try:
                label = labelMap[detection.label]
            except:
                label = detection.label

            #cv2.putText(rectifiedRight, str(label), (x1 + 10, y1 + 20), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(rectifiedRight, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(rectifiedRight, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(rectifiedRight, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            cv2.putText(rectifiedRight, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, (0,255,0))
            # print("x",int(detection.spatialCoordinates.x))
            # print("y",int(detection.spatialCoordinates.y))
            #print("z",int(detection.spatialCoordinates.z))
            list_of_dist.append(int(detection.spatialCoordinates.z))
            cv2.rectangle(rectifiedRight, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

        cv2.putText(rectifiedRight, "NN fps: {:.2f}".format(fps), (2, rectifiedRight.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)
        cv2.imshow("depth", depthFrameColor)
        cv2.imshow("rectified right", rectifiedRight)
        if cv2.waitKey(1) == ord('q'):
            break
    if len(list_of_dist) > 5:
        print(" ")
        print("Object detected, robot in frame!")

# Now do the mvts

x,y,z,a,b,c = 0.4, 0.0, 0.20, -0.1, 0.3, 0.0
robot.move_pose(x,y,z,a,b,c)

release()

x,y,z,a,b,c = 0.4, 0.0, 0.16, -0.1, 0.3, 0.0
robot.move_pose(x,y,z,a,b,c) # lower

grab()

z += 0.01
robot.move_pose(x,y,z,a,b,c) # higher
z += 0.01
robot.move_pose(x,y,z,a,b,c) # higher
z += 0.01
robot.move_pose(x,y,z,a,b,c) # higher
z += 0.01
robot.move_pose(x,y,z,a,b,c) # higher
z += 0.02
robot.move_pose(x,y,z,a,b,c) # higher

x -= 0.07
robot.move_pose(x,y,z,a,b,c) # back out slowly 
x -= 0.07
robot.move_pose(x,y,z,a,b,c) # back out slowly
x -= 0.07
robot.move_pose(x,y,z,a,b,c) # back out slowly 

z -= 0.03
robot.move_pose(x,y,z,a,b,c)
b = 0.7
robot.move_pose(x,y,z,a,b,c)
release()
print(" ")
print("Finished routine")

