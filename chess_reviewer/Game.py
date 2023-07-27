import chess.pgn
import pygame
from Board import Board
import numpy as np
from Other_functions import FR_to_SQ
from Constants import piece,sq64_to_sq120,WHITE,mirror64,sq120_to_sq64,piece_color, \
    BLACK,START_FEN,MVFLAGEP,str_to_sq
from Move_gen import generate_all_moves
from Run_engine import draw_by_material,is_repetition
from Move_format import make_move,FROMSQ,TOSQ,MoveList,undo_move
from Attacks import is_attacked
from Squares import *

piece_dictss = {1: "wp", 4: "wR", 2: "wN",
                3: "wB", 5: "wQ", 6: "wK",
                7: "bp", 10: "bR", 8: "bN",
                9: "bB", 11: "bQ", 12: "bK"
                }
DIM = 8
HEIGHT=WIDTH=DIM*70
SQUARE_SIZE=HEIGHT//DIM
pieces_arr = ["wp", "wN", "wB", "wR", "wQ", "wK", "bp", "bN", "bB", "bR", "bQ", "bK"]
mirror_col = [7,6,5,4,3,2,1,0]
mirrored_sq = [
               h1, g1, f1, e1, d1, c1, b1, a1,
               h2, g2, f2, e2, d2, c2, b2, a2,
               h3, g3, f3, e3, d3, c3, b3, a3,
               h4, g4, f4, e4, d4, c4, b4, a4,
               h5, g5, f5, e5, d5, c5, b5, a5,
               h6, g6, f6, e6, d6, c6, b6, a6,
               h7, g7, f7, e7, d7, c7, b7, a7,
               h8, g8, f8, e8, d8, c8, b8, a8,
               ]

def is_legal_move(move, gs):
    lists=MoveList()
    generate_all_moves(gs, lists)

    for i in range(lists.count):
        moves=lists.moves[i].move

        if not make_move(gs, moves):
            continue

        undo_move(gs)

        if move==moves:
            return moves

    return 0
def load_images():
    images = {}
    for piecess in pieces_arr:
        images[piecess] = pygame.transform.scale(pygame.image.load("images/" + piecess + ".png"), (SQUARE_SIZE, SQUARE_SIZE))
    return images
def init2d():
    board2d = []
    r = 0
    for i in range(DIM):
        f = 0
        for j in range(DIM):
            board2d.append((r, f))
            f += 1
        r += 1

    return board2d

class Game:
    def __init__(self,screen,game_start_SFX,fen_font):
        self.already_went_endgame = False
        self.fen_font = fen_font
        self.game_start_SFX = game_start_SFX
        self.win = screen

        self.move_comments = None
        self.we_should_display_caps = False
        self.best_move_recommended = None
        self.eval_for_best = None
        self.move_cap = None

        self.removed_move = []
        self.white_moves = []
        self.black_moves = []
        self.game_positions = []
        self.captured_pieces = []
        self.initialized_fen = START_FEN
        self.board_state = Board()
        self.colors = [pygame.Color((160, 190, 160)), pygame.Color((0, 100, 0))]
        self.reversed_colors = [pygame.Color((0, 100, 0)),pygame.Color((160, 190, 160))]
        self.images = load_images()
        self.two_players = True
        self.move_made = False
        self.d2_board = init2d()
        self.valid_moves = MoveList()
        generate_all_moves(self.board_state,self.valid_moves)
        self.moves_history = []
        self.capture_history = []
        self.not_mirrored = False

        #inputs
        self.sq_selected = None
        self.player_clicks = []
        self.sq_tuple = (8,8)
        pygame.mixer.Sound.play(game_start_SFX)
    def update_valid_moves(self):
        self.valid_moves = MoveList()
        generate_all_moves(self.board_state, self.valid_moves)
    def highlight_squares(self):
        if self.sq_selected is not None:
            if self.not_mirrored:
                pce = self.board_state.pieces120[mirrored_sq[self.sq_selected]]
            else:
                pce = self.board_state.pieces120[sq64_to_sq120[mirror64[self.sq_selected]]]
            r, c = self.sq_tuple
            if piece_color[pce]==self.get_side():
                s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                s.set_alpha(110)
                s.fill(pygame.Color((255, 255, 0)))
                self.win.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
                s.fill(pygame.Color((255, 0, 0)))
                s.set_alpha(80)
                for i in range(self.valid_moves.count):
                    move = self.valid_moves.moves[i].move
                    sqto64 = mirror64[sq120_to_sq64[TOSQ(move)]] if not self.not_mirrored else sq120_to_sq64[TOSQ(move)]
                    move = is_legal_move(move,self.board_state)
                    if move != 0:
                        sq11 = sq64_to_sq120[mirror64[self.sq_selected]] if not self.not_mirrored else mirrored_sq[self.sq_selected]
                        if sq11 == FROMSQ(move):
                            if self.not_mirrored:self.win.blit(s, (mirror_col[self.d2_board[sqto64][1]] * SQUARE_SIZE, self.d2_board[sqto64][0] * SQUARE_SIZE))
                            else:self.win.blit(s, (self.d2_board[sqto64][1] * SQUARE_SIZE, self.d2_board[sqto64][0] * SQUARE_SIZE))
    def draw_board(self):
        for row in range(8):
            for col in range(8):
                color = self.colors[(row + col) % 2]
                pygame.draw.rect(self.win, color, pygame.Rect(col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

        if len(self.moves_history)>0:
            move = self.moves_history[-1]
            r,c = self.d2_board[mirror64[sq120_to_sq64[FROMSQ(move)]]] if not self.not_mirrored else self.d2_board[sq120_to_sq64[FROMSQ(move)]]
            if self.not_mirrored: c = mirror_col[c]
            s = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
            s.set_alpha(110)
            s.fill(pygame.Color((255, 255, 0)))
            self.win.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
            r, c = self.d2_board[mirror64[sq120_to_sq64[TOSQ(move)]]] if not self.not_mirrored else self.d2_board[sq120_to_sq64[TOSQ(move)]]
            if self.not_mirrored:c = mirror_col[c]
            self.win.blit(s, (c * SQUARE_SIZE, r * SQUARE_SIZE))
    def draw_pieces(self):
        temp_board = self.board_state.pieces120
        temp_board = temp_board.reshape(12, 10)
        if not self.not_mirrored:temp_board = np.flipud(temp_board)
        else:temp_board = np.fliplr(temp_board)
        temp_board = temp_board.reshape(120)

        for r in range(DIM):
            for f in range(DIM):
                sq = FR_to_SQ(f, r)

                piecess = temp_board[sq]
                if piecess != piece.EMPTY and piecess != piece.OFF_BOARD:
                    self.win.blit(self.images[piece_dictss[piecess]], pygame.Rect(f * SQUARE_SIZE, r * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
    def draw_move_caps(self):
        try:
            if self.we_should_display_caps:
                sqto64 = mirror64[sq120_to_sq64[TOSQ(self.moves_history[-1])]] if not self.not_mirrored else sq120_to_sq64[mirrored_sq[sq120_to_sq64[TOSQ(self.moves_history[-1])]]]
                if self.move_cap is not None:
                    image_cap = pygame.transform.scale(pygame.image.load("images/" + self.move_cap + ".png"),(SQUARE_SIZE//2,SQUARE_SIZE//2))
                    self.win.blit(image_cap,
                                  (self.d2_board[sqto64][1]*SQUARE_SIZE, self.d2_board[sqto64][0]*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
                if self.best_move_recommended is not None:
                    sq64_from = mirror64[sq120_to_sq64[str_to_sq[self.best_move_recommended[:2]]]] \
                        if not self.not_mirrored else sq120_to_sq64[mirrored_sq[sq120_to_sq64[str_to_sq[self.best_move_recommended[:2]]]]]
                    sq64_to = mirror64[sq120_to_sq64[str_to_sq[self.best_move_recommended[2:4]]]] \
                        if not self.not_mirrored else sq120_to_sq64[mirrored_sq[sq120_to_sq64[str_to_sq[self.best_move_recommended[2:4]]]]]



                    x_pos = ((self.d2_board[sq64_from][1] * SQUARE_SIZE) + SQUARE_SIZE // 2, (self.d2_board[sq64_from][0] * SQUARE_SIZE) + SQUARE_SIZE // 2)
                    y_pos = ((self.d2_board[sq64_to][1] * SQUARE_SIZE) + SQUARE_SIZE // 2, (self.d2_board[sq64_to][0] * SQUARE_SIZE) + SQUARE_SIZE // 2)
                    pygame.draw.line(self.win, pygame.Color("green"), x_pos,
                                     y_pos, 4)
                    pygame.draw.circle(self.win, pygame.Color("green"), y_pos, SQUARE_SIZE // 8)


        except IndexError:
            pass
    def draw_info(self):
        #fen
        # text = fen_font.render(self.board_state.board_to_fen(), True, (0, 0, 0))
        # self.win.blit(text, (WIDTH, 30))
        offset = 50

        #phase
        if self.board_state.game_phase < 43:
            if not self.already_went_endgame:phase = "opening"
            else:phase = "endgame"
        elif 43 <= self.board_state.game_phase < 171:
            if not self.already_went_endgame:phase = "middle game"
            else:phase = "endgame"
        else:
            if not self.already_went_endgame:self.already_went_endgame = True
            phase = "endgame"

        move_number = str(int(1 + (self.board_state.his_ply - (self.board_state.side == BLACK)) / 2))
        text = self.fen_font.render(f"Move number: {move_number}", True, (0, 0, 0))
        self.win.blit(text, (WIDTH + offset, 30))
        text = self.fen_font.render(f"Fifty Move Rule:{int(self.board_state.fifty_move)}", True, (0, 0, 0))
        self.win.blit(text, (WIDTH+offset, 60))
        text = self.fen_font.render(f"Phase:{phase.upper()}", True, (0, 0, 0))
        self.win.blit(text, (WIDTH+offset, 90))

        #if in check
        in_check,_ = is_attacked(self.board_state.kingSq[self.board_state.side], self.board_state.side ^ 1, self.board_state)
        text = self.fen_font.render(f"Check:{in_check}", True, (0, 0, 0))
        self.win.blit(text, (WIDTH+offset, 120))

        self.draw_captured()

        if self.we_should_display_caps:
            text = self.fen_font.render(f"best={self.best_move_recommended}", True, (0, 0, 0))
            self.win.blit(text, (WIDTH+offset, 240))
            text = self.fen_font.render(f"eval={self.eval_for_best}", True, (0, 0, 0))
            self.win.blit(text, (WIDTH+offset, 270))

            if self.eval_for_best is not None:
                if "M" not in self.eval_for_best and "G" not in self.eval_for_best:real_eval = int(self.eval_for_best)
                else:
                    if "G" not in self.eval_for_best:real_eval = int(self.eval_for_best[1:])
                    else:real_eval = 0
                mate_found = "M" in self.eval_for_best
            else:
                mate_found = False
                real_eval = 0
            self.draw_eval_bar(real_eval,mate_found)
    def draw_eval_bar(self, evaluation, mate_found):
        x1 = WIDTH
        x2 = WIDTH + 40
        x = evaluation
        eval_copy = x
        if mate_found:
            if eval_copy > 0:
                evaluation = 20000
            else:
                evaluation = -20000
        evaluation /= 2
        eval_bar_white = pygame.Rect((x1, 0),
                                     (x2 - x1, ((HEIGHT // 2) + evaluation) - 0))
        eval_bar_black = pygame.Rect((x1, (HEIGHT // 2) + evaluation),
                                     (x2 - x1, HEIGHT - ((HEIGHT // 2) + evaluation)))
        pygame.draw.rect(self.win, (10, 10, 10), eval_bar_black)
        pygame.draw.rect(self.win, (210, 210, 210), eval_bar_white)
    def reset_clicks(self):
        self.sq_selected = None
        self.player_clicks = []
        self.sq_tuple = (8,8)
    def is_game_over(self):
        if self.board_state.fifty_move >= 100:
            return "1/2-1/2","{Draw by Fifty Move Rule}"

        if is_repetition(self.board_state):
            return "1/2-1/2","{Draw by Threefold Repetition}"

        if draw_by_material(self.board_state):
            return "1/2-1/2","{Insufficient Material}"

        move_list = MoveList()
        generate_all_moves(self.board_state, move_list)
        legal = 0
        for move_num in range(move_list.count):
            if not make_move(self.board_state, move_list.moves[move_num].move):
                continue

            legal += 1
            undo_move(self.board_state)
            break

        in_check,_ = is_attacked(self.board_state.kingSq[self.board_state.side], self.board_state.side ^ 1, self.board_state)
        if legal == 0:
            if in_check:
                if self.board_state.side == WHITE:
                    return "0-1","{Black win by Checkmate}"
                else:
                    return "1-0","{White win by Checkmate}"
            else:
                return "1/2-1/2","{Stalemate}"
        return None
    def get_side(self):
        return self.board_state.side
    def draw_captured(self):
        white_caps = 0
        black_caps = 0
        offset = 50
        for cap in self.captured_pieces:
            if piece_color[cap]==WHITE:
                self.win.blit(pygame.transform.scale(self.images[piece_dictss[cap]], (20, 20)),
                              pygame.Rect(WIDTH+offset+(white_caps*11), 180, SQUARE_SIZE, SQUARE_SIZE))
                white_caps+=1
            else:
                self.win.blit(pygame.transform.scale(self.images[piece_dictss[cap]], (20, 20)),
                              pygame.Rect(WIDTH+offset+(black_caps*11), 150, SQUARE_SIZE, SQUARE_SIZE))
                black_caps+=1
    def reset_game(self):
        self.already_went_endgame = False
        self.removed_move = []
        self.white_moves = []
        self.move_comments = None
        self.black_moves = []
        self.best_move_recommended = None
        self.eval_for_best = None
        self.move_cap = None
        self.we_should_display_caps = False
        pygame.mixer.Sound.play(self.game_start_SFX)
        self.board_state = Board()
        self.game_positions = [self.board_state.board_to_fen()]
        self.move_made = False
        self.captured_pieces = []
        self.valid_moves = MoveList()
        self.initialized_fen = START_FEN
        generate_all_moves(self.board_state, self.valid_moves)
        self.moves_history = []
        self.capture_history = []

        # inputs
        self.sq_selected = None
        self.player_clicks = []
        self.sq_tuple = (8,8)
    def draw_all(self):
        self.draw_board()
        self.highlight_squares()
        self.draw_pieces()
        self.draw_info()
        self.draw_move_caps()
    def parse_pgn(self,path):
        self.reset_game()
        game_pgn = chess.pgn.read_game(open(path,'r'))

        main_moves = []
        for move in game_pgn.mainline_moves():
            main_moves.append(str(move))

        move_comments = []
        for node in game_pgn.mainline():
            move_comments.append((str(node.move),node.comment))

        for i in range(len(main_moves)-1,-1,-1):
            move = main_moves[i]
            self.removed_move.append(move)

        return game_pgn.headers["Site"],move_comments
    def make_the_move(self,move):
        to_sq = TOSQ(move)
        we_captured = self.board_state.pieces120[to_sq] != piece.EMPTY
        self.moves_history.append(move)
        if move & MVFLAGEP: self.captured_pieces.append(
            piece.white_pawn if self.get_side() == BLACK else piece.black_pawn)
        if we_captured:
            self.capture_history.append(move)
            self.captured_pieces.append(self.board_state.pieces120[to_sq])
        if self.get_side() == WHITE:
            self.white_moves.append(move)
        else:
            self.black_moves.append(move)
        make_move(self.board_state, move)
        self.game_positions.append(self.board_state.board_to_fen())
        self.board_state.ply = 0
        self.move_made = True