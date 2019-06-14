from PIL import Image, ImageDraw, ImageFont
import numpy as np
import datetime as dt
import glob

font_path = '/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf'
font = ImageFont.truetype(font_path, 40)
frame_time = dt.datetime(year=2015, day=1, hour=0, month=1)
format_string = '%H:%M'
frame_counter = 0


frames = glob.glob('/home/patrick/projects/kevin_gurney/la_hourly/output/pov/*.png')
frames = sorted(frames)
for frame in frames:
    img = Image.open(frame)
    if frame_counter < 61:
        pass
    elif frame_counter < 91:
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), frame_time.strftime(format_string), font=font)
    else:
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), frame_time.strftime(format_string), font=font)
        frame_time += dt.timedelta(minutes=2)
    img.save('output/overlay/{:06}.png'.format(frame_counter))
    frame_counter += 1
    print(frame_counter)

#
#for i in range(60):
#    img = Image.fromarray(np.zeros((600, 800, 4), dtype=np.uint8))
#    draw = ImageDraw.Draw(img)
#    img.save('output/overlay/{:06}.png'.format(frame_counter))
#    frame_counter += 1
#
#for i in range(30 * 24):
#    img = Image.fromarray(np.zeros((600, 800, 4), dtype=np.uint8))
#    draw = ImageDraw.Draw(img)
#    draw.text((10, 10), frame_time.strftime(format_string), font=font)
#    img.save('output/overlay/{:06}.png'.format(frame_counter))
#    frame_time += dt.timedelta(seconds=2)
#    #img.show()
#    frame_counter += 1
