from Search import iterative_deepening, SearchInfo
from Board import Board
from Pv_table import init_pv_table, clear_table, move_exists
from Constants import MAX_DEPTH, BOTH, WHITE
from I_o import parse_move
from Engine_tests import engine_test
from Move_format import make_move, undo_move, MoveList
from Move_gen import generate_all_moves
from Attacks import is_attacked
from Evaluate import draw_by_material
from Perft import perft_test


def is_repetition(board):
    r = 0
    for index in range(board.his_ply):
        if board.history[index].position_key == board.position_key:
            r += 1

    if r >= 2:
        return True
    return False
def is_game_over(board):
    if board.fifty_move >= 100:
        print("fifty move rule exceeded")
        return True

    if is_repetition(board):
        print("threefold repetition")
        return True

    if draw_by_material(board):
        print("draw material")
        return True

    move_list = MoveList()
    generate_all_moves(board, move_list)
    legal = 0
    for move_num in range(move_list.count):
        if not make_move(board, move_list.moves[move_num].move):
            continue

        legal += 1
        undo_move(board)
        break

    in_check,_ = is_attacked(board.kingSq[board.side], board.side ^ 1, board)
    if legal == 0:
        if in_check:
            if board.side == WHITE:
                print("black mates white")
            else:
                print("white mates black")
        else:
            print("stalemate")
        return True
    return False
def print_help():
    print("go - let engine think")
    print("fen x - set board fen to x")
    print("depth x - set depth to x")
    print("time x - set time to x")
    print("perft x - test position to depth x")
    print("undo - undo a move")
    print("view - view settings")
    print("print - print board")
    print("off - engine will not think")
    print("new - new game")
    print("clear - clear transposition tables")
    print("enginetest - test the engine for bugs")
    print("quit - exit engine")
    print("for a move type in algebraic notation eg. e2e4, e7e8q(promote)")

def cli(num_entries=2_000_000):
    board = Board()
    init_pv_table(board.pv_table, num_entries)
    info = SearchInfo()

    max_time = 1000
    time = 5
    depth = 10
    side = BOTH
    info.post = True
    print("Type 'help' for commands")
    while True:
        board.ply = 0
        if side == board.side and not is_game_over(board):
            info.all_time = time
            info.depth = depth

            if time >= 1:info.time_set = True
            else: info.time_set = False

            move = iterative_deepening(board, info)
            make_move(board,move)

        input_line = input(">")
        if input_line.lower() == "help":
            print_help()
            continue
        if input_line.lower() == "go":
            side = board.side
            continue
        if input_line.lower().startswith("fen"):
            try:
                fen = input_line.split("fen")[1][1:]
                board.parse_fen(fen)
                board.print_board()
            except IndexError:
                print("invalid")
            continue
        if input_line.lower().startswith("depth"):
            try:
                depth = int(input_line.split(" ")[1])

                if depth < 1: depth = MAX_DEPTH
                if depth > MAX_DEPTH: depth = MAX_DEPTH
            except IndexError:
                depth = 10
            continue
        if input_line.lower().startswith("time"):
            try:
                time = int(input_line.split(" ")[1])

                if time > max_time: time = max_time
            except IndexError:
                time = 5
            continue
        if input_line.lower() == "undo":
            if board.his_ply != 0:
                board.ply = 0
                side = BOTH
                undo_move(board)
                board.print_board()
            continue
        if input_line.lower() == "view":
            print(f"time {time}\ndepth {depth}\nside {side}")
            continue
        if input_line.lower() == "print":
            board.print_board()
            continue
        if input_line.lower() == "off":
            side = BOTH
            continue
        if input_line.lower() == "new":
            board = Board()
            init_pv_table(board.pv_table, num_entries)
            side = BOTH
            continue
        if input_line.lower().startswith("perft"):
            try:
                p_depth = input_line.split(" ")[1]
            except IndexError:
                p_depth = 2
            print(perft_test(board, p_depth))
            continue
        if input_line.lower() == "clear":
            clear_table(board.pv_table)
            continue
        if input_line.lower() == "enginetest":
            engine_test(3)
            continue
        if input_line.lower() == "quit": break

        try:
            move = parse_move(input_line, board)
            if move_exists(board, move):
                make_move(board, move)
                board.print_board()
            else:
                print("invalid command:" + input_line)
        except KeyError:
            print("invalid command:" + input_line)


if __name__ == "__main__":
    cli()
