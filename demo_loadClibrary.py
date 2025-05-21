"""
250416
Had to make a new library for Apple Silicon using XCode
libHeliosDACAPI.dylib

# https://github.com/Grix/helios_dac/blob/master/sdk/examples/python/linux_example.py

Example for using Helios DAC libraries in python (using C library with ctypes)
NB: If you haven't set up udev rules you need to use sudo to run the program for it to detect the DAC.
"""

import ctypes

#Define point structure
class HeliosPoint(ctypes.Structure):
    #_pack_=1
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]

#Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary("./libHeliosDacAPI.dylib")
numDevices = HeliosLib.OpenDevices()
print("\nFound ", numDevices, "Helios DACs")


# ----------- Code Above Works -------------
nn = 1000 # max 1000, number of points in lines painted in 1 frame

#Create sample frames
frames = [0 for x in range(30)]
frameType = HeliosPoint * nn  # Array of points
x = 0
y = 0


for i in range(30):
    y = round(i * 0xFFF / 30)
    frames[i] = frameType()
    for j in range(nn):
        if (j < nn//2 ):
            x = round(j * 0xFFF / (nn//2)) # Full width
        else:
            x = round(0xFFF - ((j - (nn//2)) * 0xFFF / (nn//2))) # Full width


        # [i] 30 frames
        # [j] nn points within the frames
        frames[i][j] = HeliosPoint(int(x),int(y)
                                #   ,255,255,255 # RGB, White
                                   ,255,0,128 # RGB, Purple
                                   ,255) # Intensity



#Play frames on DAC
print("Write 150 Frames to Helios DACs")

for i in range(150):
# Use i % 30 when selecting from Frame

    for j in range(numDevices):
    # Looping over devices

        statusAttempts = 0

        # Make 512 attempts for DAC status to be ready. After that, just give up and try to write the frame anyway
        while (statusAttempts < 512 and HeliosLib.GetStatus(j) != 1):
            statusAttempts += 1

        HeliosLib.WriteFrame(
            j
            , 30 * nn   # Why is this 30 frames * number of points in a frame, i.e. all frames
            , 0
            , ctypes.pointer( frames[i % 30] )  # We are passing array of points
            , nn  # This is number of points
        ) #Send the frame

        if statusAttempts>=512:
            print("Warning: Could not write frame to DAC")

print("\n------------------------------- Finished Writing Frames")


HeliosLib.CloseDevices()


