from chessboard import PIECE

MATE_LOWER_BOUND = PIECE["K"] - 10 * PIECE["Q"]
MATE_UPPER_BOUND = PIECE["K"] + 10 * PIECE["Q"]

class Bot:

    def __init__(self) -> None:
        self.nodes          = 0
        self.state          = None
        self.variated_moves = {}
        
    def alphabeta(self, state, g, depth):
        ''' an alphabeta function designed for recursively going through every possible
         chess move and finding the best move '''
        
        # to make sure we still have a king
        if -MATE_LOWER_BOUND > state.value:
            # the other side has won
            return -MATE_UPPER_BOUND
        
        self.nodes += 1
        v_low = 40 - depth * 140
        
        def strongest_move():

            # look for strongest move from the last move
            strongest_move = self.variated_moves.get(state)

            if not strongest_move and depth > 2:
                self.alphabeta(state, g, depth - 3)
                strongest_move = self.variated_moves.get(state)

            if strongest_move and state.points(strongest_move) >= v_low:
                # recursively iterates through, with one less depth
                # negative bound because it switches turns
                print("6yes")
                yield strongest_move, -self.alphabeta(state.move(strongest_move), 1 - g, depth - 1)
        
        def make_moves():

            # if depth is 0, then return the value
            if depth == 0:
                yield None, state.value
            
            # find the strongest move
            strongest_move()

            for v, move in sorted(
                ((state.points(move), move) for move in state.generate_moves()), 
                reverse = True
                ):
                if v < v_low: break
                if depth <= 1 and state.value + v < g:
                    yield move, state.value + v if v < MATE_LOWER_BOUND else MATE_UPPER_BOUND
                    break
                # recursively iterates through, with one less depth
                # negative bound because it switches turns
                yield move, -self.alphabeta(state.move(move), 1 - g, depth - 1)

        # sets best as an extremely low value and adjust best as a better score is found
        best = -MATE_UPPER_BOUND
        for move, score in make_moves():
            best = max(best, score)
            if best >= g:
                # save the move if is better than gamma
                if move is not None:
                    self.variated_moves[state] = move
                break

        # handle draws
        if depth > 2 and best == -MATE_UPPER_BOUND:
            flipped_state = state.rotate(nullmove = True)
            is_in_check = self.alphabeta(flipped_state, MATE_UPPER_BOUND, 0) == MATE_UPPER_BOUND
            best = -MATE_LOWER_BOUND if is_in_check else 0

        return best
        
    def search(self, state):
        ''' iterative deepening search '''
        self.nodes = 0
        g = 0
        # we cap the depth range at 100 so that we don't head off into infinity
        for depth in range(1, 100):
            # sets upper and lower bounds
            lower = -MATE_LOWER_BOUND
            upper = MATE_LOWER_BOUND
            while lower < upper - 15:
                # grabs the score
                score = self.alphabeta(state, g, depth)
                # sets score if higer or lower than gamma
                if score >= g: lower = score
                if score < g: upper = score
                # results of search returned
                yield self.nodes, depth, g, score, self.variated_moves.get(state)
                g = (lower + upper + 1) // 2
