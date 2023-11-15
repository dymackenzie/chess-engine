import pandas as pd
import re
import string

class Openings:

    def __init__(self) -> None:
        self.openings = self.read()

    def read(self) -> list:
        '''
        Reads all 5 opening files and converts into a list of list of end moves.
        '''
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
            if len(insert) != 0 and len(insert) > 4:
                result.append(insert)
        return result

    def convert_pgn(self,pgn) -> list:
        '''
        Converts the given pgn into a list of end moves.
        '''
        list_pgn = re.split(".\\.", pgn)[1:]
        end_moves = []
        entries = []
        for x in list_pgn:
            x = x.strip()
            x = x.split(" ")
            if len(x) < 2:
                return []
            entries.append((x[0][-2:], x[1][-2:]))
        for entry in entries:
            try:
                entry = (self.convert_to_index(entry[0]), self.convert_to_index(entry[1]))
            except Exception:
                continue
            end_moves.append(entry)
        return end_moves

    def convert_to_index(self, entry) -> int:
        '''
        Converts the given entry (such as e4 or f6) into workable index
        '''
        try:
            return 91 + string.ascii_lowercase.find(entry[0]) + (int(entry[1]) * 10)
        except Exception:
            raise Exception
