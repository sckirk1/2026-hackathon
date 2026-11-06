import board
import busio
import digitalio
import random
import time
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
from rainbowio import colorwheel


# some color definitions
OFF = (0, 0, 0)


# Create the I2C object for the trellis
i2c_bus = busio.I2C(board.SCL, board.SDA)
print(f"{i2c_bus.scan()=}")

# This is for a 2x2 array of NeoTrellis boards:
trelli = [
    [NeoTrellis(i2c_bus, False, addr=0x2E), NeoTrellis(i2c_bus, False, addr=0x2F)],
    [NeoTrellis(i2c_bus, False, addr=0x30), NeoTrellis(i2c_bus, False, addr=0x31)],
]

trellis = MultiTrellis(trelli)

def brightness(xcoord, ycoord, edge):
    # Turn the LED on when a rising edge is detected
    if edge == NeoTrellis.EDGE_RISING:
        color = colorwheel(random.randrange(256))
        trellis.color(xcoord, ycoord, color)
        print(f"x={xcoord}, y={ycoord} pressed. Turning on color= 0x{color:06X}")
    # Turn the LED off when a falling edge is detected
    elif edge == NeoTrellis.EDGE_FALLING:
        trellis.color(xcoord, ycoord, OFF)
        print(f"x={xcoord}, y={ycoord} released")

# Turn off all LEDs
for y in range(8):
    for x in range(8):
        trellis.color(x, y, OFF)
        # Activate rising edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_RISING)
        # Activate falling edge events on all keys
        trellis.activate_key(x, y, NeoTrellis.EDGE_FALLING)
        trellis.set_callback(x, y, brightness)

while True:
    trellis.sync()
    # for y in range(8):
    #     for x in range(8):
    #         trellis.color(x, y, colorwheel(random.randrange(256)))
