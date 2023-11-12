import tkinter as tk
import chessboard
from PIL import Image, ImageTk

class GUI:

    # constants
    BOARD_SIZE = 8
    SQUARE_SIZE = 64
    COLOR1 = "#CBAC79"
    COLOR2 = "#8B603D"
    HIGHLIGHT_COLOR = "#A87A30"

    # variables
    available_moves = None
    selected_piece = None
    focused = None
    images = {}

    def __init__(self, parent, state):
        '''
        Constructor.
        '''
        # initializes the variables
        self.state = state
        self.parent = parent

        # initializes canvas
        canvas_width = self.SQUARE_SIZE * self.BOARD_SIZE
        canvas_height = self.SQUARE_SIZE * self.BOARD_SIZE
        self.canvas = tk.Canvas(parent, width=canvas_width, 
                                height=canvas_height)
        self.canvas.pack(padx = self.SQUARE_SIZE, pady = self.SQUARE_SIZE)
        self.draw_board()
        self.canvas.bind("<Button-1>", self.square_clicked)

    def square_clicked(self, event):
        '''
        Gets the square clicked and either moves a piece
        or selects the piece, revealing the available moves
        '''
        # initializes the values
        selected_col = int(event.x / self.SQUARE_SIZE)
        selected_row = 7 - int(event.y / self.SQUARE_SIZE)

        # grabs the index from row and col
        pos = self.state.alpha_notation(selected_row, selected_col)

        # if selected_piece exists, move it and reset variables
        if self.selected_piece:
            # move the piece
            self.step(self.selected_piece, pos)
            self.selected_piece = None
            self.focused = None
            # reset board graphics
            self.draw_pieces()
        self.focus(pos)
        self.draw_board()

    def step(self, start, end):
        '''
        Moves a piece graphically and sets new state from movement
        '''
        for move in self.available_moves:
            if end == move.end and start == move.start:
                self.state = self.state.move(move)
                break

    def focus(self, pos):
        '''
        Focuses on the piece and shows all available moves
        '''
        piece = self.state.board[pos]
        # if piece is active color and is not ".", select it and
        # find all available moves according to that piece
        if piece != "." and piece.isupper():
            self.selected_piece = pos
            self.focused = []
            self.move_indexes = []
            # finds all moves in available_moves 
            # that correspond to the piece
            for move_index, move in enumerate(self.available_moves):
                if move.start == pos:
                    # move_indexes should grow at same rate as focused does
                    self.move_indexes.append(move_index)
                    self.focused.append(self.to_row_col(move.end))

    def to_row_col(self, index):
        '''
        Helper function to transform index into row and col
        returns tuple
        '''
        return ((index // 10) - 2, (index % 10) - 1)

    def draw_board(self):
        '''
        Draws the base chess board.
        '''
        # generates the list of available 
        # moves everytime the function is called
        self.available_moves = list(self.state.generate_moves())
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
                if (self.focused is not None and (row, col) in self.focused):
                    self.canvas.create_rectangle(x0, y0, x1, y1, 
                                            fill = self.HIGHLIGHT_COLOR, 
                                            outline = "",
                                            tags = "area")
                else:
                    self.canvas.create_rectangle(x0, y0, x1, y1, 
                                            fill = color, 
                                            outline = "",
                                            tags = "area")
        # in order that pieces show in front of squares
        self.canvas.tag_raise("occupied")
        self.canvas.tag_lower("area")

    def draw_pieces(self):
        '''
        Draws the pieces onto the chessboard
        '''
        self.canvas.delete("occupied")
        chessboard = self.state.board.replace(" ", "")
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

def main(state):
    root = tk.Tk()
    root.title("Chessboard")
    root.configure(background = "#454440") # background
    gui = GUI(root, state)
    gui.draw_board()
    gui.draw_pieces()
    root.mainloop()

if __name__ == "__main__":
    state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                chessboard.INITIAL_STATE.score,
                                chessboard.INITIAL_STATE.cr,
                                chessboard.INITIAL_STATE.ep,
                                chessboard.INITIAL_STATE.kp)
    main(state)