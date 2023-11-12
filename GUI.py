import tkinter as tk
from chessboard import *
from PIL import Image, ImageTk

class GUI:
    # constants
    BOARD_SIZE = 8
    SQUARE_SIZE = 64
    COLOR1 = "#CBAC79"
    COLOR2 = "#8B603D"

    # variables
    selected_piece = None
    focused = None
    images = {}
    piece_images = {
        Piece.WHITE.value + Piece.PAWN.value : 'pwhite',        Piece.WHITE.value + Piece.ROOK.value : 'rwhite', 
        Piece.WHITE.value + Piece.KNIGHT.value : 'nwhite',    Piece.WHITE.value + Piece.BISHOP.value : 'bwhite', 
        Piece.WHITE.value + Piece.QUEEN.value : 'qwhite',      Piece.WHITE.value + Piece.KING.value : 'kwhite',
        Piece.BLACK.value + Piece.PAWN.value : 'pblack',        Piece.BLACK.value + Piece.ROOK.value : 'rblack', 
        Piece.BLACK.value + Piece.KNIGHT.value : 'nblack',    Piece.BLACK.value + Piece.BISHOP.value : 'bblack', 
        Piece.BLACK.value + Piece.QUEEN.value : 'qblack',      Piece.BLACK.value + Piece.KING.value : 'kblack'
    }

    def __init__(self, parent, chessboard):
        # constructor
        self.chessboard = chessboard
        self.parent = parent

        canvas_width = self.SQUARE_SIZE * self.BOARD_SIZE
        canvas_height = self.SQUARE_SIZE * self.BOARD_SIZE
        self.canvas = tk.Canvas(parent, width=canvas_width, 
                                height=canvas_height)
        self.canvas.pack(padx = self.SQUARE_SIZE, pady = self.SQUARE_SIZE)
        self.draw_board()
        #self.canvas.bind("<Button-1>", self.square_clicked)

    # function to draw the chess board
    def draw_board(self):    
        colors = [self.COLOR1, self.COLOR2] # beige, brown
        for row in range(self.BOARD_SIZE):
            for col in range(self.BOARD_SIZE):
                # calculate colors
                color = colors[(row + col) % 2]
                # calculate the position of each square
                x0, y0 = col * self.SQUARE_SIZE, row * self.SQUARE_SIZE
                x1, y1 = x0 + self.SQUARE_SIZE, y0 + self.SQUARE_SIZE
                self.canvas.create_rectangle(x0, y0, 
                                            x1, y1, 
                                            fill = color, 
                                            outline = "",
                                            tags = "area")
        # in order that pieces show in front of squares
        self.canvas.tag_raise("occupied")
        self.canvas.tag_lower("area")

    def draw_pieces(self):
        self.canvas.delete("occupied")
        for index, piece in enumerate(chessboard):
            if piece == 0: # a null space
                continue
            # grab filename
            filename = "chess_piece_icons/%s.png" % self.piece_images.get(int(piece))
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
            self.canvas.coords(piecename, x0, y0)

def main():
    root = tk.Tk()
    root.title("Chessboard")
    root.configure(background = "#454440") # background
    #load_fen_position()
    gui = GUI(root, chessboard)
    gui.draw_board()
    gui.draw_pieces()
    root.mainloop()


if __name__ == "__main__":
    # game = chessboard.Board()
    # main(game)
    main()