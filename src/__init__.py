import tkinter as tk
import chessboard, GUI

def main(state):
    root = tk.Tk()
    root.title("Chessboard")
    root.configure(background = "#454440") # background
    GUI.GUI(root, state)
    root.mainloop()

if __name__ == "__main__":
    state = chessboard.BoardState(chessboard.INITIAL_STATE.board,
                                chessboard.INITIAL_STATE.value,
                                chessboard.INITIAL_STATE.ac,
                                chessboard.INITIAL_STATE.cr,
                                chessboard.INITIAL_STATE.ep,
                                chessboard.INITIAL_STATE.kp)
    main(state)