from Board import Board
from Move_gen import generate_all_moves
from Move_format import make_move,undo_move,MoveList
from Perft import perft_test_function
import time

def zobrist_test():
    print("\nZobrist testing...")
    test_passed=1
    num_pos=0
    moves_made=0
    #zobrist test
    board=Board()
    with open("perft_files/perft.txt", "r") as f:
        perft_lines = f.readlines()


    for i, position_fen in enumerate(perft_lines):
        fen = position_fen.split(";")[0]
        board.parse_fen(fen)

        move_list=MoveList()
        generate_all_moves(board,move_list)
        old_key = board.position_key

        for move_num in range(move_list.count):
            move=move_list.moves[move_num].move

            if not make_move(board,move):
                continue
            new_key=board.position_key
            moves_made+=1
            undo_move(board)
            if old_key != board.position_key:
                test_passed=0

            if not make_move(board, move):
                continue
            if new_key != board.position_key:
                test_passed=0
            undo_move(board)
        num_pos+=1

    print(f"zobrist test result:{test_passed}")
    print(f"num pos:{num_pos}")
    print(f"moves made:{moves_made}")
    print("Zobrist test finished\n\n")

def engine_test(d):
    zobrist_test()
    start=time.time()
    perft_test_function(d)
    elapsed=time.time()-start
    print(f"\nFinished all Engine test in {elapsed:.2f}s")

if __name__=="__main__":
    engine_test(2)