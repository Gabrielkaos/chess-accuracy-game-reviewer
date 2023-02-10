import numpy as np
from Constants import WHITE,piece,piece_color
from Asserts import is_piece_knight,is_pce_offboard,is_piece_king,is_pce_empty,is_piece_BQ,is_piece_RQ

knight_offsets=np.array([21,19,-21,-19,12,8,-12,-8])
king_offsets=np.array([10,9,11,-10,-9,-11,1,-1])
bishop_offsets=np.array([9,11,-9,-11])
rook_offsets=np.array([1,-1,10,-10])

def is_attacked(sq,side,board):

    if side==WHITE:
        #pawns
        if (board.pieces120[sq-11]==piece.white_pawn) or\
                (board.pieces120[sq-9]==piece.white_pawn):
            return True
    else:
        # pawns
        if (board.pieces120[sq + 11] == piece.black_pawn) or \
                (board.pieces120[sq + 9] == piece.black_pawn):
            return True

    # rooks and queens
    for dir in rook_offsets:
        t_sq=sq+dir
        pce=board.pieces120[t_sq]
        while not is_pce_offboard(board.pieces120[t_sq]):
            if not is_pce_empty(pce):
                if is_piece_RQ(pce) and piece_color[pce] == side:
                    return True
                break
            t_sq += dir
            pce = board.pieces120[t_sq]

    #bishops and queens
    for dir in bishop_offsets:
        t_sq = sq + dir
        pce = board.pieces120[t_sq]
        while not is_pce_offboard(board.pieces120[t_sq]):
            if not is_pce_empty(pce):
                if is_piece_BQ(pce) and piece_color[pce] == side:
                    return True
                break
            t_sq += dir
            pce = board.pieces120[t_sq]

    #kings
    for dir in king_offsets:
        t_sq=sq+dir
        pce=board.pieces120[t_sq]
        if not is_pce_offboard(pce) and is_piece_king(pce) and\
                piece_color[pce]==side:
            return True

    #knights
    for dir in knight_offsets:
        t_sq=sq+dir
        pce=board.pieces120[t_sq]
        if not is_pce_offboard(pce) and is_piece_knight(pce)\
                and piece_color[pce]==side:
            return True

    return False