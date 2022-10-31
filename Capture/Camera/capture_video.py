# -*- coding: utf-8 -*-
"""
Camera must not be streaming in Vimba for this script to run!
"""

from vimba import *
import os
import sys
import numpy as np
from datetime import datetime
#import tables
import threading
import csv
import cv2
from tkinter import Tk, filedialog
# must be run in every script because somehow this didn't set on install
os.environ['VIMBA_HOME'] = "C:/Program Files/Allied Vision/Vimba_5.0"

# tkinter: close annoying root window, make stuff appear on top
root = Tk()
root.withdraw()
root.wm_attributes('-topmost', 1)

# create file names
base_dir = 'C:/Users/Muspulheim/Desktop/Videos/'
#date = datetime.today().strftime('%Y%m%d')
#animal = input('Animal (e.g. TopHat): ')
#session = input('Session (e.g. LT01): ')
#base_file = base_dir + animal + '/' + date + '_' + animal + '_' + session
base_file = filedialog.asksaveasfilename()
frame_info_file = base_file + '.txt'
video_file = base_file + '.mp4'
#video_h5_file = base_file + '.h5'

# define camera settings
width = 1456
height = 1088
im_height = 600  # rescale for screen
im_width = int(width/(height/im_height))  # rescale for screen
fps = 60.0024  # 30.0003 #
settings_file = "C:/Users/Muspulheim/Desktop/ttl_exposure_60Hz.xml"
#settings_file = "C:/Users/Muspulheim/Desktop/default_60Hz_TTL_gain_exposure.xml"

# define storage variables
timestamps = []
frame_numbers = []
# frames_buffer = np.empty((width, height, int(fps*60*30)), dtype=np.int8) #159 GB

#video_h5_file_handle = tables.open_file(video_h5_file, mode='w')
#atom = tables.UInt8Atom()
# video_out_h5 = video_h5_file_handle.create_earray(video_h5_file_handle.root, \
#                                     'video_out_h5', atom, shape=(0, width, 3),
#                                     chunkshape=(1, width, height),
#                                     expectedrows=int(fps*60*30))

# create openCV video writer object
cv2.destroyAllWindows()  # close previous session, must be at start of sript
# only this codec works for CV2 in Windows
fourcc = cv2.VideoWriter_fourcc(*'DIVX')
video_out = cv2.VideoWriter(video_file, fourcc, fps, (width, height))


def get_camera() -> Camera:
    with Vimba.get_instance() as vimba:
        cams = vimba.get_all_cameras()
        if not cams:
            print('No Cameras accessible. Abort.\n')
            sys.exit(1)
        return cams[0]


class Handler:
    def __init__(self):
        self.shutdown_event = threading.Event()

    def __call__(self, cam: Camera, frame: Frame):
        ENTER_KEY_CODE = 13
        key = cv2.waitKey(1)

        if key == ENTER_KEY_CODE:
            self.shutdown_event.set()
            return

        elif frame.get_status() == FrameStatus.Complete:
            # convert to a color pixel format openCV recognizes
            # openCV does not have BayerRG8, so this is the workaround
            frame_np = frame.as_numpy_ndarray()
            frame_np = cv2.cvtColor(frame_np, cv2.COLOR_BAYER_RG2RGB)

            # resize the frame so it fits the display
            frame_resize = cv2.resize(frame_np, (im_width, im_height))

            # display the frame
            msg = 'Stream from \'{}\'. Press <Enter> to stop stream.'
            # if haven't converted to nparray above, must
            # display frame.as_opencv_image() instead
            cv2.imshow(msg.format(cam.get_name()), frame_resize)

            # save the frame, not resized
            # this line causes frames to drop
            video_out.write(frame_np)
            # frames_buffer[][][frame.get_id()] = frame_np
            # video_out_h5.append(frame_np)

            # read the timestamp & frame number
            frame_numbers.append(frame.get_id())
            timestamps.append(frame.get_timestamp())

        cam.queue_frame(frame)


"""

def main():


if __name__ == '__main__':
    main()
"""

# EVERYTHING has to be within a 'with' statement or else VimbaPython gets mad
with Vimba.get_instance():
    #cam_id = "DEV_000F315D528D"
    with get_camera() as cam:
        # Load camera settings from file

        cam.load_settings(settings_file, PersistType.All)

        # handler is executed on each acquired frame
        handler = Handler()

        print('Acquiring video, streaming & storing to '+video_file, flush=True)

        try:
            # Enter streaming mode is also known as asynchronous frame acquisition.
            # While active, the camera acquires and buffers frames continuously.
            cam.start_streaming(handler=handler, buffer_count=10)
            handler.shutdown_event.wait()

        finally:
            cam.stop_streaming()

            # close the file
            video_out.release()
            #np.savetxt(video_bin_file, frames_buffer)
            # video_h5_file_handle.close()

            # save timestamps and frame numbers
            frame_info_rows = zip(frame_numbers, timestamps)
            with open(frame_info_file, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(("Frame", "Timestamp"))
                for row in frame_info_rows:  # frame_numbers
                    writer.writerow(row)

            print('Acquisition complete, '+str(max(frame_numbers)) +
                  ' frames stored', flush=True)
