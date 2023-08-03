from Move_format import MoveList,FROMSQ,TOSQ,PROMOTED
from Move_gen import generate_all_moves
from Constants import piece,str_to_sq,WHITE,BLACK,sq_to_str

def parse_move(move, board):

    lists=MoveList()
    generate_all_moves(board,lists)

    black_pro_char={"q":piece.black_queen,"n":piece.black_knight,"b":piece.black_bishop,"r":piece.black_rook}
    white_pro_char = {"q": piece.white_queen, "n": piece.white_knight, "b": piece.white_bishop, "r": piece.white_rook}

    if len(move)==4:
        fr_sq = str_to_sq[move[0] + move[1]]
        t_sq = str_to_sq[move[2] + move[3]]

        for moveNum in range(lists.count):
            moves=lists.moves[moveNum].move
            # if(moves & MVFLAGPROM) != 0 and FROMSQ(moves)==fr_sq and TOSQ(moves)==t_sq:
            #     if PROMOTED(moves)==auto_promote:
            #         return moves
            if FROMSQ(moves)==fr_sq and TOSQ(moves)==t_sq:
                return moves

    #promotion
    if len(move)==5:
        fr_sq = str_to_sq[move[0] + move[1]]
        t_sq = str_to_sq[move[2] + move[3]]

        pro_char=move[4]
        promoted=None
        if board.side==WHITE:
            promoted=white_pro_char[pro_char]
        elif board.side==BLACK:
            promoted=black_pro_char[pro_char]

        for moveNum in range(lists.count):
            moves=lists.moves[moveNum].move
            if FROMSQ(moves)==fr_sq and TOSQ(moves)==t_sq:
                promo=PROMOTED(moves)
                if promo==promoted:
                    return moves

    return 0
def print_move(move,gs):
    from_sq=FROMSQ(move)
    to_sq=TOSQ(move)
    promote=""

    promote_to=PROMOTED(move)
    if gs.side==WHITE:
        if promote_to==piece.white_queen:
            promote="q"
        elif promote_to==piece.white_bishop:
            promote="b"
        elif promote_to==piece.white_knight:
            promote="n"
        elif promote_to==piece.white_rook:
            promote="r"
        else:
            promote=""

    elif gs.side==BLACK:
        if promote_to==piece.black_queen:
            promote="q"
        elif promote_to==piece.black_bishop:
            promote="b"
        elif promote_to==piece.black_knight:
            promote="n"
        elif promote_to==piece.black_rook:
            promote="r"
        else:
            promote=""

    print(sq_to_str[from_sq]+sq_to_str[to_sq]+promote,end="")
def str_move(move):

    if move is None:
        return "*"
    from_sq=FROMSQ(move)
    to_sq=TOSQ(move)

    promote_to=PROMOTED(move)
    if promote_to==piece.white_queen or promote_to==piece.black_queen:
        promote="q"
    elif promote_to==piece.white_bishop or promote_to==piece.black_bishop:
        promote="b"
    elif promote_to==piece.white_knight or promote_to==piece.black_knight:
        promote="n"
    elif promote_to==piece.white_rook or promote_to==piece.black_rook:
        promote="r"
    else:
        promote=""

    return sq_to_str[from_sq]+sq_to_str[to_sq]+promote


if __name__ == "__main__":
    print(str_move(76))