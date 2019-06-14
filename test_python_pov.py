import itertools as itr
from vapory import *
import random

camera = Camera(
    #'orthographic',
    'location',  [-25, -25, -100],
    'direction', [0, 0, 1],
    'look_at',  [25, 25, 5]
)
objects = [
    Background('color', [0.85, 0.75, 0.75]),
    LightSource([0, 0, 0],
                'color',[1, 1, 1],
                'translate', [-5, 5, -5]),
    LightSource ([0, 0, 0],
                 'color', [0.25, 0.25, 0.25],
                 'translate', [6, -6, -6]),
]

for x,y,z in itr.product(range(50), range(50), range(10)):
    box = Box(
        [x, y, z],
        [x + random.random(), y + random.random(), z + 0.8],
        Texture( 
            Pigment('color', [1,0.5,0]),
            #Finish('emission', random.random()),
        )
    )
    objects.append(box)

scene = Scene(camera, objects=objects)

# We use antialiasing. Remove this option for faster rendering.
scene.render("cube.png", width=1920, height=1080, antialiasing=0.00001)
