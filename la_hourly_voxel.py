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

# prepare data
nc_fp = '/home/patrick/projects/kevin_gurney/la_hourly/data/LAbasin.total.hourly.2011.v2.5.nc'
nc = netCDF4.Dataset(nc_fp)


def interpolate_data (d1, d2, w1=1, w2=1):
    arrs1 = [d1[:] for _ in range(w1)]
    arrs2 = [d2[:] for _ in range(w2)]
    arrs = arrs1 + arrs2
    return np.mean(arrs, axis=0)


counter = 1
for hour in range(48):
    threshold = 5000 

    data_before = nc.variables['Carbon Emission'][hour].filled(fill_value=0)
    data_before[data_before > threshold] = threshold
    data_before += 1
    data_before = np.sqrt(data_before)
    data_before -= 1
    data_before /= data_before.max()

    data_after = nc.variables['Carbon Emission'][hour + 1].filled(fill_value=0)
    data_after[data_after > threshold] = threshold
    data_after += 1
    data_after = np.sqrt(data_after)
    data_after -= 1
    data_after /= data_after.max()

    x_dim = data_before.shape[0]
    y_dim = data_before.shape[1]
    z_dim = 100

    colors = cc.bmy[:]
    colors = [[int(h.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)] for h in colors]

    for split in range(10):
        matrix = np.zeros((x_dim, y_dim, z_dim, 4), dtype='uint32')
        data = interpolate_data(data_before, data_after, 10 - split, split)

        # colors
        for x, y in itr.product(range(x_dim), range(y_dim)):
            val = int(z_dim * data[x, y])
            for z in range(val):
                color = colors[int((z/z_dim) * len(colors))] + [255]
                matrix[x, y, z] = color

        # prepare file
        output_file = open('output/voxel_hours/aaa-test-{:05}.qb'.format(counter), 'wb')

        def to_file (fmt, *args):
            output_file.write(pack(fmt, *args))

        version = 0
        color_format = 0
        z_axis_orientation = 1
        compression = 0
        visibility_mask_encoded = 0
        matrix_count = 1

        to_file('i', version)
        to_file('i', color_format)
        to_file('i', z_axis_orientation)
        to_file('i', compression)
        to_file('i', visibility_mask_encoded)
        to_file('i', matrix_count)

        matrix_name = ('hour-{}'.format(hour)).encode('ascii')
        to_file('B', len(matrix_name))
        to_file(str(len(matrix_name))+'s', matrix_name)

        # size
        to_file('III', x_dim, z_dim, y_dim)

        # origin
        to_file('iii', -1 * int(x_dim / 2), 0, -1 * int(y_dim / 2))

        # why the fuck is it this order, i have no idea
        for y, z, x in itr.product(range(y_dim), range(z_dim), range(x_dim)):
            #if z == 0:
            #    pass
            #    #to_file('BBBB', *[0,0,0,255])
            #else:
            to_file('BBBB', *matrix[x,y,z])

        print(counter)
        counter += 1
        break
    break
