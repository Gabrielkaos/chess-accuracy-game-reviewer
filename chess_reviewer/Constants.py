import numpy as np
from Pieces import Pieces
from Squares import *

max_game_moves = 3000
max_pos_moves = 300
MAX_DEPTH = 128
BOARD_NUM_SQ = 120
INFINITE = 300000  # 5000000
IS_MATE = INFINITE - MAX_DEPTH
NO_MOVE = 0

# PV tables
HF_NONE = 0
HF_ALPHA = 1
HF_BETA = 2
HF_EXACT = 3

piece = Pieces()

# sq
NO_SQ = 99

# for sides
BOTH = 2
WHITE = 0
BLACK = 1

# castles
WKCA = 1
WQCA = 2
BKCA = 4
BQCA = 8

MVFLAGEP = 0x40000
MVFLAGPS = 0x80000
MVFLAGCA = 0x1000000
MVFLAGPROM = 0xF00000

RANK_1 = 0
RANK_2 = 1
RANK_3 = 2
RANK_4 = 3
RANK_5 = 4
RANK_6 = 5
RANK_7 = 6
RANK_8 = 7

FILE_A = 0
FILE_B = 1
FILE_C = 2
FILE_D = 3
FILE_E = 4
FILE_F = 5
FILE_G = 6
FILE_H = 7

# fen
START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# arrays
piece_value = np.array([0, 100, 300, 315, 500, 900, 5000, 100, 300, 315, 500, 900, 5000])
piece_color = np.array([BOTH, WHITE, WHITE, WHITE, WHITE, WHITE, WHITE, BLACK, BLACK, BLACK, BLACK, BLACK, BLACK])
piece_valid = np.array([False, True, True, True, True, True, True, True, True, True, True, True, True])
piece_big = np.array([False, False, True, True, True, True, True, False, True, True, True, True, True])
sq64_to_sq120 = np.array([21, 22, 23, 24, 25, 26, 27, 28, 31, 32, 33, 34, 35, 36, 37, 38, 41, 42, 43, 44, 45, 46, 47, 48,
                             51, 52, 53, 54, 55, 56, 57, 58, 61, 62, 63, 64, 65, 66, 67, 68, 71, 72, 73, 74, 75, 76, 77, 78,
                             81, 82, 83, 84, 85, 86, 87, 88, 91, 92, 93, 94, 95, 96, 97, 98], dtype=np.int)

sq120_to_sq64 = np.array([13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,13,
                          0,1,2,3,4,5,6,7,13,13,8,9,10,11,12,13,14,15,13,13,16,17,18,19,20,
                          21,22,23,13,13,24,25,26,27,28,29,30,31,13,13,32,33,34,35,36,37,38,
                          39,13,13,40,41,42,43,44,45,46,47,13,13,48,49,50,51,52,53,54,55,13,
                          13,56,57,58,59,60,61,62,63,13,13,13,13,13,13,13,13,13,13,13,13,13,
                          13,13,13,13,13,13,13,13], dtype=np.int)

rank7 = np.array([81,82,83,84,85,86,87,88])
rank2 = np.array([31,32,33,34,35,36,37,38])

END_PHASE = 171

mirror64 = np.array([
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
    8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 7
])

# squares to string
str_to_sq = {
    "a1": a1,
    "a2": a2,
    "a3": a3,
    "a4": a4,
    "a5": a5,
    "a6": a6,
    "a7": a7,
    "a8": a8,
    "b1": b1,
    "b2": b2,
    "b3": b3,
    "b4": b4,
    "b5": b5,
    "b6": b6,
    "b7": b7,
    "b8": b8,
    "c1": c1,
    "c2": c2,
    "c3": c3,
    "c4": c4,
    "c5": c5,
    "c6": c6,
    "c7": c7,
    "c8": c8,
    "d1": d1,
    "d2": d2,
    "d3": d3,
    "d4": d4,
    "d5": d5,
    "d6": d6,
    "d7": d7,
    "d8": d8,

    "e1": e1,
    "e2": e2,
    "e3": e3,
    "e4": e4,
    "e5": e5,
    "e6": e6,
    "e7": e7,
    "e8": e8,
    "f1": f1,
    "f2": f2,
    "f3": f3,
    "f4": f4,
    "f5": f5,
    "f6": f6,
    "f7": f7,
    "f8": f8,
    "g1": g1,
    "g2": g2,
    "g3": g3,
    "g4": g4,
    "g5": g5,
    "g6": g6,
    "g7": g7,
    "g8": g8,
    "h1": h1,
    "h2": h2,
    "h3": h3,
    "h4": h4,
    "h5": h5,
    "h6": h6,
    "h7": h7,
    "h8": h8,
    "-": NO_SQ
}
sq_to_str = {v: k for k, v in str_to_sq.items()}
