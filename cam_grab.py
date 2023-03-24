# This successfully grabs 2 good 640 x 480 p pictures in 5 seconds.

import time
from pathlib import Path

import cv2
import depthai as dai

def cam_grab():
    # Start defining a pipeline
    pipeline = dai.Pipeline()

    # Define a source - color camera
    camRgb = pipeline.createColorCamera()
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
    camRgb.setIspScale(2,3)

    # Create RGB output
    xoutRgb = pipeline.createXLinkOut()
    xoutRgb.setStreamName("rgb")
    camRgb.video.link(xoutRgb.input)

    # Create encoder to produce JPEG images
    videoEnc = pipeline.createVideoEncoder()
    videoEnc.setDefaultProfilePreset(camRgb.getVideoSize(), camRgb.getFps(), dai.VideoEncoderProperties.Profile.MJPEG)
    camRgb.video.link(videoEnc.input)

    # Create JPEG output
    xoutJpeg = pipeline.createXLinkOut()
    xoutJpeg.setStreamName("jpeg")
    videoEnc.bitstream.link(xoutJpeg.input)


    # Connect and start the pipeline
    with dai.Device(pipeline) as device:

        # Output queue will be used to get the rgb frames from the output defined above
        qRgb = device.getOutputQueue(name="rgb", maxSize=30, blocking=False)
        qJpeg = device.getOutputQueue(name="jpeg", maxSize=30, blocking=True)

        # Make sure the destination path is present before starting to store the examples
        Path('image_eval_data').mkdir(parents=True, exist_ok=True)

        startx = time.time() + 3
        while time.time() < startx:
            inRgb = qRgb.tryGet()  # Non-blocking call

            if inRgb is not None:
                cv2.imshow("rgb", inRgb.getCvFrame())
            if time.time() > (startx - 0.25):
                for encFrame in qJpeg.tryGetAll():
                    with open(f"image_eval_data/{int(time.time() * 1)}.jpeg", "wb") as f:
                        f.write(bytearray(encFrame.getData()))

# print("Hello")
# input("Would you like to start?")
# cam_grab()
