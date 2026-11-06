import board
import busio
import digitalio
import random
import time
from adafruit_neotrellis.neotrellis import NeoTrellis
from rainbowio import colorwheel


# some color definitions
OFF = (0, 0, 0)


# Create the I2C object for the trellis
i2c_bus = busio.I2C(board.SCL, board.SDA)
print(f"{i2c_bus.scan()=}")

# Create the trellis
trellis = NeoTrellis(i2c_bus, addr=0x2E, auto_write=False)

def brightness(event):
    # Increase brightness
    if event.number < 8:  # increase with top half
        trellis.brightness = min(1.00, trellis.brightness + 0.05)
    else:  # decrease with bottom half
        trellis.brightness = max(0.05, trellis.brightness - 0.05)
    print(f"{trellis.brightness=:.2f}")

# Turn off all LEDs
for i in range(16):
    trellis.pixels[i] = OFF
    trellis.activate_key(i, NeoTrellis.EDGE_RISING)
    # trellis.activate_key(i, NeoTrellis.EDGE_FALLING)
    trellis.callbacks[i] = brightness

while True:
    try:
        trellis.sync()
        for i in range(16):
            trellis.pixels[i] = colorwheel(random.randrange(256))
        trellis.show()
    except KeyboardInterrupt:
        # Turn off all LEDs
        print("\nLeaving the disco...")
        for i in range(16):
            trellis.pixels[i] = OFF
        trellis.show()
        exit()

