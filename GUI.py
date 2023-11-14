import tkinter as tk
import chessboard
from copy import deepcopy
from PIL import Image, ImageTk

class GUI:

    # constants
    BOARD_SIZE = 8
    SQUARE_SIZE = 64
    COLOR1 = "#CBAC79"
    COLOR2 = "#8B603D"
    HIGHLIGHT_COLOR = "#A87A30"

    # variables
    selected_piece = None
    focused = None
    available_moves = []
    images = {}

    def __init__(self, parent, state) -> None:
        '''
        Constructor.
        '''
        # initializes the variables
        self.state = state
        self.parent = parent
        self.icolor = self.state.ac

        # Kings class
        self.kings = Kings(self.state, self.state.ac)

        # initializes canvas
        canvas_width = self.SQUARE_SIZE * self.BOARD_SIZE
        canvas_height = self.SQUARE_SIZE * self.BOARD_SIZE
        self.canvas = tk.Canvas(parent, width=canvas_width, height=canvas_height)
        self.canvas.pack(padx = self.SQUARE_SIZE, pady = self.SQUARE_SIZE)

        # draws board and pieces
        self.draw_board()
        self.draw_pieces()

        # adds click listener
        self.canvas.bind("<Button-1>", self.square)

    def square(self, event) -> None:
        '''
        Gets the square clicked and either moves a piece
        or selects the piece, revealing the available moves
        '''
        # initializes the values
        selected_col = int(event.x / self.SQUARE_SIZE)
        selected_row = 7 - int(event.y / self.SQUARE_SIZE)

        # grabs the index from row and col
        pos = self.state.alpha_notation(selected_row, selected_col)
        # handles opponent's turn
        pos = self.handle_opponent(pos) if self.icolor == 1 else pos

        # if selected_piece exists, move it and reset variables
        if self.selected_piece:
            # move the piece
            self.step(self.selected_piece, pos)
            self.selected_piece = None
            self.focused = None
        self.focus(pos)
        self.draw_board()

    def step(self, start, end) -> None:
        '''
        Moves a piece graphically and sets new state from movement
        '''
        end = self.handle_opponent(end) if self.icolor == 1 else end
        # find corresponding move in list of available moves
        for move in self.available_moves:
            if end == move.end and start == move.start:

                if ((chessboard.A8 <= end <= chessboard.H8 or chessboard.A1 <= end <= chessboard.H1)
                    and self.state.board[self.selected_piece].upper() == "P"):
                    # if pawn move is a promotion move
                    # TODO: figure out how to select between promotion types
                    self.state = self.state.move(chessboard.Move(start, end, "Q"))
                    self.draw_pieces()
                    break
                
                # if after move made the king is still in check, don't allow
                if self.in_check_after_move(move):
                    break

                # set state to new move and handles opponent's turn
                self.state = self.state.move(chessboard.Move(self.handle_opponent(move.start), self.handle_opponent(move.end), "")) if self.icolor == 1 else self.state.move(move)

                # initialize Kings (has to be before active color switch)
                self.kings = Kings(self.state, self.icolor)

                # switch active color
                self.icolor = 0 if self.icolor == 1 else 1
                self.draw_pieces()
                break

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

    def in_check_after_move(self, move) -> bool:
        '''
        Determines whether a move by you allows for check by opponent
        '''
        # makes a copy of the state
        state = self.state
        # move that copy of the state
        state = state.move(chessboard.Move(self.handle_opponent(move.start), self.handle_opponent(move.end), "")) if self.icolor == 1 else state.move(move)
        kings = Kings(state, 0 if self.icolor == 1 else 1)
        # if, after that move, you still are in check
        return kings.in_check()

    def focus(self, pos) -> None:
        '''
        Focuses on the piece and shows all available moves
        '''
        piece = self.state.board[pos]
        # if piece is active color and is not ".", select it and
        # find all available moves according to that piece
        if piece != "." and piece.isupper():
            pos = self.handle_opponent(pos) if self.icolor == 1 else pos
            self.selected_piece = pos
            self.focused = [self.to_row_col(pos)]
            # finds all moves in available_moves 
            # that correspond to the piece
            for move in self.available_moves:
                if move.start == pos:
                    self.focused.append(self.to_row_col(move.end))

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
                    self.canvas.create_rectangle(x0, y0, x1, y1, 
                                            fill = self.HIGHLIGHT_COLOR, 
                                            outline = "",
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
        self.available_moves = list(self.state.generate_moves())
        # copy the state of the game board
        chessboard = self.state.board.replace(" ", "")
        # handles opponent's turn
        chessboard = chessboard[::-1].swapcase() if self.icolor == 1 else chessboard

        for index, piece in enumerate(chessboard):
            if piece == ".": # a null space
                continue
            # grab filename
            filename = "chess_piece_icons/%s%s.png" % (piece.lower(), "white" if piece.isupper() else "black")
            row = index // 8 # from 0-7
            col = index % 8 # from 0-7
            piecename = "%s%s%s" % (piece, row, col)
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
                                    tags = (piecename, "occupied"), 
                                    anchor = tk.CENTER)

class Kings:

    def __init__(self, state, icolor) -> None:
        '''
        Constructor.
        '''
        self.state = state
        self.icolor = icolor
        for index, piece in enumerate(state.board):
            if piece == "K": 
                self.i_king = index if self.icolor == 0 else 119 - index
            if piece == "k": 
                self.o_king = index if self.icolor == 0 else 119 - index
        
        # generating moves for UPPERCASE letters
        self.available_moves = list(state.generate_moves())
        
    def in_check(self) -> bool:
        '''
        Check if own king is in check of opponent's pieces
        '''
        for x in self.available_moves:
            if self.o_king == x.end: return True
        return False


def main(state):
    '''
    Main function.
    '''
    root = tk.Tk()
    root.title("Chessboard")
    root.configure(background = "#454440") # background
    gui = GUI(root, state)
    root.mainloop()

if __name__ == "__main__":
    state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                chessboard.INITIAL_STATE.score,
                                chessboard.INITIAL_STATE.ac,
                                chessboard.INITIAL_STATE.cr,
                                chessboard.INITIAL_STATE.ep,
                                chessboard.INITIAL_STATE.kp)
    main(state)