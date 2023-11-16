import pandas as pd
import re
import string
import chessboard

class Openings:

    NUM_OF_OPENINGS = 3

    def __init__(self) -> None:
        self.openings = self.read()

    def read(self) -> list:
        ''' Reads all 5 opening files and converts into a list of list of end moves. '''
        li = []
        paths = ['chess_openings/a.tsv', 'chess_openings/b.tsv', 'chess_openings/c.tsv', 'chess_openings/d.tsv', 'chess_openings/e.tsv']
        for path in paths:
            database = pd.read_csv(path, index_col = None, header = 0, sep = "\t")
            li.append(database)
        openings = pd.concat(li, axis = 0, ignore_index = True)
        all_pgn = pd.Series(openings['pgn'], dtype = pd.StringDtype())
        result = []
        for pgn in all_pgn:
            insert = self.convert_pgn(pgn)
            if len(insert) != 0 and len(insert) >= self.NUM_OF_OPENINGS:
                result.append(insert)
        return result

    def convert_pgn(self,pgn) -> list:
        ''' Converts the given pgn into a list of end moves. '''
        list_pgn = re.split(".\\.", pgn)[1:]
        end_moves = []
        entries = []
        for x in list_pgn:
            x = x.strip()
            x = x.split(" ")
            if len(x) < 2:
                return []
            entries.append((x[0][-2:], x[1][-2:]))

        def convert_to_index(entry) -> int:
            try: return chessboard.A1 + (string.ascii_lowercase.find(entry[0]) * chessboard.E) + ((int(entry[1]) - 1) * chessboard.N)
            except Exception: raise Exception

        for entry in entries:
            try:
                entry = (convert_to_index(entry[0]), 119 - convert_to_index(entry[1]))
            except Exception:
                continue
            end_moves.append(entry)
        return end_moves
