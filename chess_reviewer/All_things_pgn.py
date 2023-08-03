import chess.pgn
from Analyzer import accuracy_full_game

# def load_pgn(path):
#     pgn = open(path)
#     games = chess.pgn.read_game(pgn)
#
#     board = games.board()
#     fens_list = [board.fen()]
#     for move in games.mainline_moves():
#         board.push(move)
#         fens_list.append(board.fen())
#
#     return fens_list
#
# def get_accuracy_of_pgn(path,depth):
#     positions = load_pgn(path)
#     _,_,w,b = accuracy_full_game(positions,depth)
#     return w,b


if __name__=="__main__":
    game = chess.pgn.read_game(open("pgns/loaded_pgn.pgn", 'r'))