import tkinter as tk
import chessboard, openings, bot
import time, random
from PIL import Image, ImageTk

#########################################

class GUI:
    '''
    The GUI class to handle all user interfaces
    '''
    BOARD_SIZE = 8
    SQUARE_SIZE = 64
    COLOR1 = "#CBAC79"
    COLOR2 = "#8B603D"
    HIGHLIGHT_COLOR = "#A87A30"
    THINK = 0.1 # in seconds

    def __init__(self, parent, state) -> None:
        # initializes the variables
        self.state = state
        self.parent = parent
        self.icolor = self.state.ac
        self.selected_piece = None
        self.focused = None
        self.available_moves = []
        self.images = {}

        # who starts first
        self.turn_start = 0 # 0 for white, 1 for black

        # initialize menu bar
        self.menu = tk.Menu(parent)
        self.filemenu = tk.Menu(self.menu, tearoff = 0)
        self.filemenu.add_command(label = "New Game as White", command = self.new_game_as_white)
        self.filemenu.add_command(label = "New Game as Black", command = self.new_game_as_black)
        self.menu.add_cascade(label = "File", menu = self.filemenu)
        self.parent.config(menu = self.menu)

        # initialize the Bot class
        self.bot = bot.Bot()

        # initalize the Openings class
        self.openings = openings.Openings().openings
        open_index = random.randint(0, len(self.openings))
        self.openings = self.openings[open_index]
        self.open_number = 5

        # initialize the Kings class
        self.kings = Kings(self.state, self.state.ac)

        # adds info frame
        self.bottom_frame = tk.Frame(parent, height = self.SQUARE_SIZE)
        self.info = tk.Label(self.bottom_frame, text = "", foreground = "#454440")
        self.info.pack(side=tk.RIGHT, padx = self.BOARD_SIZE, pady = self.BOARD_SIZE)
        self.bottom_frame.pack(fill = "x", side = tk.BOTTOM)

        # initializes canvas
        canvas_width = self.SQUARE_SIZE * self.BOARD_SIZE
        canvas_height = self.SQUARE_SIZE * self.BOARD_SIZE
        self.canvas = tk.Canvas(parent, width=canvas_width, height=canvas_height)
        self.canvas.pack(padx = self.SQUARE_SIZE, pady = self.SQUARE_SIZE)

        # draws board and pieces
        self.draw_board()
        self.draw_pieces()

        # adds click listener
        # * change function to run_AI_against_AI to see AI in action against itself
        self.canvas.bind("<Button-1>", self.on_square)

    def on_square(self, event) -> None:
        '''
        Gets the square clicked and either moves a piece
        or selects the piece, revealing the available moves
        '''
        # initializes the values
        selected_col = int(event.x / self.SQUARE_SIZE)
        selected_row = 7 - int(event.y / self.SQUARE_SIZE)

        # grabs the index from row and col
        pos = self.alpha_notation(selected_row, selected_col)
        # handles opponent's turn
        pos = self.handle_opponent(pos) if self.icolor == 1 else pos

        # if selected_piece exists, move it and reset variables
        if self.selected_piece:
            # move the piece
            try:
                self.step(self.selected_piece, pos)
            except ChessException as error:
                # print error if in check
                self.info["text"] = error.__class__.__name__
            self.selected_piece = None
            self.focused = None
        self.focus(pos)
        self.draw_board()

    def focus(self, pos) -> None:
        '''
        Focuses on the piece and shows all available moves
        '''
        piece = self.state.board[pos]
        # if piece is active color and is not ".", select it and
        # find all available moves according to that piece
        if piece != "." and piece.isupper():
            # reverts pos to handle available moves for opponent
            self.selected_piece = pos
            self.focused = [self.to_row_col(pos if self.icolor == 0 else self.handle_opponent(pos))]
            # finds all moves in available_moves 
            # that correspond to the piece
            for move in self.available_moves:
                if move.start == pos:
                    self.focused.append(self.to_row_col(move.end if self.icolor == 0 else self.handle_opponent(move.end)))

    def step(self, start, end) -> None:
        '''
        Moves a piece graphically and sets new state from movement
        '''
        # end = self.handle_opponent(end) if self.icolor == 1 else end
        # find corresponding move in list of available moves
        for move in self.available_moves:
            if end == move.end and start == move.start:
                
                # if pawn move is a promotion move
                if ((chessboard.A8 <= end <= chessboard.H8 or chessboard.A1 <= end <= chessboard.H1)
                    and self.state.board[self.selected_piece].upper() == "P"):
                    self.state = self.state.move(chessboard.Move(start, end, "Q"))
                    self.draw_pieces()
                    break

                # if self.checkmate():
                #     raise Checkmate

                # if after move made the king is in check, don't allow
                if self.in_check_after_move(move):
                    raise InCheck

                # set state to new move
                self.state = self.state.move(move)

                # initialize Kings (has to be before active color switch)
                self.kings = Kings(self.state, self.icolor)

                # switch active color
                self.icolor = 0 if self.icolor == 1 else 1

                # move bot
                try:
                    self.state = self.state.move(self.bot_recommend(self.state))
                except ChessException as error:
                    self.info["text"] = error.__class__.__name__

                # switch active color
                self.icolor = 0 if self.icolor == 1 else 1
                self.draw_pieces()
                break

    def draw_board(self) -> None:
        '''
        Draws the base chess board.
        '''
        colors = [self.COLOR1, self.COLOR2] # beige, brown
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                # calculate colors
                color = colors[(row + col) % 2]
                # calculate the position of each square
                x0, y0 = col * self.SQUARE_SIZE, row * self.SQUARE_SIZE
                x1, y1 = x0 + self.SQUARE_SIZE, y0 + self.SQUARE_SIZE
                # draws available moves if exists
                # else, draws all rectangles
                self.canvas.create_rectangle(x0, y0, x1, y1, 
                                            fill = color, 
                                            outline = "",
                                            tags = "area")
                if (self.focused is not None and (row, col) in self.focused):
                    self.canvas.create_rectangle(x0, y0, x1 - 1, y1 - 1, 
                                            fill = self.HIGHLIGHT_COLOR,
                                            outline = color,
                                            tags = "area")
        # in order that pieces show in front of squares
        self.canvas.tag_raise("occupied")
        self.canvas.tag_lower("area")

    def draw_pieces(self) -> None:
        '''
        Draws the pieces onto the chessboard
        '''
        self.canvas.delete("occupied")
        # generates the list of available 
        # moves everytime the function is called
        if self.icolor == 0: self.available_moves = list(self.state.generate_moves())
        # copy the state of the game board
        chessboard = self.state.board.replace(" ", "")
        # handles opponent's turn
        chessboard = chessboard[::-1].swapcase() if self.icolor == 1 else chessboard

        # visualize the chesboard 
        for index, piece in enumerate(chessboard):
            if piece == ".": # a null space
                continue
            # grab filename
            if self.turn_start == 0: filename = "chess_piece_icons/%s%s.png" % (piece.lower(), "white" if piece.isupper() else "black")
            else: filename = "chess_piece_icons/%s%s.png" % (piece.lower(), "black" if piece.isupper() else "white")
            row = index // 8 # from 0-7
            col = index % 8 # from 0-7
            # check if filename is already instantiated
            if filename not in self.images:
                raw_image = Image.open(filename)
                resize_image = raw_image.resize((self.SQUARE_SIZE, self.SQUARE_SIZE))
                self.images[filename] = ImageTk.PhotoImage(resize_image)
            # coords for the image and move it to coordinate
            x0 = (col * self.SQUARE_SIZE) + int(self.SQUARE_SIZE / 2)
            y0 = (row * self.SQUARE_SIZE) + int(self.SQUARE_SIZE / 2)
            # generate image at 0,0
            self.canvas.create_image(x0, y0, image = self.images[filename], 
                                    tags = "occupied", 
                                    anchor = tk.CENTER)

    ########################################

    # TODO:
    def opening_move(self) -> None:
        return

    def bot_recommend(self, state) -> object:
        '''
        Run the bot on the given state to recommend the best move
        '''
        init_time = time.time()
        best_move = None
        for nodes, depth, gamma, score, move in self.bot.search([state]):
            if score >= gamma:
                if move is None:
                    raise Checkmate
                # assign best move
                best_move = chessboard.Move(move.start, move.end, move.promote)
                self.info["text"] = ("depth:", depth, "positions:", nodes)
            # controls how long the bot will think for
            if best_move and time.time() - init_time > self.THINK * 0.8:
                print(time.time() - init_time)
                break
        return best_move

    def in_check_after_move(self, move) -> bool:
            '''
            Determines whether a move by you allows for check by opponent
            '''
            # makes a copy of the state
            state = self.state
            # move that copy of the state
            state = state.move(move)
            kings = Kings(state, 0 if self.icolor == 1 else 1)
            # if, after that move, you still are in check
            return kings.in_check()

    def checkmate(self) -> bool:
        '''
        Determines if king is in checkmate
        '''
        checkmate = True
        for move in self.available_moves:
            if not self.in_check_after_move(move):
                checkmate = False
        return checkmate

    ########################################    

    def new_game_as_white(self) -> None:
        '''
        Restarts the game and begins as white.
        '''
        self.state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                        chessboard.INITIAL_STATE.value,
                                        chessboard.INITIAL_STATE.ac,
                                        chessboard.INITIAL_STATE.cr,
                                        chessboard.INITIAL_STATE.ep,
                                        chessboard.INITIAL_STATE.kp)
        # reset variables
        self.turn_start = 0
        self.selected_piece = None
        self.focused = None
        self.available_moves = []

        # openings
        open_index = random.randint(0, len(self.openings))
        self.openings = self.openings[open_index]
        self.open_number = 5

        self.draw_board()
        self.draw_pieces()

    def new_game_as_black(self) -> None:
        '''
        Begins new game as black and has the bot move first.
        '''
        self.state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                        chessboard.INITIAL_STATE.value,
                                        chessboard.INITIAL_STATE.ac,
                                        chessboard.INITIAL_STATE.cr,
                                        chessboard.INITIAL_STATE.ep,
                                        chessboard.INITIAL_STATE.kp)
        print(self.state)
        # reset variables
        self.turn_start = 1
        self.selected_piece = None
        self.focused = None
        self.available_moves = []

        # openings
        open_index = random.randint(0, len(self.openings))
        self.openings = self.openings[open_index]
        self.open_number = 4

        # bot moves first as white
        self.state = self.state.move(self.bot_recommend(self.state))

        self.draw_board()
        self.draw_pieces()

    def run_AI_against_AI(self, event) -> None:
        '''
        Runs the bot against itself.
        '''
        try:
            self.state = self.state.move(self.bot_recommend(self.state))
            self.icolor = 0 if self.icolor == 1 else 1
            self.state = self.state.move(self.bot_recommend(self.state))
            self.icolor = 0 if self.icolor == 1 else 1
        except ChessException as error:
            self.info["text"] = error.__class__.__name__
        self.draw_board()
        self.draw_pieces()

    # TODO:
    # def initialize_opening_moves(self) -> list:
    #     for move in self.available_moves:
    #         if move.end 

    def handle_opponent(self, index) -> int:
        '''
        Helper function to handle opponent index
        '''
        return 119 - index

    def to_row_col(self, index) -> tuple:
        '''
        Helper function to transform index into row and col
        returns tuple
        '''
        return ((index // 10) - 2, (index % 10) - 1)
    
    def alpha_notation(self, row, col) -> int:
        '''
        Converts row and column into index number
        '''
        if row < 0 or row > 7 or col < 0 or col > 7: 
            return -1
        return chessboard.A1 + (chessboard.N * row) + (chessboard.E * col)

#########################################

class Kings:
    '''
    Class to keep track of king position and check status
    '''
    def __init__(self, state, icolor) -> None:
        self.state = state
        self.icolor = icolor
        for index, piece in enumerate(state.board):
            if piece == "K":
                self.i_king = index
            if piece == "k": 
                self.o_king = index
        
        # generating moves for UPPERCASE letters
        self.available_moves = list(state.generate_moves())
        
    def in_check(self) -> bool:
        '''
        Check if own king is in check of opponent's pieces
        '''
        for x in self.available_moves:
            if self.o_king == x.end: return True
        return False

class ChessException(Exception): pass

class InCheck(ChessException): pass

class Checkmate(ChessException): pass

#########################################

def main(state):
    root = tk.Tk()
    root.title("Chessboard")
    root.configure(background = "#454440") # background
    gui = GUI(root, state)
    root.mainloop()

if __name__ == "__main__":
    state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                chessboard.INITIAL_STATE.value,
                                chessboard.INITIAL_STATE.ac,
                                chessboard.INITIAL_STATE.cr,
                                chessboard.INITIAL_STATE.ep,
                                chessboard.INITIAL_STATE.kp)
    main(state)