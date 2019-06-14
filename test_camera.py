from struct import pack
import numpy as np
import itertools as itr
import os
import netCDF4
from PIL import Image, ImageDraw, ImageFont
import os
import datetime as dt
import itertools as itr
import colorcet as cc
import itertools as itr
from vapory import *
import random

# prepare scene
objects = [
    Background('color', [0.85, 0.75, 0.75]),
    LightSource([0, 0, 200],
                'color',[1, 1, 1],
                'translate', [-5, 5, -5]),
    LightSource ([500, 300, 200],
                 'color', [0.25, 0.25, 0.25],
                 'translate', [6, -6, -6]),
]

front_left = np.array([0,0,0])
back_right = np.array([1,1,1])

def make_cube (loc, color):
    return Box(
        np.array(loc),
        np.array(loc) + 1,
        Texture(
            Pigment('color', color),
            Finish('emission', 0.5),
        )
    )

#objects.append(make_cube([0,0,0], [1,0,0]))
#objects.append(make_cube([2,0,0], [0,1,0]))
#objects.append(make_cube([0,2,0], [0,0,1]))
#objects.append(make_cube([0,0,2], [1,0,1]))

# x axis
objects.append(Box(
    [-100,-0.1,-0.1],
    [100,0.1,0.1],
    Texture(
        Pigment('color', [0,1,0]),
        Finish('emission', 0.8),
    )
))

# y axis
objects.append(Box(
    [-0.1,-100,-0.1],
    [0.1,100,0.1],
    Texture(
        Pigment('color', [0,0,1]),
        Finish('emission', 0.8),
    )
))

# z axis
objects.append(Box(
    [-0.1,-0.1,-100],
    [0.1,0.1,100],
    Texture(
        Pigment('color', [1,0,0]),
        Finish('emission', 0.8),
    )
))

# origin
objects.append(Box(
    [-1,-1,-1],
    [1,1,1],
    Texture(
        Pigment('color', [1,1,1]),
        Finish('emission', 0.8),
    )
))

ratio = 800 / 600

camera = Camera(
    'orthographic', 'angle', 90,
    'location',  np.array([1, 1, -1]) * 10,
    'sky', [0,0,1],
    #'direction', [-10, 10, -10],
    'right', 40 * ratio,
    'look_at',  [0, 0, 0]
)
scene = Scene(camera, objects=objects)
scene.render('camera_test.png', width=800, height=600)
