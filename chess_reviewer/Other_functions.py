from Constants import piece

def FR_to_SQ(file,rank):
    return (21 + file) + (rank * 10)


def get_game_phase(gs):
    game_phase = 24

    game_phase -= gs.num_pieces[piece.white_knight]
    game_phase -= gs.num_pieces[piece.black_knight]
    game_phase -= gs.num_pieces[piece.white_bishop]
    game_phase -= gs.num_pieces[piece.black_bishop]

    game_phase -= gs.num_pieces[piece.white_rook] * 2
    game_phase -= gs.num_pieces[piece.black_rook] * 2
    game_phase -= gs.num_pieces[piece.white_queen] * 4
    game_phase -= gs.num_pieces[piece.black_queen] * 4

    return (game_phase * 256 + 12) / 24