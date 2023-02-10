import math
from subprocess import Popen, PIPE, STDOUT

import numpy as np

from Board import Board
from Attacks import is_attacked
from Move_gen import MoveList,generate_all_moves
from Run_engine import draw_by_material,is_repetition
from Move_format import make_move,undo_move
from Constants import WHITE

def is_over(board_state):
    if board_state.fifty_move >= 100:
        return "1/2-1/2", "{Draw by Fifty Move Rule}"

    if is_repetition(board_state):
        return "1/2-1/2", "{Draw by Threefold Repetition}"

    if draw_by_material(board_state):
        return "1/2-1/2", "{Insufficient Material}"

    move_list = MoveList()
    generate_all_moves(board_state, move_list)
    legal = 0
    for move_num in range(move_list.count):
        if not make_move(board_state, move_list.moves[move_num].move):
            continue

        legal += 1
        undo_move(board_state)
        break

    in_check = is_attacked(board_state.kingSq[board_state.side], board_state.side ^ 1, board_state)
    if legal == 0:
        if in_check:
            if board_state.side == WHITE:
                return "0-1", "{Black win by Checkmate}"
            else:
                return "1-0", "{White win by Checkmate}"
        else:
            return "1/2-1/2", "{Stalemate}"
    return None

def get_harmonic_mean(num):
    average = 0
    for i in num:

        average+=(1/i)

    return len(num)/average
def win_rate(centipawns):
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * centipawns)) - 1)
def accuracy(win_before,win_after):
    return 103.1668 * math.exp(-0.04354 * (win_before - win_after)) - 3.1669
def get_eval(depth, pos,the_engine):
    
    board = Board()
    board.parse_fen(pos)
    with_move = None

    result = is_over(board)

    if result is not None:
        if result[0]=="1/2-1/2":
            return 0,""
        if result[0]=="1-0" and board.side!=WHITE:
            return -40000,""
        if result[0]=="0-1" and board.side==WHITE:
            return -40000,""

    
    score = 0
    input_one = f'position fen {pos}'.rstrip()
    command(the_engine, input_one)

    line = f"go depth {depth}".rstrip()
    command(the_engine, line)
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        if 'cp' in e_line:
            score = int(e_line.split(" ")[e_line.split(" ").index("cp")+1])
        elif 'mate' in e_line:
            mate_in = int(e_line.split(" ")[e_line.split(" ").index("mate")+1])
            if mate_in > 0:mul = 1
            elif mate_in < 0:mul = -1
            else:mul=1
            score = (40000 - abs(mate_in))*mul
        if 'bestmove' in e_line:
            with_move = e_line
            break
    return score,with_move.split(" ")[1]
def init_engine(the_engine):
    command(the_engine, 'uci')
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        if 'uciok' in e_line:
            break
    command(the_engine, 'ucinewgame')
    command(the_engine,'isready')
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        if 'readyok' in e_line:
            break
def command(p, commands):
    p.stdin.write(f'{commands}\n')
def accuracy_full_game(positions,depth):
    print(f"ANALYZING AT DEPTH {depth}...")
    _engine = "C:/Users/LENOVO/Desktop/someEngines/CE_PVSBRUTE.exe"
    print(f'using engine={_engine}')
    the_engine = Popen([_engine], stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=0, text=True)
    init_engine(the_engine)

    centipawns = []
    centipawns_black = []
    w_best_moves = []
    b_best_moves = []
    for i,pos in enumerate(positions):
        evaluated,best_move = get_eval(depth, pos, the_engine)
        colors = pos.split(" ")[1]

        if colors=="w":w_best_moves.append(best_move)
        else:b_best_moves.append(best_move)

        centipawns.append(evaluated if colors=="w" else -evaluated)
        centipawns_black.append(evaluated if colors=="b" else -evaluated)

        if ((i+1) % 2)==0:
            print(f"Analyzing... {(((i + 1) / len(positions)) * 100):.2f}%")

    win_rate_lists = [win_rate(i) for i in centipawns]
    win_rate_lists_black = [win_rate(i) for i in centipawns_black]

    accuracy_lists = []
    accuracy_lists_black = []
    all_accuracy = []
    for i in range(len(win_rate_lists)-1):
        if (i % 2)==0:accuracy_lists.append(accuracy(win_rate_lists[i], win_rate_lists[i + 1]))
        elif (i % 2) != 0:accuracy_lists_black.append(accuracy(win_rate_lists_black[i],win_rate_lists_black[i+1]))

    all_accuracy.append(accuracy_lists)
    all_accuracy.append(accuracy_lists_black)

    accuracy_lists = np.array(accuracy_lists)
    accuracy_lists_black = np.array(accuracy_lists_black)

    accuracy_lists = np.clip(accuracy_lists,10.0,500.0)
    accuracy_lists_black = np.clip(accuracy_lists_black, 10.0, 500.0)

    command(the_engine,'quit')
    return [w_best_moves,b_best_moves],all_accuracy,min(get_harmonic_mean(accuracy_lists),100.0),min(get_harmonic_mean(accuracy_lists_black),100.0)


if __name__=="__main__":


    print(accuracy(win_rate(10),win_rate(35)))
    print(accuracy(0,10))
    # print(accuracy(100,130))