import numpy as np
from Constants import MAX_DEPTH, BOARD_NUM_SQ, INFINITE, NO_MOVE, HF_ALPHA, HF_EXACT, HF_BETA, IS_MATE, piece_value, \
    piece,END_PHASE
from Pv_table import get_pv_line, probe_hash_entry, store_hash_entry,PVEntry,score_from_pv
from Evaluate import eval_position,draw_by_material
from Attacks import is_attacked
from Move_format import make_move, undo_move, MoveList, CAPTURED, FROMSQ, TOSQ, make_null_move, take_null_move, PROMOTED
from Move_gen import generate_all_moves, generate_all_captures
from I_o import print_move
import time

aspiration_windows=50
futility_margin = np.array([0, 100, 300, 500])

###########################################################################
#                           SEARCH THINGS INFO                            #
###########################################################################
# Aspiration Windows
# Check Extension
# Transposition Tables
# Evaluation Pruning
# Null Move Pruning
# Razoring
# IIR
# Futility Pruning
# LMR
# PVS
# Delta Pruning in QSearch
# QSearch
###########################################################################

class SearchInfo:
    def __init__(self):
        self.all_time = 0
        self.time_set = 0
        self.start_time = 0

        self.depth = 0
        self.stopped = 0
        self.nodes = 0
        # self.fhf = 0
        # self.fh = 0

        self.post = False

def should_we_stop(info):
    if info.time_set and (time.time() - info.start_time) > info.all_time:
        info.stopped = True
def repetition(board):
    index = board.his_ply - board.fifty_move

    while index < board.his_ply - 1:
        if board.position_key == board.history[index].position_key:
            return True
        index += 1
    return False
def init_for_search(board, info):
    for index in range(2):
        for index2 in range(MAX_DEPTH):
            board.search_killers[index][index2] = 0

    for index in range(13):
        for index2 in range(BOARD_NUM_SQ):
            board.search_history[index][index2] = 0

    board.ply = 0
    board.pv_table.hit = 0
    board.pv_table.cut = 0
    board.pv_table.over_write = 0
    info.nodes = 0
    # info.fhf = 0
    # info.fh = 0
    info.stopped = False
    info.start_time = time.time()
def order_moves(move_num, move_list):
    # bubble sort
    index = move_num
    best_num = move_num
    best_score = 0

    while index < move_list.count:
        if move_list.moves[index].score > best_score:
            best_score = move_list.moves[index].score
            best_num = index
        index += 1

    temp_score = move_list.moves[move_num].score
    temp_move = move_list.moves[move_num].move
    move_list.moves[move_num].score = move_list.moves[best_num].score
    move_list.moves[move_num].move = move_list.moves[best_num].move
    move_list.moves[best_num].score = temp_score
    move_list.moves[best_num].move = temp_move

def alpha_beta(board, depth, alpha, beta, info, do_null):
    pv_node = (beta - alpha) > 1
    root_node=pv_node and board.ply==0

    #horizon check
    if depth <= 0: return quiescence(board, alpha, beta, info)

    #should we stop
    if (info.nodes & 2047) == 0: should_we_stop(info)
    info.nodes += 1

    # see if draw or near maxdepth
    if not root_node:
        if repetition(board) or board.fifty_move >= 100 or draw_by_material(board): return 0
        if board.ply > MAX_DEPTH - 1: return eval_position(board)

    #check extension
    in_check,_ = is_attacked(board.kingSq[board.side], board.side ^ 1, board)
    if in_check: depth += 1

    ####################################
    f_prune = False
    ####################################

    # probe transposition table
    pv_info = PVEntry()
    is_hit = probe_hash_entry(board,pv_info)
    if is_hit:
        pv_info.score = score_from_pv(pv_info.score,board.ply)
        if pv_info.depth>=depth and (depth==0 or not pv_node):
            if pv_info.flags==HF_EXACT or \
                    (pv_info.flags==HF_ALPHA and pv_info.score<=alpha) or \
                    (pv_info.flags==HF_BETA and pv_info.score>=beta):
                return pv_info.score
    pv_move = pv_info.move

    if not in_check and not pv_node:
        static_eval = eval_position(board)

        #evaluation pruning
        if depth < 3 and (abs(beta - 1) > (-INFINITE + 100)):
            eval_margin = piece_value[piece.white_pawn] * depth
            if (static_eval - eval_margin) >= beta:
                return static_eval - eval_margin

        if do_null:
            #null move pruning
            if board.big_piece[board.side] > 1 and depth >= 4 and board.ply != 0:
                make_null_move(board)
                null_value = -alpha_beta(board, depth - 4, -beta, -beta + 1, info, False)
                take_null_move(board)
                if info.stopped:
                    return 0

                if null_value >= beta and abs(null_value) < IS_MATE:
                    return beta

            #razoring
            razor_score = static_eval + piece_value[piece.white_pawn]
            if razor_score < beta:
                if depth == 1:
                    new_score = quiescence(board, alpha, beta, info)
                    if new_score > razor_score:
                        return new_score
                    else:
                        return razor_score

            razor_score += piece_value[piece.white_pawn]
            if razor_score < beta and depth < 4:
                new_score = quiescence(board, alpha, beta, info)
                if new_score < beta:
                    if new_score > razor_score:
                        return new_score
                    else:
                        return razor_score

        #futility pruning
        if depth < 4 and abs(alpha) < (INFINITE - 1000) and (static_eval + futility_margin[depth]) <= alpha:
            f_prune = True

    #IIR
    if depth >= 5 and pv_move == NO_MOVE:
        depth -= 1

    move_list = MoveList()
    generate_all_moves(board, move_list)
    legal = 0
    moves_searched = 0
    old_alpha = alpha
    best_move = NO_MOVE
    best_score = -INFINITE

    if pv_move != NO_MOVE:
        for move_num in range(move_list.count):
            if move_list.moves[move_num].move == pv_move:
                move_list.moves[move_num].score = 2000000
                break

    for move_num in range(move_list.count):
        order_moves(move_num, move_list)
        move = move_list.moves[move_num].move

        if not make_move(board, move):
            continue
        legal += 1

        #futility pruning
        if f_prune and moves_searched != 0 and CAPTURED(move) == 0 and PROMOTED(move) == 0 and \
                (not is_attacked(board.kingSq[board.side], board.side ^ 1, board)[0]):
            undo_move(board)
            continue

        # LMR
        if moves_searched == 0:
            score = -alpha_beta(board, depth - 1, -beta, -alpha, info, True)
        else:
            if not in_check and not pv_node and CAPTURED(move) == 0 and PROMOTED(move) == 0 and \
                    moves_searched >= 4 and depth >= 3 and \
                    (FROMSQ(move) != FROMSQ(board.search_killers[0][board.ply]) or TOSQ(move) != TOSQ(
                        board.search_killers[0][board.ply])) and \
                    (FROMSQ(move) != FROMSQ(board.search_killers[1][board.ply]) or TOSQ(move) != TOSQ(
                        board.search_killers[1][board.ply])):
                r = 1
                if moves_searched > 6: r += 1
                score = -alpha_beta(board, depth - r, -alpha - 1, -alpha, info, True)
            else:
                score = alpha + 1

            #PVS
            if score > alpha:
                score = -alpha_beta(board, depth - 1, -alpha - 1, -alpha, info, True)
                if alpha < score < beta:
                    score = -alpha_beta(board, depth - 1, -beta, -alpha, info, True)

        undo_move(board)
        moves_searched += 1

        if info.stopped:
            return 0

        if score > best_score:
            best_score = score
            best_move = move

            if score > alpha:
                if score >= beta:
                    # if legal == 1: info.fhf += 1
                    # info.fh += 1

                    if CAPTURED(move) == 0:
                        board.search_killers[1][board.ply] = board.search_killers[0][board.ply]
                        board.search_killers[0][board.ply] = move

                    store_hash_entry(board, best_move, beta, HF_BETA, depth)

                    return beta
                alpha = score

                if CAPTURED(move) == 0:
                    board.search_history[board.pieces120[FROMSQ(best_move)]][TOSQ(move)] += depth

    if legal == 0:
        if in_check:
            return -INFINITE + board.ply
        else:
            return 0

    if alpha != old_alpha:
        store_hash_entry(board, best_move, best_score, HF_EXACT, depth)
    else:
        store_hash_entry(board, best_move, alpha, HF_ALPHA, depth)

    return alpha
def quiescence(board, alpha, beta, info):
    if (info.nodes & 2047) == 0: should_we_stop(info)
    info.nodes += 1

    #draw or near maxdepth
    if (repetition(board) or board.fifty_move >= 100) and board.ply != 0: return 0
    if board.ply > MAX_DEPTH - 1: return eval_position(board)

    #stand pat
    score = eval_position(board)
    stand_pat = score
    if score >= beta: return beta
    if score > alpha: alpha = score

    move_list = MoveList()
    generate_all_captures(board, move_list)
    legal = 0
    for move_num in range(move_list.count):
        order_moves(move_num, move_list)
        move = move_list.moves[move_num].move

        #delta pruning
        if stand_pat + 200 + piece_value[CAPTURED(move)] < alpha and PROMOTED(move) == 0 and \
                board.game_phase<END_PHASE:
            continue

        if not make_move(board, move):
            continue
        legal += 1

        score = -quiescence(board, -beta, -alpha, info)
        undo_move(board)

        if info.stopped:
            return 0

        if score > alpha:
            if score >= beta:
                return beta
            alpha = score

    return alpha
def iterative_deepening(board, info):
    init_for_search(board, info)

    best_move = NO_MOVE
    alpha=-INFINITE
    beta=INFINITE

    # loop
    curr_depth = 1
    while curr_depth <= MAX_DEPTH:
        best_score = alpha_beta(board, curr_depth, alpha, beta, info, True)

        if info.stopped:
            break

        pv_moves = get_pv_line(curr_depth, board)
        best_move = board.pv_array[0]

        ############################################
        #           ASPIRATION WINDOWS             #
        ############################################
        if best_score <= alpha or best_score>=beta:
            alpha=-INFINITE
            beta=INFINITE
            continue
        alpha=best_score-aspiration_windows
        beta=best_score+aspiration_windows
        ############################################

        if info.post:
            print(f"depth:{curr_depth}, score:{best_score}, nodes:{info.nodes}, pv:", end="")
            for index in range(pv_moves):
                print_move(board.pv_array[index], board)
                print(" ", end="")
            print()
        if (abs(best_score) == INFINITE - 1) and best_move != NO_MOVE:
            break

        if not info.time_set and curr_depth>=info.depth:
            break
        curr_depth += 1

    print(f"best move: ", end="")
    print_move(best_move, board)
    print()
    return best_move
