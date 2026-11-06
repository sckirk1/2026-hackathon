import time

from ConnectFour import ConnectFour

connect_four = ConnectFour()
connect_four.game.update_display()
while True:
    try:
        connect_four.game.sync()
        time.sleep(0.1)
    except KeyboardInterrupt:
        # clear board
        print("\nClosing game...")
        connect_four.game.clear_board()
        exit()  # quit

