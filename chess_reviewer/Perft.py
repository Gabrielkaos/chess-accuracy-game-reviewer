from Move_gen import generate_all_moves
from Move_format import MoveList,make_move,undo_move
from Board import Board

global LEAF_NODES

def move_generation_test(gs, depth):
    global LEAF_NODES
    if depth==0:
        LEAF_NODES+=1
        return
    lists=MoveList()
    generate_all_moves(gs,lists)
    for moveNum in range(lists.count):
        if not (make_move(gs,lists.moves[moveNum].move)):
            continue
        move_generation_test(gs, depth - 1)
        undo_move(gs)

    return
def perft_test(gs, depth):
    global LEAF_NODES

    LEAF_NODES=0
    lists=MoveList()
    generate_all_moves(gs,lists)
    no_of_moves=0

    for moveNum in range(lists.count):
        move=lists.moves[moveNum].move
        if not (make_move(gs,move)):
            continue

        no_of_moves+=1
        move_generation_test(gs, depth - 1)
        undo_move(gs)

    return LEAF_NODES
def perft_test_function(depth):
    print("\nPerft test starting...")
    board = Board()

    with open("perft_files/perft.txt", "r") as f:
        perft_lines = f.readlines()

    correct_nodes = []
    # extract node information based on depth
    for line in perft_lines:
        nodes = line.split(";")[depth]
        correct_nodes.append(nodes.split(f"D{depth} ")[1])

    nodes_searched = []
    for i, position_fen in enumerate(perft_lines):
        fen = position_fen.split(";")[0]
        board.parse_fen(fen)
        leaf_nodes = perft_test(board, depth)
        print(f"Position:{i + 1}, depth:{depth}, nodes:{leaf_nodes}")
        nodes_searched.append(leaf_nodes)

    if len(correct_nodes) == len(nodes_searched):
        for i in range(len(correct_nodes)):
            if int(correct_nodes[i]) != int(nodes_searched[i]):
                print(f"Wtf in line:{i + 1} cor_node = {correct_nodes[i]} while node_searched = {nodes_searched[i]}")
                break
        print(f"Test Passed at depth {depth}")
    else:
        print(f"Wtf length of cor_nodes:{len(correct_nodes)} while searched_nodes:{len(nodes_searched)}")
    print("Perft test finished\n\n")