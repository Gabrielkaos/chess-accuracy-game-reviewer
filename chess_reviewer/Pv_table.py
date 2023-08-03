import time

from Constants import IS_MATE
from Constants import NO_MOVE
from Move_format import MoveList,make_move,undo_move
from Move_gen import generate_all_moves,generate_all_legal
import numpy as np

class PVEntry:
    def __init__(self):
        self.depth=0
        self.score=0
        self.move=0
        self.flags=0
        self.position_key=None
class PVTable:
    def __init__(self):
        self.num_entries=0
        self.p_table=np.zeros(0)
    def __copy__(self):
        new = PVTable()
        new.p_table = self.p_table.copy()
        new.num_entries = self.num_entries
        return new


def move_exists(gs, move):
    move_list=MoveList()
    generate_all_moves(gs,move_list)

    for moveNum in range(move_list.count):
        move_in_loop=move_list.moves[moveNum].move

        if move_in_loop==move:
            return True

    return False
def move_really_exists(gs, move):
    move_list=MoveList()
    generate_all_moves(gs,move_list)

    for moveNum in range(move_list.count):
        move_in_loop=move_list.moves[moveNum].move

        if not make_move(gs,move_in_loop):
            continue

        undo_move(gs)

        if move_in_loop==move:
            return True

    return False
def get_pv_line(depth, gs):

    move=probe_move(gs)
    count=0

    while move != 0 and count<depth:
        if move_exists(gs, move):
            make_move(gs,move)
            gs.pv_array[count]=move
            count+=1
        else:
            break
        move = probe_move(gs)

    while gs.ply>0:
        undo_move(gs)

    return count
def clear_table(table):
    for pv_entry in table.p_table:
        pv_entry.depth=0
        pv_entry.move=NO_MOVE
        pv_entry.score=0
        pv_entry.flags=0
        pv_entry.position_key=None
def init_pv_table(table, num):
    table.num_entries=num
    start = time.time()
    print(f"Initializing PV Table with {num} entries...")
    table.p_table=np.array([PVEntry() for _ in range(int(table.num_entries))])
    clear_table(table)
    print(f"Initialized with {int(table.num_entries)} entries in {(time.time()-start):.2f}s\n")
def probe_move(board):
    index= board.position_key % board.pv_table.num_entries
    index = int(index)

    if board.pv_table.p_table[index].position_key == board.position_key:
        return board.pv_table.p_table[index].move

    return NO_MOVE
def store_hash_entry(board, move, score, flags, depth):
    index= board.position_key % board.pv_table.num_entries
    index = int(index)

    if score > IS_MATE:score+=board.ply
    elif score < -IS_MATE:score-=board.ply

    board.pv_table.p_table[index].position_key=board.position_key
    board.pv_table.p_table[index].move = move
    board.pv_table.p_table[index].score = score
    board.pv_table.p_table[index].flags = flags
    board.pv_table.p_table[index].depth = depth
def score_from_pv(score,ply):
    if score > IS_MATE:score -= ply
    elif score < -IS_MATE:score += ply
    return score
def probe_hash_entry(board,pv_info:PVEntry):
    index = board.position_key % board.pv_table.num_entries
    index=int(index)

    if board.pv_table.p_table[index].position_key==board.position_key:
        pv_info.flags = board.pv_table.p_table[index].flags
        pv_info.move = board.pv_table.p_table[index].move
        pv_info.score = board.pv_table.p_table[index].score
        pv_info.depth = board.pv_table.p_table[index].depth
        return True

    return False