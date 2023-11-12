import time, math, string
from itertools import count
from collections import namedtuple, defaultdict
from constants import *

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

# here, we take both the piece values and the piece-square tables and combine them
# we also pad the table with two 0s on all sides for easier illegal-move catches
for k, table in PIECE_SQUARE_TABLES.items():
    padrow = lambda row: (0,) + tuple(x + PIECE[k] for x in row) + (0,)
    PIECE_SQUARE_TABLES[k] = sum((padrow(table[i * 8 : i * 8 + 8]) for i in range(8)), ())
    PIECE_SQUARE_TABLES[k] = (0,) * 20 + PIECE_SQUARE_TABLES[k] + (0,) * 20

##############################################

STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq -"

# initializes data structure for initial state
State = namedtuple("State", "board active wc bc ep kp")
# board - 120 char representation of the board
# active - active color
# wc - white castling rights, UPPERCASE
# bc - black castling rights, lowercase
# ep - en passant square
# kp - the king passant square

# initializes data structure for initial state
Move = namedtuple("Move", "start end promote")
# start - starting index
# end - end index
# promote - if there is a promotion event

def load_from_fen(initial_state):
    '''
    Takes the tuple of initial state and assigns FEN values to it.
    '''
    # all the data from the FEN string
    fen_split = STARTING_FEN.split(' ')
    initial_state = initial_state._replace(active = fen_split[1])
    # extract UPPERCASE letters from castling_rights
    initial_state = initial_state._replace(wc = ''.join(c for c in fen_split[2] if c.isupper()))
    # extract lowercase letters from castling_rights
    initial_state = initial_state._replace(bc = ''.join(c for c in fen_split[2] if c.islower()))

    # convert enpassant square from standard notation into index
    ep_notation = fen_split[3]
    if ep_notation != "-":
        initial_state = initial_state._replace(A1 + string.ascii_lowercase.index(ep_notation[0]) + (ep_notation[1] * 10))

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
                place_piece = lambda board, i, p: board[:i] + p + board[i + 1 :]
                raw_board = place_piece(raw_board, board_index, x)
                board_index += 1

    # initialize padded rows board
    padded_rows_board = ""
    # pad the board with two 0s deep on each side
    padrow = lambda row: " " + row + " "
    for i in range(8):
        padded_rows_board += padrow(raw_board[i * 8 : i * 8 + 8])
    # pad the rows with an " " on each side
    raw_board = " " * 20 + padded_rows_board + " " * 20
    initial_state = initial_state._replace(board = raw_board)

    return initial_state # returns modified namedtuple

INITIAL_STATE = load_from_fen(State('board', 'active', 'wc', 'bc', 'ep', 'kp')) # values will be replaced by function

############################################

class BoardState(State):
    
    def generate_moves(self):
        '''
        Returns (piece index, list of available moves) for all indexes.
        '''
        # index is initial position
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
                                yield Move(index, possible_move, promotion)
                            break
                    # if all the tests pass, then move the piece.
                    yield Move(index, possible_move, "")
                    # stop sliding
                    if piece in "PNK" or pos.islower():
                        break
                    # castling
                    if index == A1 and self.board[possible_move + E] == "K" and ("K" in self.wc):
                        yield Move(possible_move + E, possible_move + W, "")
                    if index == H1 and self.board[possible_move + W] == "K" and ("Q" in self.wc):
                        yield Move(possible_move + W, possible_move + E, "")
