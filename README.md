# pi-pyniryo-oakdsr
Run NED &amp; OAK-D-SR from a Pi

First, clone this repository to your Pi.

`git clone https://github.com/hyloc-dev/pi-pyniryo-oakdsr`

Afterwards, you will need to enter the folder within your Pi.

`cd pi-pyniryo-oakdsr`

At this stage, you will need to launch the following command so that the Niryo library is installed on the Pi.

`pip install -r requirements.txt`

Before launching any routines or tests, you will also have to ensure that your Pi is on the same network as the Niryo. If you are using the Robot hotspot, ensure that the Robot's IP address has been set to "10.10.10.10" for any routines. Otherwise, use the IP address on your desired network.

This repository will be updated to include instructions for installing the OAK-D-SR custom branch. See documentation here: [Link](https://docs.google.com/document/d/1hlznYsO-OxvtL1uhkDoJ9PkRrED_PsSP3CEVlt9JooY/edit?usp=sharing)


