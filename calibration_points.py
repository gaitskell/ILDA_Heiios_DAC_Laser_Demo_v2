# -*- coding: utf-8 -*-
"""

DO NOT LOOK AT THIS FILE - IT IS PROBABLY NOT USEFUL

Random example that I am trying to look at

250423 Doesn't run yet
NameError: name 'LaserPath' is not defined
Think I need to import the ensire code
https://git.rubenvandeven.com/security_vision/trap/src/commit/5728213e2c43d33687fbd18c261ad2684adddc7d/trap

Source for this file:
https://git.rubenvandeven.com/security_vision/trap/src/commit/5728213e2c43d33687fbd18c261ad2684adddc7d/trap/helios_dac/calibration_points.py


Example for using Helios DAC libraries in python (using C library with ctypes)

NB: If you haven't set up udev rules you need to use sudo to run the program for it to detect the DAC.
"""
# from __future__ import annotations
# import annotations

import ctypes
import json
import math
from typing import Optional

import cv2  # Requires opencv-python
import numpy as np


def lerp(a: float, b: float, t: float) -> float:
    """Linear interpolate on the scale given by a to b, using t as the point on that scale.
    Examples
    --------
        50 == lerp(0, 100, 0.5)
        4.2 == lerp(1, 5, 0.8)
    """
    return (1 - t) * a + t * b


class LaserFrame():
    def __init__(self, paths: list[LaserPath]):
        self.paths = paths

    # def closest_path(cls, point, paths):
    #     distances = [min(p.last()-)]

    # def optimise_paths_lazy(self, last_point = None):
    #     """Quick way to optimise order of paths
    #     last_point can be the ending point of previous frame.
    #     """
    #     ordered_paths = []
    #     if not last_point:
    #         ordered_paths.append(self.paths.pop(0))

    #     last_point = endpoint
    #     pass

    def get_points_interpolated_by_distance(self, point_interval, last_point: Optional[LaserPoint] = None) -> list[
        LaserPoint]:
        """
        Interpolate the gaps between paths (NOT THE PATHS THEMSELVES)
        point_interval is the maximum interval at which a new point should be added
        """
        points: list[LaserPoint] = []
        for path in self.paths:
            if last_point:
                a = last_point
                b = path.first()
                dx = b.x - a.x
                dy = b.y - a.y
                distance = np.linalg.norm([dx, dy])
                steps = int(distance // point_interval)
                for step in range(steps + 1):  # have both 0 and 1 in the lerp for empty points
                    t = step / (steps + 1)
                    x = int(lerp(a.x, b.x, t))
                    y = int(lerp(a.y, b.y, t))
                    points.append(LaserPoint(x, y, (0, 0, 0), 0, True))
                # print('append', steps)

            points.extend(path.points)

            last_point = path.last()

        return points


class LaserPath():
    def __init__(self, points: list[LaserPoint] = []):
        # if len(points) < 1:
        #     raise RuntimeError("LaserPath should have some points")

        self.points = points

    def last(self):
        return self.points[-1]

    def first(self):
        return self.points[0]


class LaserPoint():
    def __init__(self, x, y, c: Color = (255, 0, 0), i=255, blank=False):
        self.x = x
        self.y = y
        self.c = c
        self._i = i
        self.blank = blank

    @property
    def color(self):
        if self.blank: return (0, 0, 0)
        return self.c

    @property
    def i(self):
        return 0 if self.blank else self._i


def circle_points(cx, cy, r, c: Color):
    # r = 100
    steps = r
    pointlist: list[LaserPoint] = []
    for i in range(steps):
        x = int(cx + math.cos(i * (2 * math.pi) / steps) * r)
        y = int(cy + math.sin(i * (2 * math.pi) / steps) * r)
        pointlist.append(LaserPoint(x, y, c, blank=(i == (steps - 1) or i == 0)))

    return pointlist


def cross_points(cx, cy, r, c: Color):
    # r = 100
    steps = r
    pointlist: list[LaserPoint] = []
    for i in range(steps):
        x = int(cx)
        y = int(cy + r - i * 2 * r / steps)
        pointlist.append(LaserPoint(x, y, c, blank=(i == (steps - 1) or i == 0)))
    path = LaserPath(pointlist)
    pointlist: list[LaserPoint] = []
    for i in range(steps):
        y = int(cy)
        x = int(cx + r - i * 2 * r / steps)
        pointlist.append(LaserPoint(x, y, c, blank=(i == (steps - 1) or i == 0)))
    path2 = LaserPath(pointlist)

    return [path, path2]


Color = tuple[int, int, int]


# Define point structure
class HeliosPoint(ctypes.Structure):
    # _pack_=1
    _fields_ = [('x', ctypes.c_uint16),
                ('y', ctypes.c_uint16),
                ('r', ctypes.c_uint8),
                ('g', ctypes.c_uint8),
                ('b', ctypes.c_uint8),
                ('i', ctypes.c_uint8)]


# Load and initialize library
HeliosLib = ctypes.cdll.LoadLibrary("./libHeliosDacAPI.so")
numDevices = HeliosLib.OpenDevices()
print("Found ", numDevices, "Helios DACs")

# #Create sample frames
# frames = [0 for x in range(100)]
# frameType = HeliosPoint * 1000
# x = 0
# y = 0
# for i in range(100):
#     y = round(i * 0xFFF / 100)
#     # y = round(50*0xFFF/100)
#     frames[i] = frameType()
#     for j in range(1000):
#         if (j < 500):
#             x = round(j * 0xFFF / 500)
#             offset = 0
#         else:
#             offset = 0
#             x = round(0xFFF - ((j - 500) * 0xFFF / 500))

#         # frames[i][j] = HeliosPoint(int(x),int(y+offset),0,(x%155),0,255)
#         frames[i][j] = HeliosPoint(int(x),int(y+offset),0,100,0,255)

pct = 0xfff / 100
r = 50

# TODO)) scriptje met sliders

paths = [
    # LaserPath(circle_points(10*pct, 45*pct, r, (100,0,100))),
    # *cross_points(10*pct, 45*pct, r, (100,0,100)), # magenta
    *cross_points(13.7 * pct, 38.9 * pct, r, (100, 0, 100)),  # magenta # punt 10
    *cross_points(44.3 * pct, 47.0 * pct, r, (0, 100, 0)),  # groen # punt 0
    *cross_points(82.5 * pct, 12.7 * pct, r, (100, 100, 100)),  # wit # punt 4
    *cross_points(89 * pct, 49 * pct, r, (0, 100, 100)),  # cyan # punt 2
    *cross_points(36 * pct, 81.7 * pct, r, (100, 100, 0)),  # geel # punt 7
]

calibration_points = [
    (13.7 * pct, 38.9 * pct, 10,),
    (44.3 * pct, 47.0 * pct, 0),
    (82.5 * pct, 12.7 * pct, 4),
    (89 * pct, 49 * pct, 2),
    (36 * pct, 81.7 * pct, 7),
]

with open('/home/ruben/suspicion/DATASETS/hof3/irl_points.json') as fp:
    irl_points = json.load(fp)

src_points = []
dst_points = []
for x, y, index in calibration_points:
    src_points.append(irl_points[index])
    dst_points.append([x, y])

print(src_points)
H, status = cv2.findHomography(np.array(src_points), np.array(dst_points))
print("LASER HOMOGRAPHY MATRIX")
print(H)
dst_img_points = cv2.perspectiveTransform(np.array([[irl_points[1]]]), H)
print(dst_img_points)

paths.extend([
    *cross_points(dst_img_points[0][0][0], dst_img_points[0][0][1], r, (100, 100, 0)),  # geel # punt 7
])

frame = LaserFrame(paths)

pointlist = frame.get_points_interpolated_by_distance(3)

print(len(pointlist))
# Play frames on DAC
i = 0
while True:

    frameType = HeliosPoint * len(pointlist)
    frame = frameType()

    # print(len(pointlist), last_laser_point.x, last_laser_point.y)

    for j, point in enumerate(pointlist):
        frame[j] = HeliosPoint(point.x, point.y, point.color[0], point.color[1], point.color[2], point.i)

        # Make 512 attempts for DAC status to be ready. After that, just give up and try to write the frame anyway
    statusAttempts = 0

    while (statusAttempts < 512 and HeliosLib.GetStatus(0) != 1):
        statusAttempts += 1

    HeliosLib.WriteFrame(0, 50000, 0, ctypes.pointer(frame), len(pointlist))

# for i in range(250):
# i+=1
# for j in range(numDevices):
#     statusAttempts = 0
#     # Make 512 attempts for DAC status to be ready. After that, just give up and try to write the frame anyway
#     while (statusAttempts < 512 and HeliosLib.GetStatus(j) != 1):
#         statusAttempts += 1
#     HeliosLib.WriteFrame(j, 50000, 0, ctypes.pointer(frames[i % 100]), 1000) #Send the frame


HeliosLib.CloseDevices()

