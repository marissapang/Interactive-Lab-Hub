import busio
import time
import subprocess
import digitalio
import board
from PIL import Image, ImageDraw, ImageFont
import adafruit_rgb_display.st7789 as st7789
from adafruit_rgb_display.rgb import color565
from adafruit_bus_device.i2c_device import I2CDevice
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

# LED button
DEVICE_ADDRESS = 0x6f  # device address of our button
STATUS = 0x03 # reguster for button status
AVAILIBLE = 0x1
BEEN_CLICKED = 0x2
IS_PRESSED = 0x4

# I2C Commands
i2c = busio.I2C(board.SCL, board.SDA)
device = I2CDevice(i2c, DEVICE_ADDRESS)

def write_register(dev, register, value, n_bytes=1):
    # Write a wregister number and value
    buf = bytearray(1 + n_bytes)
    buf[0] = register
    buf[1:] = value.to_bytes(n_bytes, 'little')
    with dev:
        dev.write(buf)

def read_register(dev, register, n_bytes=1):
    # write a register number then read back the value
    reg = register.to_bytes(1, 'little')
    buf = bytearray(n_bytes)
    with dev:
        dev.write_then_readinto(reg, buf)
    return int.from_bytes(buf, 'little')

# helper function for drawing circles
def draw_countdown(total, current, y, w): 
    for i in range(0, total, 1):
        r = 10
        padding = 25
        spacing = (w - padding*2 - total*r*2)/(total-1)
        x_i = padding + i*r*2 + (i)*spacing
        if i <= current:
            draw.regular_polygon((x_i, y, r), n_sides =5, fill=orange)
        else: 
            draw.regular_polygon((x_i, y, r), n_sides =5, fill=gray)
# clear out settings
write_register(device, 0x1A, 1)
write_register(device, 0x1B, 0, 2)
write_register(device, 0x19, 0)

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
title_font = ImageFont.truetype("/usr/share/fonts/truetype/piboto/PibotoCondensed-Bold.ttf", 30)
title_coords = (15, 45)
guidance_font = ImageFont.truetype("/usr/share/fonts/truetype/piboto/PibotoCondensed-Bold.ttf", 45)
guidance_coords = (10, 10)
counter_font = ImageFont.truetype("/usr/share/fonts/truetype/piboto/PibotoCondensed-Bold.ttf", 28)
counter_coords = (15, 5)
orange = "#ff9e61"
gray = "#d9d9d9" 

click_count = 0
click_started = False

num_breaths = 0

while True:
    # Draw a black filled box to clear the image.
    draw.rectangle((0, 0, width, height), outline=0, fill=background_color)
    btn_status = read_register(device, STATUS)
    
    # when button is pressed down...    
    if (btn_status&IS_PRESSED) !=0:
        if click_started == False: # we start a new cycle... 
            click_started = True
            click_count = 0
        else: # or we continue a current cycle
            click_count += 1 
    else: # if button is not pressed...
        click_started = False # we reset
        click_count = 0   
    
    # display different commands depending on whether and for how long the button is pressed 
    display_text = "Time to breath?"
 
    if click_count == 0: 
        draw.text(title_coords, "Time to breathe?", font=title_font, fill="#FFFFFF")
        draw.text(counter_coords, str(num_breaths), font=counter_font, fill=orange)
    elif click_count % 19 != 0 and click_count % 19 <5:
        draw.text(guidance_coords, "Inhale", font=guidance_font, fill="#FFFFFF")
        draw_countdown(4, click_count % 19, 100, width)
    elif click_count % 19 != 0 and click_count % 19 <12:
        draw.text(guidance_coords, "Hold", font=guidance_font, fill="#FFFFFF")
        draw_countdown(7, (click_count-4) % 19, 100, width)
    elif click_count % 19 != 0 and click_count % 19 <19:
        draw.text(guidance_coords, "Exhale", font=guidance_font, fill="#FFFFFF")
        draw_countdown(9, (click_count-11) % 19, 100, width)
    elif click_count!= 0 and click_count % 19 == 0:
        num_breaths += 1
        draw.text(guidance_coords, "Exhale", font=guidance_font, fill="#FFFFFF")
        draw_countdown(9, (click_count-11) % 19, 100, width)


    disp.image(image, rotation)
    time.sleep(1)
