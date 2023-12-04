# Jason Keller
# September 2021
# =============================================================================
#  Program to set BlackFly S camera settings and acquire frames from 2 synchronized cameras and 
#  write them to a compressed video file. Based on FLIR Spinnaker API example code. This 
#  example uses color cameras with 24-bit RGB pixel format, and also checks camera serial
#  numbers to ensure correct enumeration.
# 
#  The intent is that this program started first, then will wait for triggers
#  on Line 0 (OPTO_IN) from the DAQ system. It is assumed that the DAQ system will provide
#  a specified number of triggers, and that the Line 0 black wires of both cameras are
#  soldered together and driven simultaneously. Both cameras output their "exposure active"
#  signal on Line 1 (OPTO_OUT, the white wire, which is pulled up to 3.3V via a 1.8kOhm resistor 
#  for each camera) so that each frame can be synchronized (DAQ should sample this at ~1kHz+).
#
#  Tkinter is used to provide a simple GUI to display the images, and skvideo 
#  is used as a wrapper to ffmpeg to write H.264 compressed video quickly, using
#  mostly default parameters.
#
#  To setup, you must download an FFMPEG executable and set an environment 
#  variable path to it (as well as setFFmpegPath function below). Other nonstandard
#  dependencies are the FLIR Spinnaker camera driver and PySpin package (see 
#  Spinnaker downloads), and the skvideo package. In this version, hardware encoding is used
#  which requires a compatible NVIDIA GPU with the drives installed before FFMPEG is compiled.
#  See: https://developer.nvidia.com/ffmpeg, https://trac.ffmpeg.org/wiki/HWAccelIntro
#  
#  NOTE: currently there is no check to see if readout can keep up with triggering
#  other that a timeout warning. It is up to the user to determine if the correct number
#  of frames are captured.
#
# Modified by Emily Aery Jones November 2023
# Similar to cameraCapture2colorCamsGpu.py, except with 1 camera
# Fixed a few errors, possibly specific to my build
# (camCapture had a lock on i, so it never increased in the main loop,
# camCapture threw an error once camera was de-initialized instead of stopping)
# Added an output file of frame number and timestamp 
# =============================================================================

import PySpin, time, os, threading, queue
import sys, csv
from datetime import datetime
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np
import skvideo
skvideo.setFFmpegPath('C:/Users/Muspelheim1/AppData/Local/Programs/ffmpeg_OLD/bin') #set path to ffmpeg installation before importing io
import skvideo.io

#constants
SAVE_FOLDER_ROOT = 'C:/Users/Muspelheim1/Desktop/Video'
EXPOSURE_TIME = 8335 #in microseconds
WAIT_TIME = 0.0001 #in seconds - this limits polling time and should be less than the frame rate period 
GAIN_VALUE = 30 #in dB, 0-40;
GAMMA_VALUE = 1 #0.25-1
IMAGE_HEIGHT = 1200  #540 pixels default; this should be divisible by 16 for H264 compressed encoding
IMAGE_WIDTH = 1920 #720 pixels default; this should be divisible by 16 for H264 compressed encoding
HEIGHT_OFFSET = 0 #600 #16 #round((540-IMAGE_HEIGHT)/2) # Y, to keep in middle of sensor; must be divisible by 4
WIDTH_OFFSET = 0 #960 #104# round((720-IMAGE_WIDTH)/2) # X, to keep in middle of sensor; must be divisible by 4
#FRAMES_PER_SECOND = 60 #this is determined by triggers sent from behavior controller
CAM_TIMEOUT = 1000 #in ms; time to wait for another image before aborting
#FRAME_RATE_OUT = FRAMES_PER_SECOND #can alter ouput frame rate if necessary, but note that H264 limits this for playback, and this slows down video FFMPEG encoding dramatically

# generate output video directory and filename and make sure not overwriting
saveFolder = SAVE_FOLDER_ROOT
if not os.path.exists(saveFolder):
    os.mkdir(saveFolder)
os.chdir(saveFolder)
movieName = sys.argv[1] + '.mp4'
fullFilePath = [saveFolder + '/' + movieName]
frame_info_file = saveFolder + '/' + sys.argv[1] + '.txt'
if os.path.isfile(frame_info_file):
    print('{} already exists. Choose another file name.'.format(fullFilePath))
    sys.exit()
print('Video will be saved to: {}'.format(fullFilePath))
# get frame rate and query for video length based on this

# define storage variables
timestamps = []
frame_numbers = []

# SETUP FUNCTIONS #############################################################################################################
def initCam(cam): #function to initialize camera parameters for synchronized capture
    cam.Init()
    # load default configuration
    cam.UserSetSelector.SetValue(PySpin.UserSetSelector_Default)
    cam.UserSetLoad()
    # set acquisition. Continuous acquisition. Auto exposure off. Set frame rate using exposure time. 
    cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
    cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
    cam.ExposureMode.SetValue(PySpin.ExposureMode_Timed) #Timed or TriggerWidth (must comment out trigger parameters other that Line)
    cam.ExposureTime.SetValue(EXPOSURE_TIME)
    cam.AcquisitionFrameRateEnable.SetValue(False)
    #######cam.AcquisitionFrameRate.SetValue(FRAMES_PER_SECOND)
    # set analog. Set Gain + Gamma. 
    cam.GainAuto.SetValue(PySpin.GainAuto_Off)
    cam.Gain.SetValue(GAIN_VALUE)
    cam.GammaEnable.SetValue(True)
    cam.Gamma.SetValue(GAMMA_VALUE)
    # set ADC bit depth and image pixel depth, size
    cam.AdcBitDepth.SetValue(PySpin.AdcBitDepth_Bit12) #use higher bit depth for better color image
    cam.PixelFormat.SetValue(PySpin.PixelFormat_RGB8Packed) #24 bits total; 8x R then G then B
    cam.Width.SetValue(IMAGE_WIDTH)
    cam.Height.SetValue(IMAGE_HEIGHT)
    cam.OffsetX.SetValue(WIDTH_OFFSET)
    cam.OffsetY.SetValue(HEIGHT_OFFSET)
    # setup FIFO buffer
    camTransferLayerStream = cam.GetTLStreamNodeMap()
    handling_mode1 = PySpin.CEnumerationPtr(camTransferLayerStream.GetNode('StreamBufferHandlingMode'))
    handling_mode_entry = handling_mode1.GetEntryByName('OldestFirst')
    handling_mode1.SetIntValue(handling_mode_entry.GetValue())
    # optionally send exposure active signal on Line 2 (the white wire)
    cam.LineSelector.SetValue(PySpin.LineSelector_Line1)
    cam.LineMode.SetValue(PySpin.LineMode_Output) 
    cam.LineSource.SetValue(PySpin.LineSource_ExposureActive) #route desired output to Line 1 (try Counter0Active or ExposureActive)
    #cam.LineSelector.SetValue(PySpin.LineSelector_Line2)
    #cam.V3_3Enable.SetValue(True) #enable 3.3V rail on Line 2 (red wire) to act as a pull up for ExposureActive - this does not seem to be necessary as long as a pull up resistor is installed between the physical lines, and actually degrades signal quality 
    
def saveImage(imageWriteQueue, writer): #function to save video frames from the queue in a separate process
    while True:
        dequeuedImage = imageWriteQueue.get()
        if dequeuedImage is None:
            break
        else:
            writer.writeFrame(dequeuedImage) #call to ffmpeg
            imageWriteQueue.task_done()
                      
def camCapture(camQueue, cam, frame_numbers, timestamps, k): #function to capture images, convert to numpy, send to queue, and release from buffer in separate process
    while True:
        try:
            image = cam.GetNextImage() #get pointer to next image in camera buffer; blocks until image arrives via USB, within infinite timeout for first frame 
                        
            npImage = np.array(image.GetData(), dtype="uint8").reshape(image.GetHeight(), image.GetWidth(), 3); #convert PySpin ImagePtr into numpy array; use uint8 for color channels x3
            camQueue.put(npImage)  
            image.Release() #release from camera buffer
            k = k + 1
            frame_numbers.append(k)
            timestamps.append(time.time())
        # if camera has been de-initialized in the main script, end
        except:
            break
        
        

# INITIALIZE CAMERAS & COMPRESSION ###########################################################################################
system = PySpin.System.GetInstance() # Get camera system
cam_list = system.GetCameras() # Get camera list
cam1 = cam_list[0]
initCam(cam1)
 
# setup output video file parameters (first make sure latencies are OK with conservative parameters, then try to optimize):  
# for now just use default h264_nvenc options
writer = skvideo.io.FFmpegWriter(movieName, outputdict={'-vcodec': 'h264_nvenc'}) # encoder is h264_nvenc or libx264
#writer = skvideo.io.FFmpegWriter(movieName, inputdict={'-pixel_format': 'rgb24'}, outputdict={'-vcodec': 'h264_nvenc'}) #can explicitly set input format, although FFMPEG will infer

#setup tkinter GUI (non-blocking, i.e. without mainloop) to output images to screen quickly
window = tk.Tk()
window.title("camera acquisition")
geomStrWidth = str(int(IMAGE_WIDTH/2) + 25)
geomStrHeight = str(int(IMAGE_HEIGHT/2) + 35)
window.geometry(geomStrWidth + 'x' + geomStrHeight)
textlbl = tk.Label(window, text="elapsed time: ")
textlbl.grid(column=0, row=0)
imglabel = tk.Label(window) # make Label widget to hold image
imglabel.place(x=10, y=20) #pixels from top-left
window.update() #update TCL tasks to make window appear

#############################################################################
# start main program loop ###################################################
#############################################################################    

try:
    print('Press Ctrl-C to end recording and save video')
    i = 0
    imageWriteQueue = queue.Queue() #queue to pass images captures to separate compress and save thread
    cam1Queue = queue.Queue()  #queue to pass images from separate cam1 acquisition thread
    # setup separate threads to accelerate image acquisition and saving, and start immediately:
    saveThread = threading.Thread(target=saveImage, args=(imageWriteQueue, writer,))
    saveThread.daemon = True
    cam1Thread = threading.Thread(target=camCapture, args=(cam1Queue, cam1, frame_numbers, timestamps, i,))
    cam1Thread.daemon = True
    saveThread.start()  
    
    cam1.BeginAcquisition()
    cam1Thread.start() 
    tStart = time.time()

    while True: # main acquisition loop
        while cam1Queue.empty(): #wait until ready in a loop
            time.sleep(WAIT_TIME)
           
        dequeuedAcq1 = cam1Queue.get() # get images formated as numpy from separate process queues as soon as they are ready
        
        # send image to FFMPEG saving queue
        imageWriteQueue.put(dequeuedAcq1)
        
        if frame_numbers[-1]%5 == 0: #update screen every X frames 
            framesElapsedStr = "frame #: " + str(frame_numbers[-1])
            textlbl.configure(text=framesElapsedStr)
            I = ImageTk.PhotoImage(Image.fromarray(dequeuedAcq1))
            imglabel.configure(image=I)
            imglabel.image = I #keep reference to image
            window.update() #update on screen (this must be called from main thread)

# end aqcuisition loop #############################################################################################            
except KeyboardInterrupt: #if user hits Ctrl-C, everything should end gracefully
    tEndAcq = time.time()
    pass        
        
cam1.EndAcquisition() 
textlbl.configure(text='Capture complete, still writing to disk...') 
window.update()
print('Capture ends at: {:.2f}sec'.format(tEndAcq - tStart))
imageWriteQueue.join() #wait until compression and saving queue is done writing to disk
tEndWrite = time.time()
print('File written at: {:.2f}sec'.format(tEndWrite - tStart))
writer.close() #close to FFMPEG writer
window.destroy()

# save timestamps and frame numbers
timestamps = [x-timestamps[0] for x in timestamps]
frame_info_rows = zip(frame_numbers, timestamps)
with open(frame_info_file, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(("Frame", "Timestamp"))
    for row in frame_info_rows:  # frame_numbers
        writer.writerow(row)
    
# delete all pointers/variable/etc:
cam1.DeInit()
del cam1
cam_list.Clear()
del cam_list
system.ReleaseInstance()
del system
print('Done!')