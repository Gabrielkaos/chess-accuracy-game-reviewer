import numpy as np
from Constants import BOTH, NO_SQ, WHITE, BLACK, RANK_8, RANK_1, FILE_A, FILE_H
from Constants import piece, MAX_DEPTH, BOARD_NUM_SQ
from Constants import WKCA, WQCA, BKCA, BQCA, START_FEN, piece_color, piece_big
from Constants import str_to_sq, sq_to_str, max_game_moves, piece_value
from Undo import Undo
from Other_functions import FR_to_SQ,get_game_phase
from Asserts import is_piece_king
from Pv_table import PVTable
from Hash_keys import init_hash_keys,generate_pos_key
import io

class Board:
    def __init__(self):

        # PVTable
        self.pv_table = PVTable()
        self.pv_array = np.zeros(max_game_moves, dtype=np.int)

        # board things
        self.side = BOTH
        self.pieces120 = np.zeros(BOARD_NUM_SQ, dtype=np.int)
        self.castle_rights = 0
        self.en_passant = NO_SQ
        self.fifty_move = 0

        # extra board things
        self.game_phase = 0
        self.num_pieces = np.zeros(13, dtype=np.int)
        self.piece_list = np.zeros((13, 10), dtype=np.int)
        self.material = np.zeros(2, dtype=np.int)
        self.kingSq = np.zeros(2, dtype=np.int)
        self.big_piece = np.zeros(2, dtype=np.int)

        # board history things
        self.ply = 0
        self.his_ply = 0
        self.history = np.array([Undo() for _ in range(max_game_moves)])

        # zobrist hashing things
        self.position_key = np.uint64(0)
        self.side_key = np.uint64(0)
        self.piece_keys = np.zeros((13, BOARD_NUM_SQ), dtype=np.uint64)
        self.castle_keys = np.zeros(16, dtype=np.uint64)
        init_hash_keys(self)

        # search things
        self.search_killers = np.zeros((2, MAX_DEPTH), dtype=np.int)
        self.search_history = np.zeros((13, BOARD_NUM_SQ), dtype=np.int)

        # parsing start fen
        self.parse_fen(START_FEN)

    def reset(self):

        # board things
        for i in range(BOARD_NUM_SQ):
            self.pieces120[i] = piece.OFF_BOARD
        self.castle_rights = 0
        self.en_passant = NO_SQ
        self.side = BOTH
        self.fifty_move = 0

        # extra board things
        self.game_phase = 0
        for i in range(2):
            self.material[i] = 0
            self.kingSq[i] = 0
            self.big_piece[i] = 0

        for i in range(13):
            self.num_pieces[i] = 0
            for j in range(10):
                self.piece_list[i][j] = 0

        # hash things
        self.position_key = np.uint64(0)

    def update_board_things(self):
        for sq in range(BOARD_NUM_SQ):
            if (self.pieces120[sq] != piece.EMPTY) and (self.pieces120[sq] != piece.OFF_BOARD):
                pce = self.pieces120[sq]
                color = piece_color[pce]

                self.piece_list[pce][self.num_pieces[pce]] = sq
                self.num_pieces[pce] += 1
                self.material[color] += piece_value[pce]
                if piece_big[pce]:
                    self.big_piece[color] += 1
                if is_piece_king(pce):
                    self.kingSq[color] = sq
        self.game_phase =get_game_phase(self)

    def parse_fen(self, fen):
        self.reset()
        board = list('         \n' * 2 + ' ' + ''.join([
            '.' * int(c) if c.isdigit() else c
            for c in fen.split()[0].replace('/', '\n ')
        ]) + '\n' + '         \n' * 2)

        board = np.array(board)
        board = np.resize(board, (12, 10))
        board = np.flipud(board)
        board = board.reshape(BOARD_NUM_SQ)

        for i, x in enumerate(board):
            if x == '.':
                self.pieces120[i] = piece.EMPTY
            if x == 'p':
                self.pieces120[i] = piece.black_pawn
            if x == 'P':
                self.pieces120[i] = piece.white_pawn
            if x == 'r':
                self.pieces120[i] = piece.black_rook
            if x == 'R':
                self.pieces120[i] = piece.white_rook
            if x == 'n':
                self.pieces120[i] = piece.black_knight
            if x == 'N':
                self.pieces120[i] = piece.white_knight
            if x == 'b':
                self.pieces120[i] = piece.black_bishop
            if x == 'B':
                self.pieces120[i] = piece.white_bishop
            if x == 'q':
                self.pieces120[i] = piece.black_queen
            if x == 'Q':
                self.pieces120[i] = piece.white_queen
            if x == 'k':
                self.pieces120[i] = piece.black_king
            if x == 'K':
                self.pieces120[i] = piece.white_king

        # side
        string_side = fen.split(" ")[1]
        if string_side == "w":
            self.side = WHITE
        else:
            self.side = BLACK

        # castle rights
        string_ca = fen.split(" ")[2]
        if 'K' in string_ca: self.castle_rights |= WKCA
        if 'Q' in string_ca: self.castle_rights |= WQCA
        if 'k' in string_ca: self.castle_rights |= BKCA
        if 'q' in string_ca: self.castle_rights |= BQCA

        # enpassant
        string_ep = fen.split(" ")[3]
        self.en_passant = str_to_sq[string_ep]

        self.update_board_things()
        self.position_key = generate_pos_key(self)

    def board_to_fen(self):
        piece_char = {1: "P", 2: "N", 3: "B", 4: "R", 5: "Q", 6: "K", 7: "p", 8: "n", 9: "b", 10: "r", 11: "q", 12: "k"}
        board = self.pieces120.reshape(12, 10)
        board = np.flipud(board)
        with io.StringIO() as s:
            for row in board:
                empty = 0
                for cell in row:
                    c = cell
                    if c == piece.OFF_BOARD:
                        continue
                    if c in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                        if empty > 0:
                            s.write(str(empty))
                            empty = 0
                        s.write(piece_char[c])
                    else:
                        empty += 1
                if empty > 0:
                    s.write(str(empty))
                s.write('/')
            s.seek(s.tell() - 3)
            side_char = {0: "w", 1: "b"}
            s.write(" " + side_char[self.side])

            if self.castle_rights & WKCA:
                a = "K"
            else:
                a = ""
            if self.castle_rights & WQCA:
                b = "Q"
            else:
                b = ""
            if self.castle_rights & BKCA:
                c = "k"
            else:
                c = ""
            if self.castle_rights & BQCA:
                d = "q"
            else:
                d = ""
            if a == "" and b == "" and c == "" and d == "":
                s.write(" -")
            else:
                s.write(" " + (a + b + c + d))

            if self.en_passant == NO_SQ:
                a = "-"
            else:
                a = sq_to_str[self.en_passant]
            s.write(" " + a)
            s.write(" " + str(self.fifty_move))
            result = s.getvalue()
            result = result[2:]
            result += " " + str(int(1 + (self.his_ply - (self.side == BLACK)) / 2))
            return result

    def print_board(self):
        piece_char = {1: "P", 2: "N", 3: "B", 4: "R", 5: "Q", 6: "K", 7: "p", 8: "n", 9: "b", 10: "r", 11: "q", 12: "k"}
        board = self.pieces120.reshape(12, 10)
        board = np.flipud(board)
        with io.StringIO() as s:
            for row in board:
                empty = 0
                for cell in row:
                    c = cell
                    if c == piece.OFF_BOARD:
                        continue
                    if c in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
                        if empty > 0:
                            s.write(str(empty))
                            empty = 0
                        s.write(piece_char[c])
                    else:
                        empty += 1
                if empty > 0:
                    s.write(str(empty))
                s.write('/')
            s.seek(s.tell() - 3)
            side_char = {0: "w", 1: "b"}
            s.write(" " + side_char[self.side])

            if self.castle_rights & WKCA:
                a = "K"
            else:
                a = ""
            if self.castle_rights & WQCA:
                b = "Q"
            else:
                b = ""
            if self.castle_rights & BKCA:
                c = "k"
            else:
                c = ""
            if self.castle_rights & BQCA:
                d = "q"
            else:
                d = ""
            if a == "" and b == "" and c == "" and d == "":
                s.write(" -")
            else:
                s.write(" " + (a + b + c + d))

            if self.en_passant == NO_SQ:
                a = "-"
            else:
                a = sq_to_str[self.en_passant]
            s.write(" " + a)
            s.write(" " + str(self.fifty_move))
            result = s.getvalue()
            result = result[2:]
            result += " " + str(int(1 + (self.his_ply - (self.side == BLACK)) / 2))

            # printing board legit
            rank = RANK_8
            while rank >= RANK_1:
                file = FILE_A
                print(f" {rank + 1}  ", end="")
                while file <= FILE_H:
                    sq = FR_to_SQ(file, rank)
                    pce = self.pieces120[sq]
                    if pce == piece.EMPTY:
                        print(".  ", end="")
                    else:
                        print(piece_char[pce] + "  ", end="")
                    if file != 0 and (file % 7) == 0:
                        print()
                    file += 1
                rank -= 1
            print("    a  b  c  d  e  f  g  h")
            print()
            print(f"fen:{result}")
            print(f"key:{hex(self.position_key)}")
            return
