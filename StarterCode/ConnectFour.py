import enum
import typing
import threading
import time

from NeoTrellisGame import NeoTrellisGame, AbstractNeoTrellisGame
from adafruit_neotrellis.multitrellis import MultiTrellis
from adafruit_neotrellis.neotrellis import NeoTrellis #TODO: Make this import better

RED = (255, 40 , 40)
GREEN = (40, 255, 40)
BLUE = (40, 40, 255)
ORANGE = (242, 140, 40)
PURPLE = (191, 64, 191)
WHITE = (50, 50, 50)
OFF = (0, 0, 0)

# Represents the state of the board in the game_state matrix
class CellState(enum.IntEnum):
    EMPTY = -1
    PLAYER_1 = 0
    PLAYER_2 = 1
    PLAYER_3 = 2
    PLAYER_4 = 3

# Row is the NeoTrellis Y and Col is the NeoTrellis X
NUMBER_OF_GAME_ROWS = 6
NUMBER_OF_GAME_COLUMNS = 8
ROW_OFFSET = 8 - NUMBER_OF_GAME_ROWS
NUMBER_TO_WIN = 4

def debug(val):
    print(threading.current_thread().getName() + ": " + val)

class ConnectFour:
    def __init__(self, game: typing.Optional[AbstractNeoTrellisGame] = None):
        self.game = game if game is not None else NeoTrellisGame()
        super().__init__()
        self.show_player_select()

    def empty_callback(self, x, y, edge):
        pass

    def reset_all_key_colors(self):
        for row in range(8):
            for col in range(8):
                self.game.set_cell_color(row, col, OFF)

    def show_player_select(self):
        self.enable_all_keys()

        self.reset_all_key_colors()
        self.game.set_cell_color(0, 7, GREEN)
        self.game.set_cell_color(0, 5, BLUE)
        self.game.set_callback(0, 7, self.setup_game_for_players)
        
        self.game.set_cell_color(2, 7, GREEN)
        self.game.set_cell_color(2, 5, BLUE)
        self.game.set_cell_color(2, 4, BLUE)
        self.game.set_callback(2, 7, self.setup_game_for_players)

        self.game.set_cell_color(5, 7, GREEN)
        self.game.set_cell_color(5, 5, BLUE)
        self.game.set_cell_color(5, 4, BLUE)
        self.game.set_cell_color(5, 3, BLUE)
        self.game.set_callback(5, 7, self.setup_game_for_players)

        self.game.set_cell_color(7, 7, GREEN)
        self.game.set_cell_color(7, 5, BLUE)
        self.game.set_cell_color(7, 4, BLUE)
        self.game.set_cell_color(7, 3, BLUE)
        self.game.set_cell_color(7, 2, BLUE)
        self.game.set_callback(7, 7, self.setup_game_for_players)
        self.game.update_display()
        
    def setup_game_for_players(self, x, y, edge):
        if (x == 2):
            self.number_of_players = 2
        elif(x == 5):
            self.number_of_players = 3
        elif(x == 7):
            self.number_of_players = 4
        else:
            self.number_of_players = 2 #To Do: CPU?
        
        self.show_winning_length_select()

    def show_winning_length_select(self):
        self.reset_all_key_colors()
        self.game.set_cell_color(0, 0, GREEN)
        self.game.set_cell_color(2, 0, BLUE)
        self.game.set_cell_color(3, 0, BLUE)
        self.game.set_cell_color(4, 0, BLUE)
        self.game.set_callback(0, 0, self.setup_game_for_win_length)
        
        self.game.set_cell_color(0, 2, GREEN)
        self.game.set_cell_color(2, 2, BLUE)
        self.game.set_cell_color(3, 2, BLUE)
        self.game.set_cell_color(4, 2, BLUE)
        self.game.set_cell_color(5, 2, BLUE)
        self.game.set_callback(0, 2, self.setup_game_for_win_length)

        self.game.set_cell_color(0, 5, GREEN)
        self.game.set_cell_color(2, 5, BLUE)
        self.game.set_cell_color(3, 5, BLUE)
        self.game.set_cell_color(4, 5, BLUE)
        self.game.set_cell_color(5, 5, BLUE)
        self.game.set_cell_color(6, 5, BLUE)
        self.game.set_callback(0, 5, self.setup_game_for_win_length)

        self.game.set_cell_color(0, 7, GREEN)
        self.game.set_cell_color(2, 7, BLUE)
        self.game.set_cell_color(3, 7, BLUE)
        self.game.set_cell_color(4, 7, BLUE)
        self.game.set_cell_color(5, 7, BLUE)
        self.game.set_cell_color(6, 7, BLUE)
        self.game.set_cell_color(7, 7, BLUE)
        self.game.set_callback(0, 7, self.setup_game_for_win_length)
        self.game.update_display()


    def setup_game_for_win_length(self, x, y, edge):
        if (y == 0):
            self.win_length = 3
        elif (y == 2):
            self.win_length = 4
        elif(y == 5):
            self.win_length = 5
        elif(y == 7):
            self.win_length = 6
        else:
            self.win_length = 4
        
        self.register_two_player_callbacks()
        self.reset_game()
    
    def register_two_player_callbacks(self):
        for col in range(NUMBER_OF_GAME_COLUMNS):
            self.game.set_callback(col, 0, self.handle_button_event)
            self.game.activate_key(col, 0, NeoTrellis.EDGE_RISING)

    def register_end_game_callbacks(self):
        for col in range(NUMBER_OF_GAME_COLUMNS):
            self.game.set_callback(col, 0, None)
        self.game.set_callback(0, 0, self.player_select_from_callback)
        self.game.activate_key(0, 0, NeoTrellis.EDGE_RISING)
        self.game.set_callback(7, 0, self.reset_game_from_callback)
        self.game.activate_key(7, 0, NeoTrellis.EDGE_RISING)
        self.game.update_display()

    def reset_game_from_callback(self, x, y, edge):
        self.reset_game()
        self.register_two_player_callbacks()
        self.game.stop_sound("cheer.mp3")

    def player_select_from_callback(self, x, y, edge):
        self.reset_all_key_colors()
        self.show_player_select()

    def reset_game(self):
        self.game_state = [] # Zero indexed: Row, Column
        self.current_player = CellState.PLAYER_1

        for col in range(8):
            self.game.set_cell_color(1, col, OFF)

        for i in range(NUMBER_OF_GAME_ROWS):
            self.game_state.append([CellState.EMPTY] * NUMBER_OF_GAME_COLUMNS)
        self.show_current_player()
        self.update_board_colors()
  
    def handle_button_event(self, x, y, edge):
        if not self.is_column_full(x):
            self.drop_piece(x)

    def find_lowest_empty_row(self, col: int):
        for row_index in range(NUMBER_OF_GAME_ROWS):
            if self.game_state[NUMBER_OF_GAME_ROWS - row_index - 1][col] == CellState.EMPTY:
                return NUMBER_OF_GAME_ROWS - row_index - 1
        return -1 # -1 means the column is full

    def drop_piece(self, col: int):
        self.game_state[self.find_lowest_empty_row(col)][col] = self.current_player
        self.game.play_sound('clack.mp3')
        self.update_board_colors()
        win, winning_sequence = self.check_win()
        tie = self.board_is_full()
        if not win and not tie:
            self.switch_player()
        elif win:
            self.show_winner(winning_sequence) 
        else:
            self.show_tie_game()

    def switch_player(self):
        if self.current_player == CellState.PLAYER_1:
            self.current_player = CellState.PLAYER_2
        elif self.current_player == CellState.PLAYER_2:
            if self.number_of_players != 2:
                self.current_player = CellState.PLAYER_3
            else:
                self.current_player = CellState.PLAYER_1
        elif self.current_player == CellState.PLAYER_3:
            if self.number_of_players != 3:
                self.current_player = CellState.PLAYER_4
            else:
                self.current_player = CellState.PLAYER_1
        else:
            self.current_player = CellState.PLAYER_1

        self.show_current_player()

    def show_current_player(self):
        for col in range(NUMBER_OF_GAME_COLUMNS):
            if self.is_column_full(col):
                self.game.set_cell_color(col, 0, OFF)
                self.game.activate_key(col, 0, NeoTrellis.EDGE_RISING, False)
            else:
                self.game.set_cell_color(col, 0, self.get_player_color(self.current_player))
        self.game.update_display()

    def board_is_full(self) -> bool:
        for col in range(NUMBER_OF_GAME_COLUMNS):
            if not self.is_column_full(col):
                return False
        return True

    def update_board_colors(self):
        for row_index, row in enumerate(self.game_state):
            for col_index, col in enumerate(row):

                self.game.set_cell_color(col_index, row_index + ROW_OFFSET, self.get_player_color(col))
        self.game.update_display()

    def get_player_color(self, player: CellState) -> tuple[int, int, int]:
        if player == CellState.PLAYER_1:
            return RED
        elif player == CellState.PLAYER_2:
            return BLUE
        elif player == CellState.PLAYER_3:
            return ORANGE
        elif player == CellState.PLAYER_4:
            return PURPLE
        else:
            return WHITE

    def animate_piece_drop(self, col: int, player: int):
        pass

    def play_animation(self, animation, cells=None):
        self.disable_all_keys()
        if (cells != None):
            animation(cells);
        else:
            animation()
        self.enable_all_keys()

    def is_column_full(self, col: int) -> bool:
        for row in self.game_state:
            if row[col] == CellState.EMPTY:
                return False
        return True

    def check_for_horizontal_win(self, row, col):
        current_col = col
        cells = []
        while current_col < NUMBER_OF_GAME_COLUMNS:
            if self.game_state[row][current_col] == self.current_player:
                cells.append((row, current_col))
                current_col += 1
            else:
                break
        return cells

    def check_for_vertical_win(self, row, col):
        current_row = row
        cells = []
        while current_row < NUMBER_OF_GAME_ROWS:
            if self.game_state[current_row][col] == self.current_player:
                cells.append((current_row, col))
                current_row += 1
            else:
                break
        return cells

    def check_for_diagonal_win_1(self, row, col):
        current_row = row
        current_col = col
        cells = []
        while current_row < NUMBER_OF_GAME_ROWS and current_col < NUMBER_OF_GAME_COLUMNS:
            if self.game_state[current_row][current_col] == self.current_player:
                cells.append((current_row, current_col))
                current_row += 1
                current_col += 1
            else:
                break
        return cells

    def check_for_diagonal_win_2(self, row, col):
        current_row = row
        current_col = col
        cells = []
        while current_row >= 0 and current_col < NUMBER_OF_GAME_COLUMNS:
            if self.game_state[current_row][current_col] == self.current_player:
                cells.append((current_row, current_col))
                current_row -= 1
                current_col += 1
            else:
                break
        return cells

    def check_win(self):
        win_checkers = [self.check_for_horizontal_win, self.check_for_vertical_win, self.check_for_diagonal_win_1, self.check_for_diagonal_win_2]
        for col_index in range(NUMBER_OF_GAME_COLUMNS):
            for row_index in range(NUMBER_OF_GAME_ROWS):
                if self.game_state[row_index][col_index] == self.current_player:
                    for f in win_checkers:
                        longest_sequence = f(row_index, col_index)
                        if len(longest_sequence) >= self.win_length: 
                            return True, longest_sequence
        return False, []

    def disable_all_keys(self):
        for x in range(8):
            for y in range(8):
                self.game.activate_key(x, y, edge=NeoTrellis.EDGE_RISING, enable=False)

    def enable_all_keys(self):
        self.game.clear_keypad_buffer()
        for x in range(8):
            for y in range(8):
                self.game.activate_key(x, y, edge=NeoTrellis.EDGE_RISING, enable=True)

    def show_draw(self):
        for i in range(10):
            for row in range(NUMBER_OF_GAME_ROWS):
                for col in range(NUMBER_OF_GAME_COLUMNS):
                    self.game.set_cell_color(col, row + ROW_OFFSET, (0,0,0))
                self.game.update_display()

            for row in range(NUMBER_OF_GAME_ROWS):
                for col in range(NUMBER_OF_GAME_COLUMNS):
                    self.game.set_cell_color(col, row + ROW_OFFSET, self.get_player_color(self.game_state[row][col]))
                self.game.update_display()

    def highlight_winning_sequence(self, cells):
        for i in range(10):
            for cell in cells:
                self.game.set_cell_color(cell[1], cell[0] + ROW_OFFSET, (40, 255, 40))
                self.game.update_display()
            for cell in cells:
                self.game.set_cell_color(cell[1], cell[0] + ROW_OFFSET, self.get_player_color(self.current_player))
                self.game.update_display()

    def show_winner(self, winning_sequence):
        self.register_end_game_callbacks()
        for col in range(NUMBER_OF_GAME_COLUMNS):
            self.game.set_cell_color(col, 0, OFF)
        self.game.set_cell_color(7, 0, GREEN)
        self.game.set_cell_color(0,0, ORANGE)
        self.game.play_sound("cheer.mp3")
        self.play_animation(self.highlight_winning_sequence, cells=winning_sequence)

    def show_tie_game(self):
        self.register_end_game_callbacks()
        for col in range(NUMBER_OF_GAME_COLUMNS):
            self.game.set_cell_color(col, 0, OFF)
        self.game.set_cell_color(7, 0, GREEN)
        self.game.set_cell_color(0,0, ORANGE)
        self.game.play_sound("aww.mp3")
        self.play_animation(self.show_draw)


