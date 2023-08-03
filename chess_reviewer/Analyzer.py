import math
from subprocess import Popen, PIPE, STDOUT
import numpy as np
from Board import Board
from Attacks import is_attacked
from Move_gen import MoveList, generate_all_moves
from Run_engine import draw_by_material, is_repetition
from Move_format import make_move, undo_move
from Constants import WHITE


def get_hashes():
    # get the booklines
    with open("hashed_positions/hashed_positions.txt", "r") as f:
        booklines = f.readlines()
    # clean the data
    hashes = []
    for i in booklines:
        pos = i.split(",")[0]
        depth = i.split(",")[1]
        evaluated = i.split(",")[2]
        best_move = i.split(",")[3]
        real_eval = i.split(",")[4]
        hashes.append((pos, depth, evaluated, best_move, real_eval))
    ###################################################
    return hashes


def find_pos_in_hashes(pos, depth, hashes):
    for h in hashes:
        # if matching fen
        if h[0] == pos:
            # if matching depth
            if int(h[1]) == depth:
                return int(h[2]), h[3], h[4]

    return None, None, None


def save_to_data(pos, depth, evaluated, best_move, real_eval):
    with open("hashed_positions/hashed_positions.txt", "a") as f:
        f.writelines(f"{pos},{depth},{evaluated},{best_move},{real_eval}\n")


def game_phase_cap(board_state):
    if board_state.game_phase < 43:
        phase = "opening"
    elif 43 <= board_state.game_phase < 171:
        phase = "middle game"
    else:
        phase = "endgame"

    return phase


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

    in_check,_ = is_attacked(board_state.kingSq[board_state.side], board_state.side ^ 1, board_state)
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

    if len(num)==0:return 0.00

    for i in num:

        average += (1 / i)

    return len(num)/ average


def win_rate(centipawns):
    return 50 + 50 * (2 / (1 + math.exp(-0.00368208 * centipawns)) - 1)


def accuracy(win_before, win_after):
    return 103.1668 * math.exp(-0.04354 * (win_before - win_after)) - 3.1669


def get_eval(pos, the_engine, depth_limit):
    board = Board()
    board.parse_fen(pos)
    with_move = None
    real_eval = "M0"
    latest_depth = 1

    result = is_over(board)

    if result is not None:
        if result[0] == "1/2-1/2":
            return 0, "", real_eval, latest_depth
        if result[0] == "1-0" and board.side != WHITE:
            return -40000, "", real_eval, latest_depth
        if result[0] == "0-1" and board.side == WHITE:
            return -40000, "", real_eval, latest_depth

    score = 0
    input_one = f'position fen {pos}'.rstrip()
    command(the_engine, input_one)

    line = f"go depth {depth_limit}".rstrip()
    command(the_engine, line)
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        # print(e_line)
        if 'cp' in e_line:
            score = int(e_line.split(" ")[e_line.split(" ").index("cp") + 1])
            colors = pos.split(" ")[1]
            real_eval = f"{-score if colors == 'b' else score}"
        elif 'mate' in e_line:
            mate_in = int(e_line.split(" ")[e_line.split(" ").index("mate") + 1])
            if mate_in > 0:
                mul = 1
            elif mate_in < 0:
                mul = -1
            else:
                mul = 1
            score = (40000 - abs(mate_in)) * mul
            colors = pos.split(" ")[1]
            real_eval = f"M{-mate_in if colors == 'b' else mate_in}"
        if 'depth' in e_line and 'currmove' not in e_line:
            latest_depth = int(e_line.split(" ")[e_line.split(" ").index("depth") + 1])
        if 'bestmove' in e_line:
            with_move = e_line
            break
    return score, with_move.split(" ")[1], real_eval, latest_depth


def init_engine(the_engine):
    command(the_engine, 'uci')
    command(the_engine, 'ucinewgame')
    command(the_engine, 'isready')
    command(the_engine,'')


def command(p, commands):
    p.stdin.write(f'{commands}\n')


def count_book_moves(moves):

    with open('books/book.txt','r') as f:
        book_lines = f.readlines()


    not_reversed_moves = []
    for i in range(len(moves) - 1, -1, -1):
        not_reversed_moves.append(moves[i])

    longest_book_lines = []
    lines_length = []
    for line in book_lines:
        real_line = line.split(" ")
        longest_line = 0
        book_moves = []

        if len(real_line)>len(not_reversed_moves):continue

        for i in range(len(real_line)):
            try:
                if str(not_reversed_moves[i])==str(real_line[i]):
                    book_moves.append(not_reversed_moves[i])
                    longest_line+=1
                else:
                    longest_book_lines.append(book_moves)
                    lines_length.append(longest_line)
                    break
            except IndexError:
                lines_length.append(longest_line)
                longest_book_lines.append(book_moves)
                break

    longest_length = 0
    best_books = 0
    for i,value in enumerate(longest_book_lines):
        if len(value)>longest_length:
            longest_length = len(value)
            best_books = i


    longest = 0
    for i in lines_length:
        if i>longest:longest = i
    return longest,longest_book_lines[best_books]



def accuracy_full_game(positions, analysis_depth,reversed_move_list):
    print(f"ANALYZING EACH MOVE TO DEPTH {analysis_depth} ...")
    _engine = "engines/stockfish_v16.exe"
    print(f'using engine={_engine}\n')

    # open the two engines each for each color
    the_engine = Popen([_engine], stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=0, text=True)
    the_engine2 = Popen([_engine], stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=0, text=True)

    # initialize
    init_engine(the_engine)
    init_engine(the_engine2)

    # variables
    already_went_endgame = False
    centipawns = []
    centipawns_black = []
    centipawns_mid_game = []
    centipawns_black_mid_game = []
    centipawns_end_game = []
    centipawns_black_end_game = []
    w_best_moves = []
    b_best_moves = []
    white_e = []
    black_e = []
    accuracy_lists_mid = []
    accuracy_lists_black_mid = []
    accuracy_lists_end = []
    accuracy_lists_black_end = []
    accuracy_lists = []
    accuracy_lists_black = []
    all_accuracy = []
    board_state = Board()
    # hashes = get_hashes()

    fen_with_moves = []

    # loop through all the seen positions in the whole game
    for i, pos in enumerate(positions):

        # was_found = find_pos_in_hashes(pos, analysis_depth, hashes)

        board_state.parse_fen(pos)
        colors = pos.split(" ")[1]

        # # get the evaluation, and best move
        # if was_found[0] is None:
        #     if colors=="w":evaluated, best_move, real_eval, _ = get_eval(pos, the_engine, analysis_depth)
        #     else:evaluated, best_move, real_eval, _ = get_eval(pos, the_engine2, analysis_depth)
        #
        #     # save to data if new
        #     # if board_state.game_phase < 86: save_to_data(pos, analysis_depth, evaluated, best_move, real_eval)
        #     save_to_data(pos, analysis_depth, evaluated, best_move, real_eval)
        # else:
        #     evaluated, best_move, real_eval = was_found
        if colors == "w":
            evaluated, best_move, real_eval, _ = get_eval(pos, the_engine, analysis_depth)
            fen_with_moves.append((pos,best_move))
        else:
            evaluated, best_move, real_eval, _ = get_eval(pos, the_engine2, analysis_depth)
            fen_with_moves.append((pos, best_move))

        # append the best move, and evaluation
        if colors == "w":
            if i != 0: black_e.append(real_eval)
            w_best_moves.append(best_move)
        else:
            white_e.append(real_eval)
            b_best_moves.append(best_move)

        centipawns.append(evaluated if colors == "w" else -evaluated)
        centipawns_black.append(evaluated if colors == "b" else -evaluated)

        # separate evaluation list for middle game and end game
        if game_phase_cap(board_state) != "endgame" and not already_went_endgame:
            centipawns_mid_game.append(evaluated if colors == "w" else -evaluated)
            centipawns_black_mid_game.append(evaluated if colors == "b" else -evaluated)
        else:
            if not already_went_endgame: already_went_endgame = True
            centipawns_end_game.append(evaluated if colors == "w" else -evaluated)
            centipawns_black_end_game.append(evaluated if colors == "b" else -evaluated)

        if not is_over(board_state):
            # if was_found[0] is None:
            #     print(
            #             f"Analyzed {'white' if colors == 'w' else 'black'} move {int(1 + (i - (1 if colors == 'b' else 0)) / 2)} and saved")
            # else:
            #     print(f"Probed hashed position, move {int(1 + (i - (1 if colors == 'b' else 0)) / 2)}")
            print(
                f"Analyzed {'white' if colors == 'w' else 'black'} move {int(1 + (i - (1 if colors == 'b' else 0)) / 2)}")

    # initialize the win rate lists
    win_rate_lists = [win_rate(i) for i in centipawns]
    win_rate_lists_black = [win_rate(i) for i in centipawns_black]

    # initialize the win rate lists each for each game phase
    win_rate_lists_mid = [win_rate(i) for i in centipawns_mid_game]
    win_rate_lists_black_mid = [win_rate(i) for i in centipawns_black_mid_game]
    win_rate_lists_end = [win_rate(i) for i in centipawns_end_game]
    win_rate_lists_black_end = [win_rate(i) for i in centipawns_black_end_game]

    # get the accuracy based on the win rates
    for i in range(len(win_rate_lists_mid) - 1):
        if (i % 2) == 0:
            accuracy_lists_mid.append(max(accuracy(win_rate_lists_mid[i], win_rate_lists_mid[i + 1]),10.00))
        elif (i % 2) != 0:
            accuracy_lists_black_mid.append(max(accuracy(win_rate_lists_black_mid[i], win_rate_lists_black_mid[i + 1]),10.00))
    for i in range(len(win_rate_lists_end) - 1):
        if (i % 2) == 0:
            accuracy_lists_end.append(max(accuracy(win_rate_lists_end[i], win_rate_lists_end[i + 1]),10.00))
        elif (i % 2) != 0:
            accuracy_lists_black_end.append(max(accuracy(win_rate_lists_black_end[i], win_rate_lists_black_end[i + 1]),10.00))
    for i in range(len(win_rate_lists) - 1):
        if (i % 2) == 0:
            accuracy_lists.append(max(accuracy(win_rate_lists[i], win_rate_lists[i + 1]),10.00))
        elif (i % 2) != 0:
            accuracy_lists_black.append(max(accuracy(win_rate_lists_black[i], win_rate_lists_black[i + 1]),10.00))

    # book_moves
    longest_book,_ = count_book_moves(reversed_move_list)
    for i in range(longest_book):
        if (i % 2) == 0:
            accuracy_lists[i] = 100.00

            if i > (len(accuracy_lists_mid) - 1):
                accuracy_lists_end[i] = 100.00
            else:
                accuracy_lists_mid[i] = 100.00

        else:
            accuracy_lists_black[i] = 100.00

            if i > (len(accuracy_lists_black_mid) - 1):
                accuracy_lists_black_end[i] = 100.00
            else:
                accuracy_lists_black_mid[i] = 100.00

    all_accuracy.append(accuracy_lists)
    all_accuracy.append(accuracy_lists_black)
    accuracy_lists = np.array(accuracy_lists)
    accuracy_lists_black = np.array(accuracy_lists_black)
    accuracy_lists = np.clip(accuracy_lists, 10.0, 500.0)
    accuracy_lists_black = np.clip(accuracy_lists_black, 10.0, 500.0)


    command(the_engine, 'quit')
    command(the_engine2, 'quit')
    eval_list = [white_e, black_e]
    # print(accuracy_lists_mid)
    # print(min(get_harmonic_mean(accuracy_lists_mid), 100.0))
    return fen_with_moves,[min(get_harmonic_mean(accuracy_lists_mid), 100.0), min(get_harmonic_mean(accuracy_lists_end), 100.0),
            min(get_harmonic_mean(accuracy_lists_black_mid), 100.0),
            min(get_harmonic_mean(accuracy_lists_black_end), 100.0)], eval_list, [w_best_moves,
                                                                                  b_best_moves], all_accuracy, min(
        get_harmonic_mean(accuracy_lists), 100.0), min(get_harmonic_mean(accuracy_lists_black), 100.0)


if __name__ == "__main__":
    print(accuracy(win_rate(900),win_rate(0)))
