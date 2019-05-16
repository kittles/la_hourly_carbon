from __future__ import division
import matplotlib.pyplot as plt
import netCDF4
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import progressbar
import matplotlib.colors as colors
import matplotlib.cm as cm
import os
import json
import datetime as dt



data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
output_dir = os.path.join(os.path.dirname(__file__), '..', 'output')
cm_viridis = cm.get_cmap('nipy_spectral')

c = 1
pctils = [] # 4.1 is a good max 99.5 pctile
scalar = 255 / 4.1
hourly_totals = [np.zeros(24) for _ in range(365)]
total_max = 300000

days = []
hours = []
make_images = False
start_datetime = dt.datetime(2015,1,1,0)

nc_fp = '/home/patrick/projects/kevin_gurney/la_hourly/data/LAbasin.total.hourly.2011.v2.5.nc'
nc = netCDF4.Dataset(nc_fp)
#data = nc.variables['Carbon Emission'][:,:,:].filled(fill_value=0).flatten()
#print('{} points - min {} max {}'.format(len(data), data.min(), data.max()))
#for pct in np.arange(10, 100, 10):
#    print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
#for pct in np.arange(90, 100, 1):
#    print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
'''
1524923280 points - min 0.0 max 241833.5573604525
10 percentile: 0.0
20 percentile: 0.0
30 percentile: 0.0
40 percentile: 0.0
50 percentile: 0.011374599506960358
60 percentile: 0.030739440350251935
70 percentile: 0.05891310046409039
80 percentile: 0.17275713875497745
90 percentile: 5.999502366748242
90 percentile: 5.999502366748242
91 percentile: 9.164872458847649
92 percentile: 14.319408123946864
93 percentile: 22.21650763535503
94 percentile: 36.543416268195955
95 percentile: 57.82064340128875
96 percentile: 95.65442003146073
97 percentile: 167.04137434824918
98 percentile: 303.9129910144013
99 percentile: 573.3088139403442
'''
threshold = 2000
for hour in range(0, len(nc.variables['Carbon Emission'])):
    data = nc.variables['Carbon Emission'][hour].filled(fill_value=0)
    data[data > threshold] = threshold
    #print(data.max())
    data += 1
    data = np.log(data)
    print('max', data.max())
    data /= data.max()
    #print(data.min(), data.max())
    #plt.hist(data.flatten())
    #plt.show()
    data = cm_viridis(data)
    data *= 255
    #data[:,:,3] = 1
    data = data.astype('uint8')
    Image.fromarray(data).convert('RGB').save('output/all_hours/{:04}.png'.format(hour))
    print(hour)
    if hour > 168:
        break

# for making color key
#key_point_names = [0, 1, 2, 5, 10, 25, 100, 250, 500, 1000, 2000]
#key_points = np.array([0, 1, 2, 5, 10, 25, 100, 250, 500, 1000, 2000])
#key_points += 1
#key_points = np.log(key_points)
#key_points /= key_points.max()
#
#key_colors = cm_viridis(key_points)
#print(key_colors)
#key_colors = [list(k) for k in key_colors]
#with open('output/all_hours/color_key.json', 'w') as fh:
#    json.dump({
#        'names': key_point_names,
#        'rgba_values': key_colors,
#    }, fh, indent=4)

#
#        day_bar = np.zeros((4, width))
#        day_span = (day / 365) * width
#        day_bar[0:2,0:int(day_span)] = 150
#
#        hour_bar = np.zeros((4, width))
#        hour_span = (hour / 24) * width
#        hour_bar[0:2,0:int(hour_span)] = 150
#
#        total = (h_data.sum() / total_max) * 500
#        total_bar = np.zeros((12, width))
#        total_bar[8:10,0:int(total)] = 200
#
#        hourly_totals[day][hour] = total
#
#        img = Image.fromarray(np.concatenate((day_bar, hour_bar, total_bar, data), axis=0)).convert('L')
#        #img = cm_viridis(np.array(img))
#        #img = np.uint8(img * 255)
#        #img = Image.fromarray(img)
#        img.save(output_dir + '/hourly/{0:06d}.png'.format(c))
#
#    hours.append({
#        'image': '{0:06d}.png'.format(c),
#        'total': h_data.sum(),
#        'hour': hour,
#        'day': day,
#        'datetime': (start_datetime + dt.timedelta(days=day, hours=hour)).strftime('%Y-%m-%d %H')
#    })
#    c += 1

#with open(output_dir + '/hourly.json', 'w') as fp:
#    fp.write(json.dumps({
#        'data': hours,
#    }, indent=True))

#for year in range(2012, 2016):
#    sample_b_fp = os.path.join(data_dir, '1km', 'Contiguous_US', 'total.{}.annual.nc'.format(year - 1))
#    sample_a_fp = os.path.join(data_dir, '1km', 'Contiguous_US', 'total.{}.annual.nc'.format(year))
#    nc_b = netCDF4.Dataset(sample_b_fp)
#    nc_a = netCDF4.Dataset(sample_a_fp)
#    ce_b = nc_b.variables['Carbon Emissions']
#    ce_a = nc_a.variables['Carbon Emissions']
#
#    # try different data compressions
#    #data = ce[:,:]
#    #data = data.flatten().filled(fill_value=0)
#    #data += 1
#    #data = np.log(data)
#    #data *= 255 / np.percentile(data, 99.5)
#
#    #print('{} points - min {} max {}'.format(len(data), data.min(), data.max()))
#    #for pct in np.arange(10, 100, 10):
#    #    print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
#    #for pct in np.arange(90, 100, 1):
#    #    print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
#
#    #print('preparing histogram of 99th percentile')
#    #plt.hist(data, range=(np.percentile(data, 99), 10000))
#    #plt.show()
#
#    ce_b = ce_b[:,:].filled(fill_value=0)
#    ce_a = ce_a[:,:].filled(fill_value=0)
#    ce_b += .000001
#    ce_a += .000001
#    ce_diff = ce_a / ce_b
#
#    data = ce_diff.flatten()
#    print('{} points - min {} max {}'.format(len(data), data.min(), data.max()))
#    for pct in np.arange(10, 100, 10):
#        print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
#    for pct in np.arange(90, 100, 1):
#        print('{} percentile: {}'.format(pct, np.percentile(data, pct)))
#
#    #print('preparing histogram of 99th percentile')
#    #plt.hist(data, range=(np.percentile(data, 99), 10000))
#    #plt.show()
#
#    ce = ce_diff
#    ce -= 1
#    ce *= 190
#    #ce += 255 / 2 # put no change in the middle, so now 50% is 255
#
#    #ce += 1
#    #ce = np.log(ce)
#    #ce *= 255 / np.percentile(ce, 99.95)
#    img = Image.fromarray(ce_diff)
#    img.convert('RGB').save(output_dir + '/pct_change_{}_bw.png'.format(year))
#    print(year)

