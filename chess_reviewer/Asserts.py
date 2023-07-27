from Constants import piece

def is_piece_king(pce):
    return pce==piece.white_king or pce==piece.black_king
def is_piece_knight(pce):
    return pce==piece.white_knight or pce==piece.black_knight
def is_piece_bishop(pce):
    return pce==piece.white_bishop or pce==piece.black_bishop
def is_piece_rook(pce):
    return pce==piece.white_rook or pce==piece.black_rook
def is_piece_pawn(pce):
    return pce==piece.white_pawn or pce==piece.black_pawn
def is_piece_queen(pce):
    return pce==piece.white_queen or pce==piece.black_queen
def is_pce_empty(pce):
    return pce==piece.EMPTY
def is_pce_offboard(pce):
    return pce==piece.OFF_BOARD
def is_piece_RQ(pce):
    return is_piece_rook(pce) or is_piece_queen(pce)
def is_piece_BQ(pce):
    return is_piece_bishop(pce) or is_piece_queen(pce)

