
import depthai as dai
import time

def record_oak(duration_seconds=5):
    # Create pipeline
    pipeline = dai.Pipeline()

    # Define sources and output
    camRgb = pipeline.create(dai.node.ColorCamera)
    videoEnc = pipeline.create(dai.node.VideoEncoder)
    xout = pipeline.create(dai.node.XLinkOut)

    xout.setStreamName('h265')

    # Properties
    camRgb.setBoardSocket(dai.CameraBoardSocket.CAM_A)
    camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_4_K)
    videoEnc.setDefaultProfilePreset(30, dai.VideoEncoderProperties.Profile.H265_MAIN)

    # Linking
    camRgb.video.link(videoEnc.input)
    videoEnc.bitstream.link(xout.input)

    # Connect to device and start pipeline
    with dai.Device(pipeline) as device:
        # Output queue will be used to get the encoded data from the output defined above
        q = device.getOutputQueue(name="h265", maxSize=30, blocking=True)

        # The .h265 file is a raw stream file (not playable yet)
        with open('video.h265', 'wb') as videoFile:
            print(f"Recording for {duration_seconds} seconds. Press Ctrl+C to stop encoding...")
            start_time = time.time()

            try:
                while time.time() - start_time < duration_seconds:
                    h265Packet = q.get()  # Blocking call, will wait until new data has arrived
                    h265Packet.getData().tofile(videoFile)  # Appends the packet data to the opened file
            except KeyboardInterrupt:
                # Keyboard interrupt (Ctrl + C) detected
                pass

        print("Recording complete. To view the encoded data, convert the stream file (.h265) into a video file (.mp4) using ffmpeg on Linux or HandBrake on Mac")

# Call the function with the default duration (5 seconds)
record_oak()

# Call the function with a custom duration (e.g., 10 seconds)
# record_oak(duration_seconds=10)

