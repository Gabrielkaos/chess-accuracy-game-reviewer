import numpy as np

class Undo:
    def __init__(self):
        self.move = 0
        self.fifty_move = 0
        self.en_passant = 0
        self.castle_rights = 0
        self.position_key = np.uint64(0)