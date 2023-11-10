from enum import Enum

# chess_board = [
#    "a8", "b8", "c8", "d8", "e8", "f8", "g8", "h8",
#    "a7", "b7", "c7", "d7", "e7", "f7", "g7", "h7", 
#    "a6", "b6", "c6", "d6", "e6", "f6", "g6", "h6",
#    "a5", "b5", "c5", "d5", "e5", "f5", "g5", "h5",
#    "a4", "b4", "c4", "d4", "e4", "f4", "g4", "h4",
#    "a3", "b3", "c3", "d3", "e3", "f3", "g3", "h3",
#    "a2", "b2", "c2", "d2", "e2", "f2", "g2", "h2",
#    "a1", "b1", "c1", "d1", "e1", "f1", "g1", "h1",
# ]

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# initial values
chessboard = [0] * 64
piece_placement = "8/8/8/8/8/8/8/8"
starting_color = "w"                # "w" for white, "b" for black
castling_rights = "KQkq"            # uppercase for white, lowercase for black
en_passant = "-"                    # "-" for null
halfmove_clock = 0
fullmove_number = 1

########################################################

class Piece(Enum):
    NULL    = 0
    KING    = 1
    PAWN    = 2
    KNIGHT  = 3
    BISHOP  = 4
    ROOK    = 5
    QUEEN   = 6

    WHITE = 8
    BLACK = 16

########################################################

def load_fen_position():

    global piece_placement
    global starting_color
    global castling_rights
    global en_passant
    global halfmove_clock
    global fullmove_number

    piece_from_fen_symbol = { # dictionary for piecetype to Fen symbol
        'p' : Piece.PAWN.value,
        'n' : Piece.KNIGHT.value,
        'b' : Piece.BISHOP.value,
        'r' : Piece.ROOK.value,
        'q' : Piece.QUEEN.value,
        'k' : Piece.KING.value
    }

    # all the data from the FEN string
    fen_split        = STARTING_FEN.split(' ')
    piece_placement  = fen_split[0]
    starting_color   = fen_split[1]
    castling_rights  = fen_split[2]
    en_passant       = fen_split[3]
    halfmove_clock   = fen_split[4]
    fullmove_number  = fen_split[5]

    fenBoard = [x for x in piece_placement]
    boardIndex = 0
    for x in fenBoard:
        if x == '/':
            continue
        elif x.isnumeric():
            boardIndex += int(x)
        else:
            if x.isupper():
                chessboard[boardIndex] = piece_from_fen_symbol.get(x.lower()) + Piece.WHITE.value
            else:
                chessboard[boardIndex] = piece_from_fen_symbol.get(x.lower()) + Piece.BLACK.value
            boardIndex += 1

load_fen_position()
print(chessboard)