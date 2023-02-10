from Constants import piece, WHITE, \
    MVFLAGPS, MVFLAGEP, MVFLAGCA, piece_color, \
    BLACK, NO_SQ, WKCA, WQCA, BKCA, BQCA,rank2,rank7
from Squares import *
import numpy as np
from Attacks import is_attacked
from Move_format import CAPTURED, FROMSQ, TOSQ
from Move_format import MOVE,make_move,undo_move,MoveList

victim_score = np.array([0, 100, 200, 300, 400, 500, 600, 100, 200, 300, 400, 500, 600])
mvv_lva = np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                    [0, 105, 104, 103, 102, 101, 100, 105, 104, 103, 102, 101, 100],
                    [0, 205, 204, 203, 202, 201, 200, 205, 204, 203, 202, 201, 200],
                    [0, 305, 304, 303, 302, 301, 300, 305, 304, 303, 302, 301, 300],
                    [0, 405, 404, 403, 402, 401, 400, 405, 404, 403, 402, 401, 400],
                    [0, 505, 504, 503, 502, 501, 500, 505, 504, 503, 502, 501, 500],
                    [0, 605, 604, 603, 602, 601, 600, 605, 604, 603, 602, 601, 600],
                    [0, 105, 104, 103, 102, 101, 100, 105, 104, 103, 102, 101, 100],
                    [0, 205, 204, 203, 202, 201, 200, 205, 204, 203, 202, 201, 200],
                    [0, 305, 304, 303, 302, 301, 300, 305, 304, 303, 302, 301, 300],
                    [0, 405, 404, 403, 402, 401, 400, 405, 404, 403, 402, 401, 400],
                    [0, 505, 504, 503, 502, 501, 500, 505, 504, 503, 502, 501, 500],
                    [0, 605, 604, 603, 602, 601, 600, 605, 604, 603, 602, 601, 600]])
LoopSlidePiece = np.array([
    piece.white_bishop, piece.white_rook, piece.white_queen, 0, piece.black_bishop, piece.black_rook, piece.black_queen,
    0
])
LoopNonSlidePiece = np.array([piece.white_knight, piece.white_king, 0, piece.black_knight, piece.black_king, 0])
LoopSlideIndex = np.array([0, 4])
LoopNonSlideIndex = np.array([0, 3])
pieceDir = np.array([[0, 0, 0, 0, 0, 0, 0, 0],
                     [0, 0, 0, 0, 0, 0, 0, 0],
                     [-8, -19, -21, -12, 8, 19, 21, 12],
                     [-9, -11, 11, 9, 0, 0, 0, 0],
                     [-1, -10, 1, 10, 0, 0, 0, 0],
                     [-1, -10, 1, 10, -9, -11, 11, 9],
                     [-1, -10, 1, 10, -9, -11, 11, 9],

                     [0, 0, 0, 0, 0, 0, 0, 0],
                     [-8, -19, -21, -12, 8, 19, 21, 12],
                     [-9, -11, 11, 9, 0, 0, 0, 0],
                     [-1, -10, 1, 10, 0, 0, 0, 0],
                     [-1, -10, 1, 10, -9, -11, 11, 9],
                     [-1, -10, 1, 10, -9, -11, 11, 9]])
numDir = np.array([0, 0, 8, 4, 4, 8, 8, 0, 8, 4, 4, 8, 8])


def is_sq_offboard(board, sq):
    return board.pieces120[sq] == piece.OFF_BOARD


def add_capture(move_list, move, board):
    pce_cap = CAPTURED(move)
    pce_from = board.pieces120[FROMSQ(move)]

    move_list.moves[move_list.count].move = move
    move_list.moves[move_list.count].score = mvv_lva[pce_cap][pce_from] + 1000000

    move_list.count += 1


def add_enpassant(move_list, move):
    move_list.moves[move_list.count].move = move
    move_list.moves[move_list.count].score = 1000105
    move_list.count += 1


def add_quiet_moves(move_list, move, board):
    move_list.moves[move_list.count].move = move
    if board.search_killers[0][board.ply] == move:
        move_list.moves[move_list.count].score = 900000
    elif board.search_killers[1][board.ply] == move:
        move_list.moves[move_list.count].score = 800000
    else:
        move_list.moves[move_list.count].score = board.search_history[board.pieces120[FROMSQ(move)]][TOSQ(move)]

    move_list.count += 1


def add_white_pawn_captures(move_list, from_sq, to_sq, cap, board):
    if from_sq in rank7:
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.white_queen, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.white_rook, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.white_bishop, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.white_knight, 0), board)
    else:
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.EMPTY, 0), board)


def add_white_pawn_moves(move_list, from_sq, to_sq, board):
    if from_sq in rank7:
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.white_queen, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.white_bishop, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.white_rook, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.white_knight, 0), board)
    else:
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.EMPTY, 0), board)


def add_black_pawn_captures(move_list, from_sq, to_sq, cap, board):
    if from_sq in rank2:
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.black_queen, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.black_rook, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.black_bishop, 0), board)
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.black_knight, 0), board)
    else:
        add_capture(move_list, MOVE(from_sq, to_sq, cap, piece.EMPTY, 0), board)


def add_black_pawn_moves(move_list, from_sq, to_sq, board):
    if from_sq in rank2:
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.black_queen, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.black_bishop, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.black_rook, 0), board)
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.black_knight, 0), board)
    else:
        add_quiet_moves(move_list, MOVE(from_sq, to_sq, piece.EMPTY, piece.EMPTY, 0), board)


def generate_all_moves(board, move_list):
    move_list.count = 0

    if board.side == WHITE:
        # for white pawns
        for pieceNum in range(board.num_pieces[piece.white_pawn]):
            sq = board.piece_list[piece.white_pawn][pieceNum]
            # for pawns just moving forward
            if board.pieces120[sq + 10] == piece.EMPTY:
                add_white_pawn_moves(move_list, sq, sq + 10, board)
                if sq in rank2 and board.pieces120[sq + 20] == piece.EMPTY:
                    add_quiet_moves(move_list, MOVE(sq, sq + 20, piece.EMPTY, piece.EMPTY, MVFLAGPS), board)

            # captures pawn
            if not is_sq_offboard(board, sq + 9) and piece_color[board.pieces120[sq + 9]] == BLACK:
                add_white_pawn_captures(move_list, sq, sq + 9, board.pieces120[sq + 9], board)
            if not is_sq_offboard(board, sq + 11) and piece_color[board.pieces120[sq + 11]] == BLACK:
                add_white_pawn_captures(move_list, sq, sq + 11, board.pieces120[sq + 11], board)

            # enpas
            if board.en_passant != NO_SQ:
                if (sq + 9) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq + 9, piece.EMPTY, piece.EMPTY, MVFLAGEP))
                if (sq + 11) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq + 11, piece.EMPTY, piece.EMPTY, MVFLAGEP))
        # castle
        if board.castle_rights & WKCA:
            if board.pieces120[f1] == piece.EMPTY and board.pieces120[g1] == piece.EMPTY:
                if not is_attacked(f1, BLACK, board) and not is_attacked(e1, BLACK, board):
                    add_quiet_moves(move_list, MOVE(e1, g1, piece.EMPTY, piece.EMPTY, MVFLAGCA), board)
        if board.castle_rights & WQCA:
            if board.pieces120[d1] == piece.EMPTY and board.pieces120[c1] == piece.EMPTY and \
                    board.pieces120[b1] == piece.EMPTY:
                if not is_attacked(d1, BLACK, board) and not is_attacked(e1, BLACK, board):
                    add_quiet_moves(move_list, MOVE(e1, c1, piece.EMPTY, piece.EMPTY, MVFLAGCA), board)
    elif board.side == BLACK:
        # for black pawns
        for pieceNum in range(board.num_pieces[piece.black_pawn]):
            sq = board.piece_list[piece.black_pawn][pieceNum]

            # for pawns just moving forward
            if board.pieces120[sq - 10] == piece.EMPTY:
                add_black_pawn_moves(move_list, sq, sq - 10, board)
                if sq in rank7 and board.pieces120[sq - 20] == piece.EMPTY:
                    add_quiet_moves(move_list, MOVE(sq, sq - 20, piece.EMPTY, piece.EMPTY, MVFLAGPS), board)

            # captures pawn
            if not is_sq_offboard(board, sq - 9) and piece_color[board.pieces120[sq - 9]] == WHITE:
                add_black_pawn_captures(move_list, sq, sq - 9, board.pieces120[sq - 9], board)
            if not is_sq_offboard(board, sq - 11) and piece_color[board.pieces120[sq - 11]] == WHITE:
                add_black_pawn_captures(move_list, sq, sq - 11, board.pieces120[sq - 11], board)

            # enpas
            if board.en_passant != NO_SQ:
                if (sq - 9) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq - 9, piece.EMPTY, piece.EMPTY, MVFLAGEP))
                if (sq - 11) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq - 11, piece.EMPTY, piece.EMPTY, MVFLAGEP))
        # castle
        if board.castle_rights & BKCA:
            if board.pieces120[f8] == piece.EMPTY and board.pieces120[g8] == piece.EMPTY:
                if not is_attacked(f8, WHITE, board) and not is_attacked(e8, WHITE, board):
                    add_quiet_moves(move_list, MOVE(e8, g8, piece.EMPTY, piece.EMPTY, MVFLAGCA), board)
        if board.castle_rights & BQCA:
            if board.pieces120[d8] == piece.EMPTY and board.pieces120[c8] == piece.EMPTY and \
                    board.pieces120[b8] == piece.EMPTY:
                if not is_attacked(d8, WHITE, board) and not is_attacked(e8, WHITE, board):
                    add_quiet_moves(move_list, MOVE(e8, c8, piece.EMPTY, piece.EMPTY, MVFLAGCA), board)

    # non slider pieces moves
    pce_index = LoopNonSlideIndex[board.side]
    pce = LoopNonSlidePiece[pce_index]
    pce_index += 1

    while pce != piece.EMPTY:
        for pieceNum in range(board.num_pieces[pce]):
            sq = board.piece_list[pce][pieceNum]

            for index in range(numDir[pce]):
                dir = pieceDir[pce][index]
                t_sq = sq + dir

                if is_sq_offboard(board, t_sq):
                    continue

                if board.pieces120[t_sq] != piece.EMPTY:
                    if piece_color[board.pieces120[t_sq]] == board.side ^ 1:
                        add_capture(move_list, MOVE(sq, t_sq, board.pieces120[t_sq], piece.EMPTY, 0), board)
                        # capture move
                    continue
                # not capture move
                add_quiet_moves(move_list, MOVE(sq, t_sq, piece.EMPTY, piece.EMPTY, 0), board)
        pce = LoopNonSlidePiece[pce_index]
        pce_index += 1

    # slider pieces
    pce_index = LoopSlideIndex[board.side]
    pce = LoopSlidePiece[pce_index]
    pce_index += 1
    while pce != piece.EMPTY:
        for pieceNum in range(board.num_pieces[pce]):
            sq = board.piece_list[pce][pieceNum]

            for index in range(numDir[pce]):
                dir = pieceDir[pce][index]
                t_sq = sq + dir

                while not is_sq_offboard(board, t_sq):
                    if board.pieces120[t_sq] != piece.EMPTY:
                        if piece_color[board.pieces120[t_sq]] == board.side ^ 1:
                            add_capture(move_list, MOVE(sq, t_sq, board.pieces120[t_sq], piece.EMPTY, 0), board)
                            # capture
                        break
                    # quiet move
                    add_quiet_moves(move_list, MOVE(sq, t_sq, piece.EMPTY, piece.EMPTY, 0), board)
                    t_sq += dir

        pce = LoopSlidePiece[pce_index]
        pce_index += 1


def generate_all_captures(board, move_list):
    move_list.count = 0

    if board.side == WHITE:
        # for white pawns
        for pieceNum in range(board.num_pieces[piece.white_pawn]):
            sq = board.piece_list[piece.white_pawn][pieceNum]

            # captures pawn
            if not is_sq_offboard(board, sq + 9) and piece_color[board.pieces120[sq + 9]] == BLACK:
                add_white_pawn_captures(move_list, sq, sq + 9, board.pieces120[sq + 9], board)
            if not is_sq_offboard(board, sq + 11) and piece_color[board.pieces120[sq + 11]] == BLACK:
                add_white_pawn_captures(move_list, sq, sq + 11, board.pieces120[sq + 11], board)

            # enpas
            if board.en_passant != NO_SQ:
                if (sq + 9) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq + 9, piece.EMPTY, piece.EMPTY, MVFLAGEP))
                if (sq + 11) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq + 11, piece.EMPTY, piece.EMPTY, MVFLAGEP))

    elif board.side == BLACK:
        # for black pawns
        for pieceNum in range(board.num_pieces[piece.black_pawn]):
            sq = board.piece_list[piece.black_pawn][pieceNum]

            # captures pawn
            if not is_sq_offboard(board, sq - 9) and piece_color[board.pieces120[sq - 9]] == WHITE:
                add_black_pawn_captures(move_list, sq, sq - 9, board.pieces120[sq - 9], board)
            if not is_sq_offboard(board, sq - 11) and piece_color[board.pieces120[sq - 11]] == WHITE:
                add_black_pawn_captures(move_list, sq, sq - 11, board.pieces120[sq - 11], board)

            # enpas
            if board.en_passant != NO_SQ:
                if (sq - 9) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq - 9, piece.EMPTY, piece.EMPTY, MVFLAGEP))
                if (sq - 11) == board.en_passant:
                    add_enpassant(move_list, MOVE(sq, sq - 11, piece.EMPTY, piece.EMPTY, MVFLAGEP))

    # non slider pieces moves
    pce_index = LoopNonSlideIndex[board.side]
    pce = LoopNonSlidePiece[pce_index]
    pce_index += 1

    while pce != piece.EMPTY:
        for pieceNum in range(board.num_pieces[pce]):
            sq = board.piece_list[pce][pieceNum]

            for index in range(numDir[pce]):
                dir = pieceDir[pce][index]
                t_sq = sq + dir

                if is_sq_offboard(board, t_sq):
                    continue

                if board.pieces120[t_sq] != piece.EMPTY:
                    if piece_color[board.pieces120[t_sq]] == board.side ^ 1:
                        add_capture(move_list, MOVE(sq, t_sq, board.pieces120[t_sq], piece.EMPTY, 0), board)
                        # capture move
                    continue
                # not capture move
        pce = LoopNonSlidePiece[pce_index]
        pce_index += 1

    # slider pieces
    pce_index = LoopSlideIndex[board.side]
    pce = LoopSlidePiece[pce_index]
    pce_index += 1
    while pce != piece.EMPTY:
        for pieceNum in range(board.num_pieces[pce]):
            sq = board.piece_list[pce][pieceNum]

            for index in range(numDir[pce]):
                dir = pieceDir[pce][index]
                t_sq = sq + dir

                while not is_sq_offboard(board, t_sq):
                    if board.pieces120[t_sq] != piece.EMPTY:
                        if piece_color[board.pieces120[t_sq]] == board.side ^ 1:
                            add_capture(move_list, MOVE(sq, t_sq, board.pieces120[t_sq], piece.EMPTY, 0), board)
                            # capture
                        break
                    # quiet move
                    # add_quiet_moves(movelist, MOVE(sq, t_sq, piece.EMPTY, piece.EMPTY, 0),board)
                    t_sq += dir

        pce = LoopSlidePiece[pce_index]
        pce_index += 1


def generate_all_legal(board):
    move_list = MoveList()
    generate_all_moves(board,move_list)
    lenss = move_list.count
    for i in range(lenss):
        if not make_move(board,move_list.moves[i].move):
            move_list.moves.remove(move_list.moves[i])
            move_list.count -=1
            continue

        undo_move(board)

    return move_list
