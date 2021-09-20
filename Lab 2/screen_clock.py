import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from adafruit_rgb_display.rgb import color565

from datetime import datetime

# Configuration for CS and DC pins (these are FeatherWing defaults on M0/M4):
cs_pin = digitalio.DigitalInOut(board.CE0)
dc_pin = digitalio.DigitalInOut(board.D25)
reset_pin = None

# Config for display baudrate (default max is 24mhz):
BAUDRATE = 64000000

# Setup SPI bus using hardware SPI:
spi = board.SPI()

# Create the ST7789 display:
disp = st7789.ST7789(
    spi,
    cs=cs_pin,
    dc=dc_pin,
    rst=reset_pin,
    baudrate=BAUDRATE,
    width=135,
    height=240,
    x_offset=53,
    y_offset=40,
)

# Create blank image for drawing.
# Make sure to create image with mode 'RGB' for full color.
height = disp.width  # we swap height/width to rotate it to landscape!
width = disp.height
image = Image.new("RGB", (width, height))
rotation = 90

# Get drawing object to draw on image.
draw = ImageDraw.Draw(image)

# Draw a black filled box to clear the image.
draw.rectangle((0, 0, width, height), outline=0, fill=(0, 0, 0))
disp.image(image, rotation)
# Draw some shapes.
# First define some constants to allow easy resizing of shapes.
padding = -2
top = padding
bottom = height - padding
# Move left to right keeping track of the current x position for drawing shapes.
x = 0

# Alternatively load a TTF font.  Make sure the .ttf font file is in the
# same directory as the python script!
# Some other nice fonts to try: http://www.dafont.com/bitmap.php
# font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)

# Turn on the backlight
backlight = digitalio.DigitalInOut(board.D22)
backlight.switch_to_output()
backlight.value = True

# Buttons
buttonA = digitalio.DigitalInOut(board.D23)
buttonB = digitalio.DigitalInOut(board.D24)
buttonA.switch_to_input()
buttonB.switch_to_input()

##### LAB PART D & E - Styling Variables #####
background_color = "#8ad7e3"
title_font = ImageFont.truetype("/usr/share/fonts/truetype/piboto/PibotoCondensed-Bold.ttf", 27)
date_font = ImageFont.truetype("/usr/share/fonts/truetype/piboto/PibotoCondensed-Bold.ttf", 42)
title_coords = (10, 10)
bar_x = 10
bar_y = 60
bar_h = 35
bar_w = width-20
filled_color = "#ff9e61"
empty_color = "#d9d9d9" 

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=background_color)
   
    ##### LAB PART E - A clock that shows the % of day & year that has passed #####
    # Trying to go for a clock that's a little "self-help" a little "philosophical"
    # by having short phrases at the top of each interface
    
    # get current date time in tuple form
    now_tuple = datetime.now().timetuple()
    now = datetime.now()
    if buttonA.value: # show % of day that has passed by default
        # days interface
        draw.text(title_coords, "Days pass slowly", font=title_font, fill="#FFFFFF")
        hour = now_tuple[3]
        day_pct = hour/24
        draw.rectangle((bar_x, bar_y, bar_x + day_pct*bar_w,bar_y+bar_h), fill=filled_color)
        draw.rectangle((bar_x + day_pct*bar_w, bar_y, bar_x + bar_w, bar_y+bar_h), fill=empty_color) 
    elif buttonB.value: # shows % of year that has passed when top button pressed
        # years interface
        draw.text(title_coords, "Years fly by", font=title_font, fill="#FFFFFF")
        day_num = now_tuple.tm_yday
        year_pct = day_num/365
        draw.rectangle((bar_x, bar_y, bar_x + year_pct*bar_w,bar_y+bar_h), fill=filled_color)
        draw.rectangle((bar_x + year_pct*bar_w, bar_y, bar_x + bar_w, bar_y+bar_h), fill=empty_color)
    else : # show bare bones clock form part D
        ##### Lab PART D #####
        draw.text(title_coords, "Is it time yet??", font=title_font, fill="#FFFFFF")
        draw.text((bar_x, bar_y), now.strftime("%H:%M:%S"), font=date_font, fill=filled_color)
    # Display image
    disp.image(image, rotation)
    time.sleep(1)
