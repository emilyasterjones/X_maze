# X_maze
Build files and scripts for an automated delayed (non)match to direction task, with simultaneous video recording and TTL pulses to synchronize to additional data streams

This task is derived from the H maze, originally published in [(Seigle & Wilson, 2014)](https://elifesciences.org/articles/03061) with a detailed protocol published in [(Wirtshafter, Quan, & Wilson, 2021)](https://bio-protocol.org/e3947).

### GigE Allied Vision Camera Acquisition Instructions
1. Configure Ethernet Card
	1. Configure ethernet card according to [these settings](https://www.alliedvision.com/fileadmin/content/documents/products/cameras/various/installation-manual/GigE_Installation_Manual.pdf)
	1. [Turn off unnecessary protocols](https://www.mathworks.com/help/supportpkg/gigevisionhardware/ug/configure-gigabit-ethernet-network-adapter-on-windows.html#bu10a4b)
	1. [Set the camera's network to private](https://supportcenter.pleora.com/s/article/Correcting-Firewall-Issues-with-Third-Party-GigE-Vision-Devices-KBase)
1. Install OpenCV and Vimba SDK for Python
	1. `pip install opencv-python`
	1. Vimba => modify => select Vimba Python
	1. `pip install "C:/Program Files/Allied Vision/Vimba_X.X/VimbaPython/Source"` where x is whatever your version is
	
### FLIR Blackfly S USB3 Camera Acquisition Instructions
1. Install [SpinView](https://www.flir.com/products/spinnaker-sdk) to set camera settings and stream and record video.
1. Read the [Blackfly S Manual](https://www.eureca.de/files/pdf/optoelectronics/flir/BFS-Installation-Guide.pdf).
1. To set up PySpinCapture to record using the GPU:
	1. 


[Visual Studio (2022)](https://visualstudio.microsoft.com/)
[CUDA Toolkit 12.2](https://developer.nvidia.com/cuda-downloads)
[NVIDIA Video Codec SDK (12.1)](https://developer.nvidia.com/nvidia-video-codec-sdk/download)
[Python (3.8)](https://www.python.org/downloads/)
[Python Spinnaker SDK for your Python version](https://www.flir.com/support-center/iis/machine-vision/downloads/spinnaker-sdk-download/spinnaker-sdk--download-files/)
[FFmpeg (6.0)](https://ffmpeg.org/download.html)
`conda create -n flir python=3.8`
`pip install skikit-video`