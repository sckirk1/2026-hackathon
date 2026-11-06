import board
import busio
import digitalio
import random
import time
from adafruit_neotrellis.neotrellis import NeoTrellis
from rainbowio import colorwheel


# some color definitions
OFF = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
RGB = [RED, GREEN, BLUE]

def blink(event):
    # event definition: https://github.com/adafruit/Adafruit_CircuitPython_seesaw/blob/main/adafruit_seesaw/keypad.py#L34
    # turn the LED on when a rising edge is detected
    if event.edge == NeoTrellis.EDGE_RISING:
        color = colorwheel(random.randrange(256))
        trellis.pixels[event.number] = color
        print(f"Button {event.number} pressed. Turning on color= 0x{color:06X}")
    # turn the LED off when a falling edge is detected
    elif event.edge == NeoTrellis.EDGE_FALLING:
        trellis.pixels[event.number] = OFF
        print(f"Button {event.number} released")

# Setup interrupt (INT) pin
int_pin = digitalio.DigitalInOut(board.D4)
int_pin.direction = digitalio.Direction.INPUT
print(f"{int_pin.value=}")

#create the i2c object for the trellis
i2c_bus = busio.I2C(board.SCL, board.SDA)
print(f"{i2c_bus.scan()=}")

#create the trellis
trellis = NeoTrellis(i2c_bus, addr=0x2E)

for i in range(16):
    # activate rising edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # activate falling edge events on all keys
    trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    # set all keys to trigger the blink callback
    trellis.callbacks[i] = blink

    # cycle the LEDs on startup
    trellis.pixels[i] = RGB[i%3]
    time.sleep(0.05)

for i in range(16):
    trellis.pixels[i] = OFF
    time.sleep(0.05)
    
while True:
    # call the sync function call any triggered callbacks
    trellis.sync()
    # the trellis can only be read every 17 millisecons or so
    time.sleep(0.02)

