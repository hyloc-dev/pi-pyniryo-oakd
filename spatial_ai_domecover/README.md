# Spatial AI

This is probably the most powerful code in the whole repository. While the code itself is short, it 

* Runs on-device decoding instead of on-host, dramatically improving latency and putting no load on the host device
* Returns XYZ of a detected object using the PyTorch -> ONNX converted 'blob' file ; ONNX is closer to the metal and makes the model lightweight (25 MB)
* Trained using YOLOv8, which is a much newer version of YOLO object detection compared to the standard YOLOv5 ; Better performance but much more lightweight

This code is also very generic, meaning that training new models and plug-and-play different blobs can be used to achieve any object detection task, not just dome cover related tasks.
This library integrates easily in Python, which means it will play nicely with Niryo for object detection purposes. Since results are output in real-world cm instead of pixels and this is the convention
that the Niryo robot takes inputs in, there is no further translation or extra step of implementing an extra vector space library -- this part is already taken care of just by the OAK-D camera.
