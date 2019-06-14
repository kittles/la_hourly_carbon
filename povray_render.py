import math
from struct import pack
import datetime as dt
import numpy as np
import itertools as itr
import os
import sys
import netCDF4
from PIL import Image, ImageDraw, ImageFont
import os
import datetime as dt
import itertools as itr
import colorcet as cc
import itertools as itr
from vapory import *
import random

# load all data
nc_fp = '/home/patrick/projects/kevin_gurney/la_hourly/data/LAbasin.total.hourly.2011.v2.5.nc'
nc = netCDF4.Dataset(nc_fp)

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


# get some basic dimensions
data = data_by_hour(0)
x_dim = data.shape[0]
y_dim = data.shape[1]
z_dim = 100

# for aligning map with data
scale_x = x_dim
scale_y = y_dim
trans_x = 0
trans_y = y_dim

# prepare scene
colors = cc.rainbow[:]
colors = [np.array([int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)]) for h in colors]
colors[0] = np.array([0,0,0])


# for rendering and camera placement
radiosity = Radiosity(
    'brightness', 1.5,
    'count', 100,
    'error_bound', 0.15,
    'gray_threshold', 0.0,
    'low_error_factor', 0.2,
    'minimum_reuse', 0.015,
    'nearest_count', 5,
    'recursion_limit', 2,
    'adc_bailout', 0.01,
    'max_sample', 0.5,
    'media off',
    'normal off',
    'always_sample', 1,
    'pretrace_start', 0.08,
    'pretrace_end', 0.01
)

config = dict(
    bar_threshold = 1,
    base_resolution_x = 1920,
    base_resolution_y = 1080,
    resolution_multiple = 1,
    radius = y_dim + (y_dim / 2),
    origin = [x_dim / 2, y_dim / 2],
    z_base = 500,
    ortho_angle = 70,
    step_counter = 0,         # everything about the frame should be determined by this
    nth_step = 1,            # for quick and dirty renders
    #angle = 50,
    #angle_step = 0.06,
    angle_start = 45,         # where the camera starts the animation
    angle_sweep = 90,         # total sweep during the entire animation
    render_times = [],
    empty_steps_before = 60,  # show empty map to get bearings
    empty_steps_after = 60,
    total_hours = 24,
    still_steps = 30,         # steps to wait between hours to show still bars
    interpolation_steps = 30, # steps to fade between two hours
    radiosity = False,        # render with radiosity
    antialiasing = 0.0001,
    output_dir = 'output/test/',
    fps = 60,                 # for ffmpeg movie rendering
)

# compute some handy numbers
config['ratio'] = config['base_resolution_x'] / config['base_resolution_y']
config['total_steps'] = config['empty_steps_before'] + config['empty_steps_after']
config['total_steps'] += (1 + config['total_hours']) * (config['still_steps'] + config['interpolation_steps'])
config['single_hour_steps'] = config['still_steps'] + config['interpolation_steps']
config['total_hour_steps'] = config['single_hour_steps'] * (1 + config['total_hours'])
config['angles'] = np.linspace(config['angle_start'], config['angle_start'] + config['angle_sweep'], config['total_steps'] + 1) 
config['start_time'] = dt.datetime.now()

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
    if config['step_counter'] > config['total_steps']:
        return False
    progress =  100 * config['step_counter'] / config['total_steps']
    elapsed = dt.datetime.now() - config['start_time']
    estimate = 100 * (elapsed / progress)
    estimate -= elapsed
    sys.stdout.write('\r'+'step counter: {:06} of {:06} -- {:0.2f} % -- elapsed: {} -- estimated_left: {}'.format(
        config['step_counter'], 
        config['total_steps'], 
        progress, 
        elapsed,
        estimate
    ))
    sys.stdout.flush()
    return True


def generate_camera (config):
    step = config['step_counter']
    angle = config['angles'][step]
    angle_rad = math.radians(angle)
    x = config['origin'][0] + math.cos(angle_rad)*config['radius'];
    y = config['origin'][1] + math.sin(angle_rad)*config['radius'];
    # should rise until 90, then fall correspondingly
    y -= 200 * (1 - (abs(90 - angle)/ 90))
    camera = Camera(
        'orthographic', 'angle', config['ortho_angle'],
        'location',  [x, y, config['z_base']],
        'sky', [0,0,1],
        #'direction', [0, 0, 1],
        #'right', 
        'look_at',  [x_dim/2, y_dim/2, 20]
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
                        'png', '"/home/patrick/projects/kevin_gurney/la_hourly/basemaps/la-streets-sized.png"', 'once',
                    ),
                    'scale', [scale_x, scale_y, 1],
                    'translate', [-trans_x, -trans_y, 0],
                    #'rotate', [0,180,0],
                    'rotate', [180,0,0],
                    #'rotate', [0,0,180],
                ),
                #Pigment('color', [1,0,0]),
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


def generate_bars (config):
    bars = []

    def make_bar (x,y,z):
        color = colors[int(255 * z / z_dim)]
        return Box(
            [x, y, 0],
            [x + 1, y + 1, z],
            Texture( 
                Pigment('color', color / 255),
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
    elif step < (config['empty_steps_before'] + config['total_hour_steps']):
        # during one of the hours
        total_hour_step = step - config['empty_steps_before']
        hour = total_hour_step // config['single_hour_steps']
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
    return sum(config['render_times'], dt.timedelta(0)) / len(config['render_times'])


def render_scene (config, verbose=False):
    start = dt.datetime.now()

    scene_objects = generate_scene_objects(config)
    camera = generate_camera(config)
    bars = generate_bars(config)

    scene = Scene(camera, objects=scene_objects + bars)
    scene.render(
        config['output_dir']+'{:06}.png'.format(config['step_counter']),
        width=config['base_resolution_x'] * config['resolution_multiple'],
        height=config['base_resolution_y'] * config['resolution_multiple'],
        antialiasing=config['antialiasing'],
    )
    config['render_times'].append(dt.datetime.now() - start)
    if verbose:
        print('render took {} seconds. average render time: {}'.format(
            dt.datetime.now() - start, 
            render_time_average(config)
        ))


import pprint
print('\n --- RENDER CONFIG --- \n')
pprint.PrettyPrinter(indent=4).pprint(config)
print('\n --- STARTING RENDER --- \n')
while next_frame(config):
    render_scene(config)

## show blank map for a bit to get bearings
#for step in range(60):
#    objects = prepare_scene()
#    render_scene(objects, config)
#
## fade in bars from nothing
#hour_data = zero_data()
#next_data = data_by_hour(0)
#for step in range(config['interpolation_steps']):
#    data = interpolate_data(hour_data, next_data, config['interpolation_steps'] - step, step)
#    objects = prepare_scene()
#    place_data(data, objects)
#    render_scene(objects, config)
#
## step through hours
#for hour in range(24):
#    hour_data = data_by_hour(hour)
#    next_data = data_by_hour(hour + 1)
#    print('starting hour {}'.format(hour))
#    start_time = dt.datetime.now()
#    # add a bit of time where the bars are still, to indicate each hour
#    for step in range(config['still_steps']):
#        data = hour_data
#        objects = prepare_scene()
#        place_data(data, objects)
#        render_scene(objects, config)
#
#    for step in range(config['interpolation_steps']):
#        data = interpolate_data(hour_data, next_data, config['interpolation_steps'] - step, step)
#        objects = prepare_scene()
#        place_data(data, objects)
#        render_scene(objects, config)
#    print('finished hour {}, took {} seconds'.format(hour, dt.datetime.now() - start_time))
#    print('average frame render time', render_time_average(config))
