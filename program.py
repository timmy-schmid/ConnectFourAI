#SID: 500687806

from operator import itemgetter

log_enabled = False

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7

RED = 0
YEL = 1

MAX_EVAL = 10000
MIN_EVAL = -10000
class Board:
    '''
    Bitboard Representation of state.
    I chose to represent with bitboard to minimise computation of states as we
    generate so many (will help for tournament).
    Bitshifting is done at a hardware level and is super fast

    Board is represented as a bitstring with 0'th position being LSB

    |6 13 20 27 34 41 48| <- Auxilary Row
    +===================+
    |5 12 19 26 33 40 47|
    |4 11 18 25 32 39 46|
    |3 10 17 24 31 38 45|
    |2  9 16 23 30 37 44|
    |1  8 15 22 29 36 43|
    |0  7 14 21 28 35 42|
    +===================+
    '''
    def __init__(self):

        self.height = 6
        self.width = 7

        self.col_height = [0]*self.width
        self.moves_made = 0

        self.cur_player = 0
        self.our_player = 0

        self.player_states = [b'',b'']
        self.board_state = b''
        self.moves = []
        self.analysed_moves = 0

def convert_state_to_player_pos(turn, contents):

    board = Board()
    
    red_state, yel_state = '', '',

    rows = contents.split(',')
    for i in range (board.width-1,-1,-1):

        #add auxilary row for bitwise manipulation
        red_state += '0'
        yel_state += '0'

        #setup states for the overall board and current player (us)
        for j in range(board.height-1,-1,-1):
            if rows[j][i] == '.':
                board.col_height[i] = i*(board.height+1)+j
                red_state += '0'
                yel_state += '0'
            elif rows[j][i] == 'r':
                red_state += '1'
                yel_state += '0'
            elif rows[j][i] == 'y':
                red_state += '0'
                yel_state += '1'
                
    board.player_states[RED] = int(red_state,2)
    board.player_states[YEL] = int(yel_state,2)

    #calcuate board state by bitwise OR with players
    board.board_state = board.player_states[RED] | board.player_states[YEL]

    board.moves_made = bin(board.board_state).count("1")

    if turn == 'r':
        board.our_player = RED
    else:
        board.our_player = YEL

    board.cur_player = board.our_player

    return board


def make_move(board, col):
    move = 1 << board.col_height[col]
    board.col_height[col] += 1

    board.player_states[board.cur_player] ^= move
    #board.board_state ^= board.player_states[board.cur_turn]

    board.moves.append(col)
    board.moves_made+=1

    board.cur_player = not board.cur_player

def undo_move(board):
    col = board.moves.pop()
    board.moves_made-=1

    board.col_height[col] -= 1
    move = 1 << board.col_height[col]

    board.player_states[not board.cur_player] ^= move

    board.cur_player = not board.cur_player
    #board.board_state ^= board.player_states[board.cur_turn] #do we need this?


def eval(board, depth, is_maximiser):
    #check terminal state - if previous player  has made 4 in a row
    if num_in_row(4,board.player_states[not board.cur_player]):
        return MIN_EVAL if is_maximiser else MAX_EVAL

    elif depth == 0:
        return score(board.player_states[board.our_player]) - \
            score(board.player_states[not board.our_player])

def score(state):

    #Note: we subtract double counts when counting how many 2/3 in a rows there are.
    #      eg. in every 4 in a row there is 2 x three in a rows.
 
    #four_in_row = num_in_row(4,state)
    three_in_row = num_in_row(3,state) #- 2*four_in_row 
    two_in_row = num_in_row(2,state) - 2*three_in_row #3*four_in_row 
    return bin(state).count("1") + 10*two_in_row + 100*three_in_row #+ 1000*four_in_row

def num_in_row(count, state):
    total = 0
    directions = {VERTICAL,RIGHT_DIAG,LEFT_DIAG,HORIZONTAL}
    
    #Some bitshifting magic to found how many in a row we have.
    #See: https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0
    
    for dir in directions:
        m = state
        for j in range(1,count):
            m = m & (m >> dir)
        total += bin(m).count("1")

    return total

def minimax(board, depth, is_maximiser, alpha = MIN_EVAL, beta = MAX_EVAL):
    score = eval(board, depth, is_maximiser)

    if score is not None:
        return score
    
    scores = []
    for col in available_cols(board):
        make_move(board,col)
        board.analysed_moves += 1
        log_board(board,log_enabled, depth)
        score = minimax(board,depth-1,not is_maximiser, alpha, beta)
        scores.append(score)
        undo_move(board)
        if is_maximiser:
            alpha = max(alpha, score)
        else:
            beta = min(beta, score)

        if beta <= alpha:
            break

    return (max if is_maximiser else min)(scores)

def find_best_move(board,depth, alpha = -1000000, beta = 1000000):
    board.analysed_moves = 1
    log_board(board,log_enabled, depth)
    moves = []
    for col in available_cols(board):
        make_move(board,col)
        board.analysed_moves += 1
        log_board(board,log_enabled, depth)
        
        score = minimax(board,depth-1,False, alpha, beta)
        moves.append((score,col))
        undo_move(board)
        alpha = max(alpha, score)
        if beta <= alpha:
            break

        
    log_msg("Possible move evals: " + str(moves),log_enabled)
    return max(moves,key=itemgetter(0))

#returns the list of columns that are possible to play in
def available_cols(board):
    return [j for j in range(0,board.width)
            if (board.col_height[j] % 7 != 6)]

def connect_four_ab(contents, turn, max_depth):

    board = convert_state_to_player_pos(turn[0],contents)
    log_msg("STARTING BOARD",log_enabled)
    log_msg("We are playing as " + turn,log_enabled)
    best_move = find_best_move(board,max_depth)

    log_msg("------\nSummary\n------", log_enabled)
    log_msg("Running minimax at depth: " + str(max_depth),log_enabled)
    log_msg("Best Move: " + str((best_move[1])), log_enabled)
    log_msg("Score: " + str((best_move[0])), log_enabled)
    log_msg("Moves Analysed: " + str(board.analysed_moves), log_enabled)
    return str(best_move[1]) + '\n' + str(board.analysed_moves)

def log_msg(msg,enabled):
    if enabled:
        print(msg)

def log_board(board, enabled, depth):
    if enabled:
        print("-----")
        print("Move " + str(board.moves_made) + " at depth " + str(depth))
        print("Moves Analysed " + str(board.analysed_moves))
        print('+===============+')
        for i in range(board.height,-1,-1):
            print('| ', end="")
            for j in range(0,board.width):
                cur = (i + j*(board.height+1))
                if (board.player_states[RED] & (1 << cur)):
                    print('r ', end='')
                elif (board.player_states[YEL] & (1 << cur)):
                    print('y ', end='')
                else:
                    print('. ', end='')

            print('|')
        print('+===============+')

if __name__ == '__main__':
    connect_four_ab("r..y..r,r..y..r,......r,.......,.......,.......", "red", 3)