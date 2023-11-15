from chessboard import PIECE
from collections import namedtuple

######################################

Entry = namedtuple("Entry", "lower upper")
# a data struct for upper and lower bounds
# lower <= score of position <= upper

MATE_LOWER_BOUND = PIECE["K"] - 10 * PIECE["Q"]
MATE_UPPER_BOUND = PIECE["K"] + 10 * PIECE["Q"]
QS = 40
QS_A = 140
EVAL_ROUGHNESS = 15

#######################################

class Bot:

    def __init__(self) -> None:
        self.nodes = 0
        self.history = set()
        self.transposition_score = {}
        self.transposition_move = {}
        
    def bound(self, state, gamma, depth, null = True):
        '''
        An upper and lower bound function
        '''
        self.nodes += 1

        # to make sure we still have a king
        if -MATE_LOWER_BOUND > state.value:
            # the other side has won
            return -MATE_UPPER_BOUND

        # if we've looked at this position before, revoke and return
        entry = self.transposition_score.get(
            (state, depth, null), 
            Entry(-MATE_UPPER_BOUND, MATE_UPPER_BOUND)
        )
        if entry.lower >= gamma:
            return entry.lower
        if entry.upper < gamma:
            return entry.upper
        
        # don't repeat positions
        if null and depth > 0 and state in self.history:
            return 0
        
        def moves():
            '''
            Generates the moves and prunes the branches 
            '''
            if depth > 2 and null and abs(state.value) < 500:
                yield None, -self.bound(state.rotate(nullmove=True), 1 - gamma, depth - 3)

            # if depth is 0, then do nothing
            if depth == 0:
                yield None, state.value

            # look for strongest move from the last move
            strongest = self.transposition_move.get(state)

            # if strongest move does not exist, then find one with a shallower search
            if not strongest and depth > 2:
                self.bound(state, gamma, depth - 3, null = False)
                strongest = self.transposition_move.get(state)

            val_lower = QS - depth * QS_A
            # if strongest move exists and has a higher value than the lower bound, return strongest move
            if strongest and state.points(strongest) >= val_lower:
                yield strongest, -self.bound(state.move(strongest), 1 - gamma, depth - 1)

            for val, move in sorted(
                ((state.points(m), m) for m in state.generate_moves()), 
                reverse=True
                ):
                # quiescent searching
                if val < val_lower:
                    break
                # takes the good branches
                if depth <= 1 and state.value + val < gamma:
                    yield move, state.value + val if val < MATE_LOWER_BOUND else MATE_UPPER_BOUND
                    break
                # recursively iterates through, with one less depth
                # negative bound because it switches turns
                yield move, -self.bound(state.move(move), 1 - gamma, depth - 1)

        # sets best as an extremely low value and adjust best as a better score is found
        best = -MATE_UPPER_BOUND
        for move, score in moves():
            best = max(best, score)
            if best >= gamma:
                # save the move if is better than gamma
                if move is not None:
                    self.transposition_move[state] = move
                break

        # stalemate
        if depth > 2 and best == -MATE_UPPER_BOUND:
            flipped = state.rotate(nullmove = True)
            in_check = self.bound(flipped, MATE_UPPER_BOUND, 0) == MATE_UPPER_BOUND
            best = -MATE_LOWER_BOUND if in_check else 0

        # set values of the transposition_score to look up later
        if best >= gamma:
            self.transposition_score[state, depth, null] = Entry(best, entry.upper)
        if best < gamma:
            self.transposition_score[state, depth, null] = Entry(entry.lower, best)

        return best
        
    def search(self, history):
        '''
        iterative deepening search
        '''
        self.nodes = 0
        self.history = set(history)
        self.transposition_score.clear()

        gamma = 0
        # we cap the depth range at 1000 so that we don't head off into infinity
        for depth in range(1, 1000):
            # sets upper and lower bounds
            lower, upper = -MATE_LOWER_BOUND, MATE_LOWER_BOUND
            while lower < upper - EVAL_ROUGHNESS:
                # grabs the score
                score = self.bound(history[-1], gamma, depth, null = False)
                # sets score if higer or lower than gamma
                if score >= gamma:
                    lower = score
                if score < gamma:
                    upper = score
                # results of depth returned
                yield self.nodes, depth, gamma, score, self.transposition_move.get(history[-1])
                # sets gamma for next depth
                gamma = (lower + upper + 1) // 2