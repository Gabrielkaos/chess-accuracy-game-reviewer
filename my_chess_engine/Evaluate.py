from Constants import WHITE, BLACK
from Constants import piece
from Constants import sq120_to_sq64
from Eval_weights import *

mirror64 = np.array([
    56, 57, 58, 59, 60, 61, 62, 63,
    48, 49, 50, 51, 52, 53, 54, 55,
    40, 41, 42, 43, 44, 45, 46, 47,
    32, 33, 34, 35, 36, 37, 38, 39,
    24, 25, 26, 27, 28, 29, 30, 31,
    16, 17, 18, 19, 20, 21, 22, 23,
    8, 9, 10, 11, 12, 13, 14, 15,
    0, 1, 2, 3, 4, 5, 6, 7
])

def draw_by_material(board):
    if board.num_pieces[piece.white_pawn] != 0 or \
            board.num_pieces[piece.black_pawn] != 0 or \
            board.num_pieces[piece.white_rook] != 0 or \
            board.num_pieces[piece.black_rook] != 0 or \
            board.num_pieces[piece.white_queen] != 0 or \
            board.num_pieces[piece.black_queen] != 0 or \
            board.num_pieces[piece.white_bishop] > 1 or \
            board.num_pieces[piece.black_bishop] > 1 or \
            board.num_pieces[piece.white_knight] > 2 or \
            board.num_pieces[piece.black_knight] > 2: return False
    return True

def game_phase_scale(opening, ending, phase):
    return ((opening * (256 - phase)) + (ending * phase)) / 256

def adjust_opening_score(board, score):
    adjusted_score = score
    fifty = board.fifty_move

    if fifty > 20: adjusted_score = (120 - fifty) * adjusted_score / 100

    return adjusted_score

def adjust_ending_score(board, score):
    adjusted_score = score
    fifty = board.fifty_move

    if fifty > 20: adjusted_score = (120 - fifty) * adjusted_score / 100

    return adjusted_score

def evaluate_pawns(board):
    score_white_opening = score_white_ending = 0
    score_black_opening = score_black_ending = 0

    pce = piece.white_pawn
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score_white_opening += pawn_table[sq120_to_sq64[sq]]
        score_white_ending += pawn_table_e[sq120_to_sq64[sq]]

    pce = piece.black_pawn
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score_black_opening += pawn_table[mirror64[sq120_to_sq64[sq]]]
        score_black_ending += pawn_table_e[mirror64[sq120_to_sq64[sq]]]

    return score_white_opening,score_white_ending,score_black_opening,score_black_ending

def eval_position(board):

    total_o_white = board.material[WHITE]
    total_e_white = board.material[WHITE]
    total_o_black = board.material[BLACK]
    total_e_black = board.material[BLACK]

    score = 0

    wo_pawns,we_pawns,bo_pawns,be_pawns=evaluate_pawns(board)

    pce = piece.white_knight
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score += knight_table[sq120_to_sq64[sq]]
    pce = piece.black_knight
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score -= knight_table[mirror64[sq120_to_sq64[sq]]]

    pce = piece.white_bishop
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score += bishop_table[sq120_to_sq64[sq]]
    pce = piece.black_bishop
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score -= bishop_table[mirror64[sq120_to_sq64[sq]]]

    pce = piece.white_rook
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score += rook_table[sq120_to_sq64[sq]]
    pce = piece.black_rook
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score -= rook_table[mirror64[sq120_to_sq64[sq]]]

    pce = piece.white_queen
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score += queen_table[sq120_to_sq64[sq]]
    pce = piece.black_queen
    for index in range(board.num_pieces[pce]):
        sq = board.piece_list[pce][index]

        score -= queen_table[mirror64[sq120_to_sq64[sq]]]

    #kings
    total_o_white += king_o[sq120_to_sq64[board.kingSq[WHITE]]]
    total_e_white += king_e[sq120_to_sq64[board.kingSq[WHITE]]]
    total_o_black += king_o[mirror64[sq120_to_sq64[board.kingSq[BLACK]]]]
    total_e_black += king_e[mirror64[sq120_to_sq64[board.kingSq[BLACK]]]]

    total_o_white+=wo_pawns
    total_e_white+=we_pawns
    total_o_black+=bo_pawns
    total_e_black+=be_pawns

    opening = adjust_opening_score(board, (total_o_white - total_o_black) + score)
    ending = adjust_ending_score(board, (total_e_white - total_e_black) + score)
    score = game_phase_scale(opening, ending, board.game_phase)

    if board.side == BLACK: score = -score
    return int(score)
