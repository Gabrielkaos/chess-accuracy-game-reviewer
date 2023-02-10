import pygame
from Other_functions import FR_to_SQ
from Constants import piece,sq64_to_sq120,WHITE,mirror64,sq_to_str,sq120_to_sq64,piece_color,piece_big,rank7,rank2,\
    BLACK,MVFLAGCA,START_FEN,MVFLAGEP
from I_o import parse_move,str_move
from Pv_table import move_really_exists
from Move_format import undo_move,CAPTURED
from Game import Game,HEIGHT,WIDTH,SQUARE_SIZE,DIM,mirrored_sq
import pyperclip
from subprocess import Popen, PIPE, STDOUT
from Analyzer import accuracy_full_game

#TODO
# pgn loader

pygame.init()

pygame.display.set_caption("Gab Chess Gui")
pygame.display.set_icon(pygame.image.load("logo/gabchessgui.png"))
fen_font = pygame.font.Font('freesansbold.ttf', 13)
move_SFX = pygame.mixer.Sound("sounds/moves_sound.mp3")
castle_SFX = pygame.mixer.Sound("sounds/castle_sound.mp3")
capture_SFX = pygame.mixer.Sound("sounds/captured_sound.mp3")
game_start_SFX = pygame.mixer.Sound("sounds/game_start_chess.mp3.mp3")

goob_e = "C:/Users/LENOVO/Desktop/someEngines/CE_PVSBRUTE.exe"
the_engine = Popen([goob_e], stdout=PIPE, stdin=PIPE, stderr=STDOUT, bufsize=0, text=True)
def command(p, commands):
    p.stdin.write(f'{commands}\n')
def engine(time, game):
    with_move = None
    moves_so_far = ""
    for i,move in enumerate(game.moves_history):
        if i != (len(game.moves_history) - 1):
            moves_so_far+=str_move(move)+" "
        else:moves_so_far+=str_move(move)
    # position startpos moves e2e4
    if game.initialized_fen==START_FEN:
        if moves_so_far =="":input_one = f'position startpos'
        else:input_one = f'position startpos moves {moves_so_far}'
    else:
        if moves_so_far=="":input_one = f'position fen {game.initialized_fen}'
        else:input_one = f'position fen {game.initialized_fen} moves {moves_so_far}'
    input_one=input_one.rstrip()
    command(the_engine, input_one)

    # go movetime 1000
    line = f"go movetime {time*1000}".rstrip()
    command(the_engine, line)
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        print(e_line)
        if 'bestmove' in e_line:
            with_move = e_line
            break
    move_str = with_move.split(" ")[1]
    return parse_move(move_str,game.board_state)
def init_engine():
    command(the_engine, 'uci')
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        if 'uciok' in e_line:
            break
    command(the_engine, 'ucinewgame')
    command(the_engine,'isready')
    for ELINES in iter(the_engine.stdout.readline, ''):
        e_line = ELINES.strip()
        if 'readyok' in e_line:
            break
def move_cap(acc,move,best_move):
    if acc > 377.6:return "legendary" #considered a legendary if you gain 30% win rate
    if acc > 156.1: return "brilliant"  # considered a brilliance if you gain 10% win rate
    if acc > 108.5:return "great" #considered great if you gain 20 centipawns

    # conditioned best move
    # if not legendary and not brilliant and not great
    # but still the same as best move
    if move is not None and best_move is not None:
        if str_move(move)==best_move:
            return "best"
    if acc > 99.5:return "excellent" #considered excellent if you only lost 1 centipawns
    if acc > 88.4:return "good" #considered good if you only lost 30 centipawns
    if acc > 81.4:return "inaccuracy" #if you lost 50 centipawns
    if acc > 68.9:return "mistake" #if you lost 90 centipawns
    if acc <= 68.9:return "blunder" #none of the above
    return ""
def find_the_move_and_cap(moves_from_pgn,move):
    if moves_from_pgn is None:
        return None,None
    for i in moves_from_pgn:
        if i[0]==move:
            return i[0],i[1]
    return None,None

def main():

    """

    controls
    r - reset game
    b - make ai play black
    w - make ai play white
    DOWN - think time of ai minus 1
    UP - think time of ai plus 1
    c - copy fen
    p - parse fen from clipboard
    LEFT - undo move
    RIGHT - make removed move again
    s - quit pygame and analyze and save game as pgn
    l - load pgn
    f - flip board
    """

    init_engine()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(screen,game_start_SFX,fen_font)

    game.two_players=True
    human = BLACK

    #searcher settings
    think_time = 1

    game.game_positions.append(game.board_state.board_to_fen())

    while True:
        screen.fill(pygame.Color("grey"))

        #ai
        if not game.we_should_display_caps and not game.is_game_over() and not game.two_players and game.get_side() != human:
            move = engine(think_time,game)
            game.make_the_move(move)

        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                command(the_engine,'quit')
                pygame.quit()
                exit(0)
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_r:
                    game.reset_game()
                    game.two_players = True
                    init_engine()
                elif event.key == pygame.K_f:game.not_mirrored^=True
                elif event.key == pygame.K_l:
                    init_engine()
                    site_pgn,game.move_comments = game.parse_pgn("C:/Users/LENOVO/PycharmProjects/my_chess_engine/pgns/saved_pgn.pgn")
                    if site_pgn.lower() != "gabchessgui":
                        while len(game.removed_move)>0:
                            move = parse_move(game.removed_move.pop(),game.board_state)
                            game.make_the_move(move)
                    else:
                        game.we_should_display_caps = True
                        game.move_cap = None
                        game.best_move_recommended = None
                elif event.key==pygame.K_s:
                    pygame.quit()
                    command(the_engine,'quit')

                    if 1 <= think_time < 5:depth = 16
                    elif 4 < think_time < 10:depth = 18
                    else:depth = 20

                    if not game.two_players:
                        black_name = "not human" if human==WHITE else "human"
                        white_name = "not human" if human==BLACK else "human"
                    else:
                        black_name=input("Enter black name:")
                        white_name=input("Enter white name:")
                    print()
                    best_moves,accuracies,w_acc,b_acc = accuracy_full_game(game.game_positions,depth)
                    white_best_moves = best_moves[0]
                    black_best_moves = best_moves[1]

                    le_moves = [0,0]
                    br_moves = [0,0]
                    gr_moves = [0,0]
                    ex_moves = [0,0]
                    go_moves = [0,0]
                    in_moves = [0,0]
                    mis_moves = [0,0]
                    blunders = [0,0]
                    be_moves = [0,0]

                    open('pgns/saved_pgn.pgn','w').close() #delete content
                    file = open('pgns/saved_pgn.pgn','a')
                    file.writelines(f'[Event "Simple Game"]\n')
                    file.writelines(f'[Site "GabChessGui"]\n')
                    file.writelines(f"[White '{white_name}']\n")
                    file.writelines(f"[Black '{black_name}']\n")
                    if game.is_game_over() is None:
                        file.writelines("[Result '*']\n\n")
                    else:file.writelines(f"[Result {game.is_game_over()[0]}]\n\n")

                    for i in range(len(game.white_moves)):

                        w_best=b_best=""

                        w_move = game.white_moves[i]
                        try:b_move = game.black_moves[i]
                        except IndexError:b_move=None

                        try:w_move_cap = move_cap(accuracies[0][i],w_move,None if w_move is None else white_best_moves[i])
                        except IndexError:w_move_cap = ""
                        try:b_move_cap = move_cap(accuracies[1][i],b_move,None if b_move is None else black_best_moves[i])
                        except IndexError:b_move_cap = ""

                        try:
                            if str_move(w_move) != white_best_moves[i]:
                                if w_move_cap not in ["best","great","brilliant","legendary"]:
                                    w_best = white_best_moves[i]
                        except IndexError:
                            w_best = ""

                        try:
                            if str_move(b_move) != black_best_moves[i]:
                                if b_move_cap not in ["best","great","brilliant","legendary"]:
                                    b_best = black_best_moves[i]
                        except IndexError:
                            b_best = ""

                        if b_move_cap == "legendary": le_moves[1] += 1
                        if w_move_cap == "legendary": le_moves[0] += 1
                        if b_move_cap=="brilliant":br_moves[1]+=1
                        if w_move_cap=="brilliant":br_moves[0]+=1
                        if b_move_cap=="great":gr_moves[1]+=1
                        if w_move_cap=="great":gr_moves[0]+=1
                        if b_move_cap=="best":be_moves[1]+=1
                        if w_move_cap=="best":be_moves[0]+=1
                        if b_move_cap=="excellent":ex_moves[1]+=1
                        if w_move_cap=="excellent":ex_moves[0]+=1
                        if b_move_cap=="good":go_moves[1]+=1
                        if w_move_cap=="good":go_moves[0]+=1
                        if b_move_cap=="inaccuracy":in_moves[1]+=1
                        if w_move_cap=="inaccuracy":in_moves[0]+=1
                        if b_move_cap=="mistake":mis_moves[1]+=1
                        if w_move_cap=="mistake":mis_moves[0]+=1
                        if b_move_cap=="blunder":blunders[1]+=1
                        if w_move_cap=="blunder":blunders[0]+=1

                        w_move_cap = w_move_cap + ("" if w_best=="" else f" best={w_best}")
                        b_move_cap = b_move_cap + ("" if b_best == "" else f" best={b_best}")

                        file.writelines(
                                f"{i+1}. {str_move(w_move)} {'{'+w_move_cap+'}'} {str_move(b_move)} {'{'+b_move_cap+'}'} ")
                        if i==len(game.white_moves) - 1:
                            file.writelines(
                                f"{'*' if game.is_game_over() is None else game.is_game_over()[1]}")


                    print(accuracies[0])
                    print(accuracies[1])
                    #game review
                    print(f"\n\nwhite:{white_name}")
                    print(f"white legendary moves:{le_moves[0]}")
                    print(f"white brilliant moves:{br_moves[0]}")
                    print(f"white great moves:{gr_moves[0]}")
                    print(f"white best moves:{be_moves[0]}")
                    print(f"white excellent moves:{ex_moves[0]}")
                    print(f"white good moves:{go_moves[0]}")
                    print(f"white inaccuracies:{in_moves[0]}")
                    print(f"white mistakes:{mis_moves[0]}")
                    print(f"white blunders:{blunders[0]}")
                    print(f"white accuracy:{w_acc:.2f}%\n")
                    
                    print(f"black:{black_name}")
                    print(f"black legendary moves:{le_moves[1]}")
                    print(f"black brilliant moves:{br_moves[1]}")
                    print(f"black great moves:{gr_moves[1]}")
                    print(f"black best moves:{be_moves[1]}")
                    print(f"black excellent moves:{ex_moves[1]}")
                    print(f"black good moves:{go_moves[1]}")
                    print(f"black inaccuracies:{in_moves[1]}")
                    print(f"black mistakes:{mis_moves[1]}")
                    print(f"black blunders:{blunders[1]}")
                    print(f"black accuracy:{b_acc:.2f}%")
                    
                    print("\nFile Saved")
                    file.close()

                    exit(0)
                elif event.key==pygame.K_b:
                    game.two_players=False
                    human=WHITE
                    game.not_mirrored = not game.two_players and human == WHITE
                elif event.key==pygame.K_w:
                    game.two_players=False
                    human=BLACK
                    game.not_mirrored = not game.two_players and human == WHITE
                elif event.key==pygame.K_DOWN:
                    think_time-=1
                    if think_time<1:
                        think_time=1
                    print(think_time)
                elif event.key==pygame.K_UP:
                    think_time+=1
                    print(think_time)
                elif event.key == pygame.K_RIGHT:
                    if len(game.removed_move) > 0:
                        move = parse_move(game.removed_move.pop(),game.board_state)
                        a,c = find_the_move_and_cap(game.move_comments,str_move(move))
                        game.move_cap = c.split(" ")[0].strip()
                        try:game.best_move_recommended = c.split("=")[1].strip()
                        except IndexError:game.best_move_recommended = None

                        if game.best_move_recommended is not None and game.move_cap is not None:
                            if game.best_move_recommended in game.move_cap:game.move_cap = game.move_cap.split("\n")[0]
                        if game.move_cap not in ["legendary","brilliant","great","best","excellent","good","inaccuracy","mistake","blunder"]:
                            game.move_cap=None
                        # print(f"{str_move(move)}={game.move_cap}{'' if game.best_move_recommended is None else f' best is {game.best_move_recommended}'}")
                        game.make_the_move(move)
                elif event.key==pygame.K_LEFT:
                    if game.board_state.his_ply > 0:
                        game.two_players = True
                        undo_move(game.board_state)
                        move = game.moves_history.pop()
                        if game.get_side() == WHITE:
                            game.white_moves.pop()
                        else:
                            game.black_moves.pop()
                        game.removed_move.append(str_move(move))
                        if move & MVFLAGEP:game.captured_pieces.remove(piece.white_pawn if game.get_side()==BLACK else piece.black_pawn)
                        if move in game.capture_history:
                            game.capture_history.remove(move)
                            game.captured_pieces.remove(CAPTURED(move))
                        game.move_made=True
                        game.game_positions.pop()
                        game.board_state.ply = 0
                elif event.key==pygame.K_c:pyperclip.copy(game.board_state.board_to_fen())
                elif event.key==pygame.K_p:
                    fen = pyperclip.paste()
                    game.parse_game(fen)
            elif event.type==pygame.MOUSEBUTTONDOWN:
                if not game.is_game_over():
                    pos = pygame.mouse.get_pos()
                    col = pos[0]//SQUARE_SIZE
                    row = pos[1]//SQUARE_SIZE

                    sq120 = FR_to_SQ(col,row)
                    sq = sq120_to_sq64[sq120]

                    if game.sq_selected == sq or col >= DIM or col < 0:
                        game.reset_clicks()
                    else:
                        game.sq_selected = sq
                        game.sq_tuple = (row,col)
                        game.player_clicks.append(sq)

                    if len(game.player_clicks)==2 and (game.two_players or human==game.get_side()) and \
                            not game.we_should_display_caps:
                        if not game.not_mirrored:
                            move_str_from = sq_to_str[sq64_to_sq120[mirror64[game.player_clicks[0]]]]
                            move_str_to = sq_to_str[sq64_to_sq120[mirror64[game.player_clicks[1]]]]
                        else:
                            move_str_from = sq_to_str[mirrored_sq[game.player_clicks[0]]]
                            move_str_to = sq_to_str[mirrored_sq[game.player_clicks[1]]]

                        #handling promotions
                        if not game.not_mirrored:
                            from_pce = game.board_state.pieces120[sq64_to_sq120[mirror64[game.player_clicks[0]]]]
                        else:
                            from_pce = game.board_state.pieces120[mirrored_sq[game.player_clicks[0]]]
                        pce_color = piece_color[from_pce]
                        if not game.not_mirrored:from_sq = sq64_to_sq120[mirror64[game.player_clicks[0]]]
                        else:from_sq = mirrored_sq[game.player_clicks[0]]

                        promotion=""
                        if not piece_big[from_pce] and pce_color==game.get_side():
                            if (game.get_side()==WHITE and from_sq in rank7) or \
                                    (game.get_side() == BLACK and from_sq in rank2):
                                promotion = input("select from [n,b,r,q]:")
                                if promotion not in ["q","r","b","n"]:
                                    promotion="q"

                        move = parse_move(move_str_from+move_str_to+promotion, game.board_state)

                        try:
                            if move_really_exists(game.board_state,move):
                                game.make_the_move(move)
                                game.reset_clicks()
                            else:
                                game.player_clicks = [game.sq_selected]
                        except AttributeError:
                            game.player_clicks = [game.sq_selected]

        if game.move_made:

            #sounds
            if (game.moves_history[-1] & MVFLAGEP if len(game.moves_history)>0 else False) or \
                    (game.moves_history[-1]==game.capture_history[-1] if len(game.capture_history)>0 else False):pygame.mixer.Sound.play(capture_SFX)
            elif len(game.moves_history)>0 and (game.moves_history[-1] & MVFLAGCA):pygame.mixer.Sound.play(castle_SFX)
            else:pygame.mixer.Sound.play(move_SFX)

            #important things
            game.move_made = False
            game.update_valid_moves()

        game.draw_all()

        pygame.display.update()

if __name__=='__MAIN__'.lower():
    main()
    command(the_engine,'quit')