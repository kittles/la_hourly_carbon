import math
from struct import pack
import datetime as dt
import numpy as np
import itertools as itr
import os
import sys
import netCDF4
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw, ImageFont
import os
import datetime as dt
import itertools as itr
import colorcet as cc
import itertools as itr
from vapory import *
import pprint
import random

def data_by_hour (hour):
    threshold = 5000 
    data = nc.variables['Carbon Emission'][hour].filled(fill_value=0)
    data[data > threshold] = threshold
    data += 1
    data = np.sqrt(data)
    data -= 1
    data /= data.max()
    # swap x and y to match how we think of maps
    data = np.swapaxes(data, 0, 1)
    return data

def zero_data ():
    data = nc.variables['Carbon Emission'][0].filled(fill_value=0)
    data = np.zeros(data.shape)
    # swap x and y to match how we think of maps
    data = np.swapaxes(data, 0, 1)
    return data
    

def interpolate_data (d1, d2, w1=1, w2=1):
    arrs1 = [d1[:] for _ in range(w1)]
    arrs2 = [d2[:] for _ in range(w2)]
    arrs = arrs1 + arrs2
    return np.mean(arrs, axis=0)

# colorscheme
colors = cc.fire[:]
colors = [np.array([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]) for h in colors]
colors[0] = np.array([0,0,0])

# all the rendering details
config = dict(
    colors = colors,
    nc_fp = '/home/patrick/projects/kevin_gurney/la_hourly/data/LAbasin.total.hourly.2011.v2.5.nc',
    basemap_fp = '/home/patrick/projects/kevin_gurney/la_hourly/basemaps/composite-crop.jpg',
    basemap_min_pixel = np.array([2833, 5904 - 3885]), # these are from top left hence the subtraction
    basemap_max_pixel = np.array([5616, 5904 - 2015]),
    basemap_scale = 0.2,
    bar_threshold = 1,
    render_resolution_x = 1920,
    render_resolution_y = 1080,
    resolution_multiple = 1,
    z_base = 500,
    ortho_angle = 60,
    step_counter = 0,         # everything about the frame should be determined by this
    nth_step = 1,             # for quick and dirty renders
    angle_start = 45,         # where the camera starts the animation
    angle_sweep = 90,         # total sweep during the entire animation
    empty_steps_before = 60,  # show empty map to get bearings
    empty_steps_after = 60,
    total_hours = 24,
    still_steps = 30,         # steps to wait between hours to show still bars
    interpolation_steps = 30, # steps to fade between two hours
    radiosity = False,
    antialiasing = 0.0001,
    output_dir = 'output/test/',
    fps = 60,                 # for ffmpeg movie rendering
)


# dataset dimension info
nc = netCDF4.Dataset(config['nc_fp'])
data = data_by_hour(0)
x_dim = data.shape[0]
y_dim = data.shape[1]
z_dim = 100

# some basics about the basemap image
basemap_img = Image.open(config['basemap_fp'])
basemap_width = basemap_img.width
basemap_height = basemap_img.height

# use the basemap info to generate the values for locating data
data_x_offset = config['basemap_scale'] * config['basemap_min_pixel'][0]
data_y_offset = config['basemap_scale'] * config['basemap_min_pixel'][1]
data_x_unit = config['basemap_scale'] * (config['basemap_max_pixel'][0] - config['basemap_min_pixel'][0]) / x_dim
data_y_unit = config['basemap_scale'] * (config['basemap_max_pixel'][1] - config['basemap_min_pixel'][1]) / y_dim

def to_basemap_coords (vec):
    return np.array([
        data_x_offset + (data_x_unit * vec[0]),
        data_y_offset + (data_y_unit * vec[1]),
        vec[2],
    ])

# compute some handy numbers for knowing where we are in the animation
total_anim_steps = config['empty_steps_before'] + config['empty_steps_after']
total_anim_steps += (1 + config['total_hours']) * (config['still_steps'] + config['interpolation_steps'])
single_hour_steps = config['still_steps'] + config['interpolation_steps']
total_hour_steps = single_hour_steps * (1 + config['total_hours'])

# camera placement info
data_center = to_basemap_coords([x_dim / 2, y_dim / 2, 0])
radius = (y_dim * 1.5) * data_y_unit # keep the camera a constant distance from the center as it rotates
angles = np.linspace(config['angle_start'], config['angle_start'] + config['angle_sweep'], total_anim_steps + 1) 

# for tracking progress and rendering speed
config['start_time'] = dt.datetime.now()
render_times = []

# prepare directory for renders
try:
    print('creating directory {}'.format(config['output_dir']))
    os.mkdir(config['output_dir'])
except:
    print('directory {} exists'.format(config['output_dir']))
    clear = input('clear? y/n: ')
    if clear.lower() == 'y':
        import shutil
        shutil.rmtree(config['output_dir'])
        os.mkdir(config['output_dir'])

def next_frame (config):
    # advance the step and counter and log some data about how things are going
    config['step_counter'] += config['nth_step']
    if config['step_counter'] > total_anim_steps:
        return False
    progress =  100 * config['step_counter'] / total_anim_steps 
    elapsed = dt.datetime.now() - config['start_time']
    estimate = 100 * (elapsed / progress)
    estimate -= elapsed
    sys.stdout.write('\r'+'step counter: {:06} of {:06} -- {:0.2f} % -- elapsed: {} -- estimated_left: {}'.format(
        config['step_counter'], 
        total_anim_steps,
        progress, 
        elapsed,
        estimate
    ))
    sys.stdout.flush()
    return True


def generate_camera (config):
    step = config['step_counter']
    angle = angles[step]
    angle_rad = math.radians(angle)
    x = data_center[0] + math.cos(angle_rad)*radius;
    y = data_center[1] + math.sin(angle_rad)*radius;
    # should rise until 90, then fall correspondingly
    y -= 200 * (1 - (abs(90 - angle)/ 90))
    camera = Camera(
        'orthographic', 'angle', config['ortho_angle'],
        'location',  [x, y, config['z_base']],
        'sky', [0,0,1],
        #'direction', [0, 0, 1],
        #'right', 
        'look_at', data_center, 
    )
    #config['angle'] += config['angle_step']
    return camera


def generate_scene_objects (config):
    objects = [
        Background('color', [1, 1, 1]),
        Plane(
            [0,0,1], 0,
            Texture(
                Pigment(
                    ImageMap(
                        'jpeg', '"{}"'.format(config['basemap_fp']), 'once',
                    ),
                    'scale', [basemap_width * config['basemap_scale'], basemap_height * config['basemap_scale'], 1],
                    'translate', [-basemap_width * config['basemap_scale'], -basemap_height * config['basemap_scale'], 0],
                    'rotate', [180,180,0],
                ),
                Finish('emission', 0.3),
            ),
            'no_shadow',
        ),
        LightSource(
            [x_dim / 2, y_dim / 2, 1000],
            'color',[1, 1, 1],
        ),
    ]
    return objects

def generate_axes (config):
    return [
        # x axis
        Box(
            data_center - 5,
            (data_center + 5) + [1000, 0, 0],
            Texture(
                Pigment('color', [0,1,0]),
                Finish('emission', 0.8),
            )
        ),
        # y axis
        Box(
            data_center - 5,
            (data_center + 5) + [0, 1000, 0],
            Texture(
                Pigment('color', [0,0,1]),
                Finish('emission', 0.8),
            )
        ),
        # z axis
        Box(
            data_center - 5,
            (data_center + 5) + [0, 0, 1000],
            Texture(
                Pigment('color', [1,0,0]),
                Finish('emission', 0.8),
            )
        ),
        Box(
            data_center - 5,
            data_center + 5,
            Texture(
                Pigment('color', [1,1,1]),
                Finish('emission', 0.8),
            )
        ),
    ]


def generate_bars (config):
    bars = []

    def transmition_value (z):
        val = 0.5
        #val -= 0.3 * (z / z_dim)
        return val

    def make_bar (x,y,z):
        color = colors[int(255 * z / z_dim)]
        return Box(
            to_basemap_coords([x, y, 0]),
            to_basemap_coords([x + 1, y + 1, z]),
            Texture( 
                Pigment('color', color / 255),
                #Pigment('color', color / 255, 'transmit', transmition_value(z)),
                Finish('emission', 0.8),
                #Finish('ambient', 0.7),
            ),
            'no_shadow',
        )

    # determine which phase of the animation we are in based on the step
    step = config['step_counter']
    if step < config['empty_steps_before']:
        # empty map
        pass
    elif step < (config['empty_steps_before'] + total_hour_steps):
        # during one of the hours
        total_hour_step = step - config['empty_steps_before']
        hour = total_hour_step // single_hour_steps
        hour_step = total_hour_step % (config['interpolation_steps'] + config['still_steps'])
        # first and last hour need zero data on either side
        if hour == 0:
            data_before = zero_data()
            data_after = data_by_hour(hour)
        elif hour == config['total_hours']:
            data_before = data_by_hour(hour - 1)
            data_after = zero_data()
        else:
            data_before = data_by_hour(hour - 1)
            data_after = data_by_hour(hour)

        # is it an interpolated step or a still step
        if hour_step < config['interpolation_steps']:
            data = interpolate_data(data_before, data_after, config['interpolation_steps'] - hour_step, hour_step)
        else:
            data = data_after

        # create the rectangular bars for each data point
        for x,y in itr.product(range(x_dim), range(y_dim)):
            z = data[x,y] * z_dim
            # omit small bars so the map is more visible
            if z < config['bar_threshold']:
                continue
            bars.append(make_bar(x,y,z))
    else:
        # empty map
        pass
    return bars


def render_time_average (config):
    return sum(render_times, dt.timedelta(0)) / len(render_times)


def render_scene (config, verbose=False):
    start = dt.datetime.now()

    scene_objects = generate_scene_objects(config)
    camera = generate_camera(config)
    bars = generate_bars(config)
    axes = generate_axes(config)

    scene = Scene(camera, objects=scene_objects + bars + axes)
    scene.render(
        config['output_dir']+'{:06}.png'.format(config['step_counter']),
        width=config['render_resolution_x'] * config['resolution_multiple'],
        height=config['render_resolution_y'] * config['resolution_multiple'],
        antialiasing=config['antialiasing'],
    )
    render_times.append(dt.datetime.now() - start)
    if verbose:
        print('render took {} seconds. average render time: {}'.format(
            dt.datetime.now() - start, 
            render_time_average(config)
        ))


print('\n --- RENDER CONFIG --- \n')
pprint.PrettyPrinter(indent=4).pprint(config)
print('\n --- STARTING RENDER --- \n')
while next_frame(config):
    render_scene(config)
