
from Constants import BOARD_NUM_SQ,WHITE,NO_SQ,piece
import numpy as np

def rand64():
    return np.random.randint(0, 2 ** 64, dtype=np.uint64)

def init_hash_keys(gs):
    for i in range(13):
        for j in range(BOARD_NUM_SQ):
            gs.piece_keys[i][j] = rand64()

    gs.side_key = rand64()

    for i in range(16):
        gs.castle_keys[i] = rand64()

def generate_pos_key(gs):
    pos_key = np.uint64(0)
    for i in range(13):
        for j in range(gs.num_pieces[i]):
            pos_key ^= gs.piece_keys[i][gs.piece_list[i][j]]

    if gs.side == WHITE:
        pos_key ^= gs.side_key

    pos_key ^= gs.castle_keys[gs.castle_rights]

    if gs.en_passant != NO_SQ:
        pos_key ^= gs.piece_keys[piece.EMPTY][gs.en_passant]

    return pos_key