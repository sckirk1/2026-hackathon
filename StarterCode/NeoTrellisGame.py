import abc
import typing

import board

import busio
import digitalio
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis
import pygame.mixer
import os


class AbstractNeoTrellisGame(abc.ABC):
    @abc.abstractmethod
    def init_hardware(self):
        """Initializes the LED board."""
        pass

    @abc.abstractmethod
    def set_cell_color(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        """Sets the color of a cell at the given coordinates."""
        pass

    @abc.abstractmethod
    def update_display(self):
        """Updates the LED display to reflect any changes made to cell colors."""
        pass

    @abc.abstractmethod
    def clear_board(self):
        """Clears board by turning off all LEDs"""
        pass

    @abc.abstractmethod
    def sync(self):
        """Read any events from the LED display and call callbacks if any events have occurred."""
        pass

    @abc.abstractmethod
    def set_callback(self, x: int, y: int, callback) -> None:
        """Sets a callback function for a cell at the given coordinates."""
        pass

    @abc.abstractmethod
    def activate_key(self, x: int, y: int, edge, enable: typing.Optional[bool] = True) -> None:
        """Activates a key at the given coordinates for a specific edge event."""
        pass


class NeoTrellisGame(AbstractNeoTrellisGame):
    
    def __init__(self):
        self._board = None
        pygame.mixer.init()
        self.init_hardware()
        self._sounds = {}

    #GIVEN
    def init_hardware(self):
        print("Initializing Hardware")
        i2c_bus = busio.I2C(board.SCL, board.SDA)

        self.__boards = [
            [NeoTrellis(i2c_bus, False, addr=0x2E, auto_write=False), NeoTrellis(i2c_bus, False, addr=0x2F, auto_write=False)],
            [NeoTrellis(i2c_bus, False, addr=0x30, auto_write=False), NeoTrellis(i2c_bus, False, addr=0x31, auto_write=False)],
            ]
        self._board = MultiTrellis(self.__boards)
        print("Hardware is ready")
  
    #GIVEN
    #An alternative is to let them register callbacks with the registerCallback(x, y, callback) instead of the index based one
    def key_index_to_xy_coordinates(self, index: int) -> tuple[int, int]:
        if index < 0 or index > 63:
            raise ValueError(f"Index must be between 0 and 63 inclusive. Was {index}")
        else:
            x = int(index / 8)
            y = int(index % 8)
            return x, y
      
    #GIVEN
    def xy_coordinates_to_key_index(self, x: int, y: int) -> int:
        self.validate_coordinates(x,y)
        return (x * 8) + y
    
    #GIVEN
    def validate_coordinates(self, x: int, y: int):
        if x < 0 or x > 7:
            raise ValueError(f"X coordinate must be between 0 and 7 inclusive. Was {x}") 
        
        if y < 0 or y > 7:
            raise ValueError(f"Y coordinate must be between 0 and 7 inclusive. Was {y}") 
    
    #GIVEN
    def set_cell_color(self, x: int, y: int, color: tuple[int, int, int]) -> None:
        self.validate_coordinates(x, y)
        for rgbValue in color:
            if rgbValue < 0 or rgbValue > 255:
                raise ValueError(f"All RGB values in the color must be between 0 and 255 inclusive. Was {color}")
        self._board.color(x, y, color)
    
    #GIVEN
    def update_display(self):
        self._board.show()

    def clear_board(self):
        """Clears board by turning off all LEDs"""
        for x in range(8):
            for y in range(8):
                self.set_cell_color(x, y, (0, 0, 0))
        self.update_display()

    def sync(self):
        self._board.sync()

    def set_callback(self, x: int, y: int, callback) -> None:
        self._board.set_callback(x, y, callback)

    def activate_key(self, x: int, y: int, edge, enable=True) -> None:
        self._board.activate_key(x, y, edge, enable)
    
    def clear_keypad_buffer(self):
        for row in self.__boards:
            for trel in row:
                trel.read_keypad(trel.count)

    def play_sound(self, sound_name, extra_plays=0):
        sound_to_play = None
        try:
            sound_to_play = self.sounds[sound_name]
        except:
            sound_to_play = pygame.mixer.Sound(os.path.join("StarterCode", "sounds", sound_name))
            self._sounds[sound_name] = sound_to_play
        sound_to_play.play(loops=extra_plays)

    def stop_sound(self, sound_name):
        try: 
            self._sounds[sound_name].stop()
        except Exception:
            pass

