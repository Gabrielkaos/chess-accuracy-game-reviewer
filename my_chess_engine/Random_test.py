import chess
import chess.pgn
import numpy as np

board = chess.pgn.read_game(open("pgns/saved_pgn.pgn","r"))
print(board.headers["Site"])
print(board.headers["Site"].removeprefix("'").removesuffix("'"))
for node in board.mainline():
    print(f"{str(node.move)},{node.comment}")
