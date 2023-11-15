import string
from itertools import count
from collections import namedtuple

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

##############################################

# values for each pieces
PIECE = {"P": 100, "N": 280, "B": 320, "R": 479, "Q": 929, "K": 60000}
# Piece-Square tables to determine where a piece has the most value
PIECE_SQUARE_TABLES = {
    'P': (   0,   0,   0,   0,   0,   0,   0,   0,
            78,  83,  86,  73, 102,  82,  85,  90,
            7,  29,  21,  44,  40,  31,  44,   7,
            -17,  16,  -2,  15,  14,   0,  15, -13,
            -26,   3,  10,   9,   6,   1,   0, -23,
            -22,   9,   5, -11, -10,  -2,   3, -19,
            -31,   8,  -7, -37, -36, -14,   3, -31,
            0,   0,   0,   0,   0,   0,   0,   0),
    'N': ( -66, -53, -75, -75, -10, -55, -58, -70,
            -3,  -6, 100, -36,   4,  62,  -4, -14,
            10,  67,   1,  74,  73,  27,  62,  -2,
            24,  24,  45,  37,  33,  41,  25,  17,
            -1,   5,  31,  21,  22,  35,   2,   0,
            -18,  10,  13,  22,  18,  15,  11, -14,
            -23, -15,   2,   0,   2,   0, -23, -20,
            -74, -23, -26, -24, -19, -35, -22, -69),
    'B': ( -59, -78, -82, -76, -23,-107, -37, -50,
            -11,  20,  35, -42, -39,  31,   2, -22,
            -9,  39, -32,  41,  52, -10,  28, -14,
            25,  17,  20,  34,  26,  25,  15,  10,
            13,  10,  17,  23,  17,  16,   0,   7,
            14,  25,  24,  15,   8,  25,  20,  15,
            19,  20,  11,   6,   7,   6,  20,  16,
            -7,   2, -15, -12, -14, -15, -10, -10),
    'R': (  35,  29,  33,   4,  37,  33,  56,  50,
            55,  29,  56,  67,  55,  62,  34,  60,
            19,  35,  28,  33,  45,  27,  25,  15,
            0,   5,  16,  13,  18,  -4,  -9,  -6,
            -28, -35, -16, -21, -13, -29, -46, -30,
            -42, -28, -42, -25, -25, -35, -26, -46,
            -53, -38, -31, -26, -29, -43, -44, -53,
            -30, -24, -18,   5,  -2, -18, -31, -32),
    'Q': (   6,   1,  -8,-104,  69,  24,  88,  26,
            14,  32,  60, -10,  20,  76,  57,  24,
            -2,  43,  32,  60,  72,  63,  43,   2,
            1, -16,  22,  17,  25,  20, -13,  -6,
            -14, -15,  -2,  -5,  -1, -10, -20, -22,
            -30,  -6, -13, -11, -16, -11, -16, -27,
            -36, -18,   0, -19, -15, -15, -21, -38,
            -39, -30, -31, -13, -31, -36, -34, -42),
    'K': (   4,  54,  47, -99, -99,  60,  83, -62,
            -32,  10,  55,  56,  56,  55,  10,   3,
            -62,  12, -57,  44, -67,  28,  37, -31,
            -55,  50,  11,  -4, -19,  13,   0, -49,
            -55, -43, -52, -28, -51, -47,  -8, -50,
            -47, -42, -43, -79, -64, -32, -29, -32,
            -4,   3, -14, -50, -57, -18,  13,   4,
            17,  30,  -3, -14,   6,  -1,  40,  18),
}

#################################################

# Lists of possible moves for each piece type.
A1, H1, A8, H8 = 91, 98, 21, 28
N, E, S, W = -10, 1, 10, -1
DIRECTIONS = {
    "P": (N, N+N, N+W, N+E),
    "N": (N+N+E, E+N+E, E+S+E, S+S+E, S+S+W, W+S+W, W+N+W, N+N+W),
    "B": (N+E, S+E, S+W, N+W),
    "R": (N, E, S, W),
    "Q": (N, E, S, W, N+E, S+E, S+W, N+W),
    "K": (N, E, S, W, N+E, S+E, S+W, N+W)
}

##############################################

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 0"

# initializes data structure for initial state
State = namedtuple("State", "board value ac cr ep kp")
# board - 120 char representation of the board
# value - value evaluation of the board
# ac - active color (0 is white, 1 is black)
# cr - castling rights, UPPERCASE for white, lowercase for black
# ep - en passant square
# kp - the king passant square

# initializes data structure for initial state
Move = namedtuple("Move", "start end promote")
# start - starting index
# end - end index
# promote - if there is a promotion event

def insert(board, index, piece):
    '''
    Inserts piece into the board.
    '''
    return board[:index] + piece + board[index + 1 :]

def load_from_fen():
    '''
    Takes the tuple of initial state and assigns FEN values to it.
    '''
    # all the data from the FEN string
    fen_split = STARTING_FEN.split(' ')

    # active color
    ac = 0 if fen_split[1] == "w" else 1

    # convert enpassant square from standard notation into index
    ep = fen_split[3]
    if ep != "-":
        ep = A1 + string.ascii_lowercase.index(ep[0]) + (int(ep[1]) * 10)
    else: ep = 0

    # initialize board with 64 empty characters
    raw_board = "." * 64

    # fill board with values from the FEN
    fen_board = [x for x in fen_split[0]]
    board_index = 0
    for x in fen_board:
        if x != '/':
            if x.isnumeric():
                board_index += int(x)
            else:
                raw_board = insert(raw_board, board_index, x)
                board_index += 1

    # initialize padded rows board
    padded_rows_board = ""
    # pad the board with two 0s deep on each side
    padrow = lambda row: " " + row + " "
    for i in range(8):
        padded_rows_board += padrow(raw_board[i * 8 : i * 8 + 8])
    # pad the rows with an " " on each side
    raw_board = " " * 20 + padded_rows_board + " " * 20
    board = raw_board

    # here, we take both the piece values and the piece-square tables and combine them
    # we also pad the table with two 0s on all sides for easier illegal-move catches
    for k, table in PIECE_SQUARE_TABLES.items():
        padrow = lambda row: (0,) + tuple(x + PIECE[k] for x in row) + (0,)
        PIECE_SQUARE_TABLES[k] = sum((padrow(table[i * 8 : i * 8 + 8]) for i in range(8)), ())
        PIECE_SQUARE_TABLES[k] = (0,) * 20 + PIECE_SQUARE_TABLES[k] + (0,) * 20

    return State(board, 0, ac, fen_split[2], ep, 0)

INITIAL_STATE = load_from_fen()

############################################

class BoardState(State):
    '''
    A state of a chess game.
    '''

    def generate_moves(self, check = False):
        '''
        Returns list of available moves for all active indexes.
        '''
        for index, piece in enumerate(self.board):
            # only consider the UPPERCASE pieces
            if not piece.isupper():
                continue
            # iterate through the piece's direction list
            for direction in DIRECTIONS[piece]:
                # for each direction, extend it until index is occupied or off the board
                for possible_move in count(index + direction, direction):
                    # str at index
                    pos = self.board[possible_move]
                    # if str is " " or UPPERCASE, stop.
                    if pos.isspace() or pos.isupper():
                        break
                    # pawn movement (cause pawns are so annoying to code)
                    if piece == "P":
                        # forward movement
                        # if any space is occupied, stop.
                        if direction in (N, N + N) and pos != ".":
                            break
                        # if pawn is not where double move is possible, stop.
                        if (
                            direction == (N + N) 
                            and (index < (A1 + N) 
                                or self.board[index + N] != ".")
                            ):
                            break
                        # pawn diagonal take conditions.
                        if (
                            direction in (N+W, N+E)
                            and pos == "."
                            and possible_move not in (self.ep, self.kp, self.kp - 1, self.kp + 1)
                            ):
                            break
                        # promote to all iterations once pawn gets to the back rank
                        if A8 <= possible_move <= H8:
                            for promotion in "NBRQ":
                                # if self.ac == 1: yield Move(119 - index, 119 - possible_move, promotion)
                                # else: yield Move(index, possible_move, promotion)
                                yield Move(index, possible_move, promotion)
                            break
                    # if all the tests pass, then move the piece.
                    # if self.ac == 1: yield Move(119 - index, 119 - possible_move, "")
                    # else: yield Move(index, possible_move, "")
                    yield Move(index, possible_move, "")
                    # stop sliding
                    if piece in "PNK" or pos.islower():
                        break
                    # castling
                    if index == A1 and self.board[possible_move + E] == "K" and ("Q" in self.cr):
                        yield Move(possible_move + E, possible_move + W, "")
                    if index == H1 and self.board[possible_move + W] == "K" and ("K" in self.cr):
                        yield Move(possible_move + W, possible_move + E, "")

    def move(self, move):
        '''
        Performs the move of a piece from one index to another
        '''
        # initialize values
        start, end, promotion = move
        piece_start = self.board[start]
        board = self.board # copies value
        score = self.value + self.points(move)
        
        # reset all the values
        ac = 0 if self.ac == 1 else 1
        castling_rights = self.cr
        en_passant, king_passant = 0, 0
        
        # move the piece
        board = insert(board, end, piece_start)
        board = insert(board, start, ".")
        
        # castling -
        # if we move our rook
        if start == A1: castling_rights = self.cr.replace("Q", "")
        if start == H1: castling_rights = self.cr.replace("K", "")
        # if we capture opponent's rook
        if end == A8: castling_rights = self.cr.replace("k", "")
        if end == H8: castling_rights = self.cr.replace("q", "")
        # if king moves
        if piece_start == "K":
            castling_rights = self.cr.replace("Q", "").replace("K", "")
            # sets king passant square
            if abs(end - start) == 2:
                kp = (start + end) // 2
                board = insert(board, A1 if end < start else H1, ".")
                board = insert(board, kp, "R")
        
        # pawn movement, promotion and en passant
        if piece_start == "P":
            if A8 <= end <= H8:
                board = insert(board, end, promotion)
            if (end + S) == (start + N):
                en_passant = start + N
            if end == self.ep:
                # takes en passant square
                board = insert(board, self.ep + S, ".")
        
        # returns rotated board
        return BoardState(board, score, ac, castling_rights, en_passant, king_passant).rotate()

    def rotate(self, nullmove = False):
        '''
        Rotates the board, negates the score, keeps the castling rights,
        and preserves en passant and king passant
        '''
        ep = 119 - self.ep if self.ep and not nullmove else 0
        kp = 119 - self.kp if self.kp and not nullmove else 0
        return BoardState(self.board[::-1].swapcase(), -self.value, self.ac, self.cr, ep, kp)

    def points(self, move) -> int:
        '''
        Score the value of the move
        '''
        start, end, promotion = move
        p_start, p_end = self.board[start], self.board[end]

        # finds move in the pst boards
        value = PIECE_SQUARE_TABLES[p_start][end] - PIECE_SQUARE_TABLES[p_start][start]

        # captures a piece
        if p_end.islower():
            value += PIECE[p_end.upper()]
        
        # checks if castled
        if abs(end - self.kp) < 2:
            value += PIECE_SQUARE_TABLES["K"][119 - end]
    
        # castle
        if p_start == "K" and abs(start - end) == 2:
            value += PIECE_SQUARE_TABLES["R"][(start + end) // 2]
            value -= PIECE_SQUARE_TABLES["R"][A1 if end < start else H1]

        # pawn promotion and enpassant
        if p_start == "P":
            if A8 <= end <= H8:
                value += PIECE_SQUARE_TABLES[promotion][end] - PIECE_SQUARE_TABLES["P"][end]
            if end == self.ep:
                value += PIECE_SQUARE_TABLES["P"][119 - (end + S)]

        return value