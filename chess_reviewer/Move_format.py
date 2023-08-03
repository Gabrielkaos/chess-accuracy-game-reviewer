from Constants import piece, max_pos_moves, piece_color, piece_value, WHITE, BLACK, piece_big
from Constants import MVFLAGEP, MVFLAGCA, MVFLAGPS, NO_SQ, NO_MOVE
from Asserts import is_piece_pawn, is_piece_king
from Attacks import is_attacked
from Squares import *
import numpy as np
from Other_functions import get_game_phase

castlePerm = np.array([
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 13, 15, 15, 15, 12, 15, 15, 14, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 7, 15, 15, 15, 3, 15, 15, 11, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15,
    15, 15, 15, 15, 15, 15, 15, 15, 15, 15

])

class MoveClass:
    def __init__(self):
        self.score = 0
        self.move = 0

class MoveList:
    def __init__(self):
        self.moves = np.array([MoveClass() for _ in range(max_pos_moves)])
        self.count = 0


def MOVE(f, t, cap, prom, flag): return f | (t << 7) | (cap << 14) | (prom << 20) | flag


def FROMSQ(m): return m & 0x7F


def TOSQ(m): return (m >> 7) & 0x7F


def CAPTURED(m): return (m >> 14) & 0xF


def PROMOTED(m): return (m >> 20) & 0xF


def hash_ep(board):
    hash_piece = board.piece_keys[piece.EMPTY][board.en_passant]
    board.position_key ^= hash_piece


def hash_ca(board):
    hash_piece = board.castle_keys[board.castle_rights]
    board.position_key ^= hash_piece


def hash_side(board):
    hash_piece = board.side_key
    board.position_key ^= hash_piece


def hash_pce(board, pce, sq):
    hash_piece = board.piece_keys[pce][sq]
    board.position_key ^= hash_piece


def clear_piece(board, sq):
    pce = board.pieces120[sq]
    col = piece_color[pce]
    t_piece = -1

    if piece_big[pce]:
        board.big_piece[col] -= 1

    hash_pce(board, pce, sq)

    board.pieces120[sq] = piece.EMPTY

    board.material[col] -= piece_value[pce]

    # remove from piecelist
    for index in range(board.num_pieces[pce]):
        if board.piece_list[pce][index] == sq:
            t_piece = index
            break

    board.num_pieces[pce] -= 1
    board.piece_list[pce][t_piece] = board.piece_list[pce][board.num_pieces[pce]]
    board.game_phase = get_game_phase(board)


def move_piece(board, from_sq, to_sq):
    pce = board.pieces120[from_sq]

    hash_pce(board, pce, from_sq)

    board.pieces120[from_sq] = piece.EMPTY

    hash_pce(board, pce, to_sq)

    board.pieces120[to_sq] = pce

    for index in range(board.num_pieces[pce]):
        if board.piece_list[pce][index] == from_sq:
            board.piece_list[pce][index] = to_sq
            break


def add_piece(board, sq, pce):
    col = piece_color[pce]

    if piece_big[pce]:
        board.big_piece[col] += 1

    hash_pce(board, pce, sq)

    board.pieces120[sq] = pce

    board.material[col] += piece_value[pce]

    board.piece_list[pce][board.num_pieces[pce]] = sq
    board.num_pieces[pce] += 1
    board.game_phase = get_game_phase(board)


def make_move(board, move):
    from_sq = FROMSQ(move)
    to_sq = TOSQ(move)
    side = board.side

    board.history[board.his_ply].position_key = board.position_key

    # if enpassant
    if move & MVFLAGEP:
        if side == WHITE:
            clear_piece(board, to_sq - 10)
        elif side == BLACK:
            clear_piece(board, to_sq + 10)

    # if castle
    if move & MVFLAGCA:
        if to_sq == c1:
            move_piece(board, a1, d1)
        elif to_sq == g1:
            move_piece(board, h1, f1)

        elif to_sq == c8:
            move_piece(board, a8, d8)
        elif to_sq == g8:
            move_piece(board, h8, f8)

    # hash enpassant
    if board.en_passant != NO_SQ:
        hash_ep(board)

    # hash castle
    hash_ca(board)

    board.history[board.his_ply].move = move
    board.history[board.his_ply].fifty_move = board.fifty_move
    board.history[board.his_ply].en_passant = board.en_passant
    board.history[board.his_ply].castle_rights = board.castle_rights

    # update castle rights
    board.castle_rights &= castlePerm[from_sq]
    board.castle_rights &= castlePerm[to_sq]

    # enpas
    board.en_passant = NO_SQ

    # hash castle
    hash_ca(board)

    # fiftymove
    board.fifty_move += 1

    captured = CAPTURED(move)
    if captured != piece.EMPTY:
        clear_piece(board, to_sq)
        board.fifty_move = 0

    board.ply += 1
    board.his_ply += 1

    if is_piece_pawn(board.pieces120[from_sq]):
        board.fifty_move = 0
        if move & MVFLAGPS:
            if side == WHITE:
                board.en_passant = from_sq + 10
            elif side == BLACK:
                board.en_passant = from_sq - 10
            # hash enpassant
            hash_ep(board)

    move_piece(board, from_sq, to_sq)

    promoted_piece = PROMOTED(move)
    if promoted_piece != piece.EMPTY:
        clear_piece(board, to_sq)
        add_piece(board, to_sq, promoted_piece)

    if is_piece_king(board.pieces120[to_sq]):
        board.kingSq[board.side] = to_sq

    board.side ^= 1

    # hash side
    hash_side(board)

    if is_attacked(board.kingSq[side], board.side, board)[0]:
        undo_move(board)
        return False
    return True


def undo_move(board):
    board.ply -= 1
    board.his_ply -= 1

    move = board.history[board.his_ply].move

    from_sq = FROMSQ(move)
    to_sq = TOSQ(move)

    # hash enpassant
    if board.en_passant != NO_SQ:
        hash_ep(board)

    # hash castle
    hash_ca(board)

    board.castle_rights = board.history[board.his_ply].castle_rights
    board.en_passant = board.history[board.his_ply].en_passant
    board.fifty_move = board.history[board.his_ply].fifty_move

    # hash enpassant
    if board.en_passant != NO_SQ:
        hash_ep(board)

    # hash castle
    hash_ca(board)

    board.side ^= 1
    # hash side
    hash_side(board)

    if move & MVFLAGEP:
        if board.side == WHITE:
            add_piece(board, to_sq - 10, piece.black_pawn)
        elif board.side == BLACK:
            add_piece(board, to_sq + 10, piece.white_pawn)

    if move & MVFLAGCA:
        if to_sq == c1:
            move_piece(board, d1, a1)
        elif to_sq == g1:
            move_piece(board, f1, h1)

        elif to_sq == c8:
            move_piece(board, d8, a8)
        elif to_sq == g8:
            move_piece(board, f8, h8)

    move_piece(board, to_sq, from_sq)

    if is_piece_king(board.pieces120[from_sq]):
        board.kingSq[board.side] = from_sq

    captured = CAPTURED(move)
    if captured != piece.EMPTY:
        add_piece(board, to_sq, captured)

    promoted = PROMOTED(move)
    if promoted != piece.EMPTY:
        clear_piece(board, from_sq)
        add_piece(board, from_sq, (piece.white_pawn if piece_color[promoted] == WHITE else piece.black_pawn))


def make_null_move(board):
    board.ply += 1
    board.history[board.his_ply].position_key = board.position_key

    if board.en_passant != NO_SQ: hash_ep(board)
    board.history[board.his_ply].move = NO_MOVE
    board.history[board.his_ply].fifty_move = board.fifty_move
    board.history[board.his_ply].en_passant = board.en_passant
    board.history[board.his_ply].castle_rights = board.castle_rights
    board.en_passant = NO_SQ

    board.side ^= 1
    board.his_ply += 1
    hash_side(board)


def take_null_move(board):
    board.ply -= 1
    board.his_ply -= 1

    if board.en_passant != NO_SQ: hash_ep(board)

    board.fifty_move = board.history[board.his_ply].fifty_move
    board.en_passant = board.history[board.his_ply].en_passant = board.en_passant
    board.castle_rights = board.history[board.his_ply].castle_rights

    if board.en_passant != NO_SQ: hash_ep(board)
    board.side ^= 1
    hash_side(board)

if __name__ == "__main__":
    pass
