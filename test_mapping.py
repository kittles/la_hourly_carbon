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

# 1st quadrant
objects.append(Box(
    [3,3,0],
    [4,4,1],
    Texture(
        Pigment('color', [1,0,1]),
        Finish('emission', 0.8),
    )
))
#objects.append(Box(
#    [3,-3,0],
#    [4,-4,1],
#    Texture(
#        Pigment('color', [1,1,0]),
#        Finish('emission', 0.8),
#    )
#))

# markers
#objects.append(Box(
#    [10,-10,-10],
#    [10,10,10],
#    Texture(
#        Pigment('color', [1,0,0]),
#        Finish('emission', 1),
#    )
#))
#objects.append(Box(
#    [990,990,-1],
#    [1010,1010,1],
#    Texture(
#        Pigment('color', [0,0,1]),
#        Finish('emission', 0.8),
#    )
#))

image_plane = Plane(
    [0,0,1], 0,
    Texture(
        Pigment(
            ImageMap(
                'png', '"/home/patrick/projects/kevin_gurney/la_hourly/la-dark.png"', 'once',
            ),
            'scale', [1000,1000,1],
        ),
        #Pigment('color', [1,0,0]),
        Finish('emission', 0.5),
    ),
)

objects.append(image_plane)

ratio = 800 / 600

for i in range(20):
    camera = Camera(
        #'orthographic', 'angle', 90,
        'location', [i, 5, 15],
        'sky', [0,0,1],
        #'direction', [-10, 10, -10],
        #'right', 40 * ratio,
        'look_at',  [3.5, 3.5, 0.5]
    )
    scene = Scene(camera, objects=objects)
    scene.render('test/mapping_test_{:04}.png'.format(i), width=800, height=600)
