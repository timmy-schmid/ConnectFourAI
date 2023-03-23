#SID: 500687806

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7

RED = 0
YEL = 1
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


def evaluation(board):
    return score(board.player_states[board.cur_player]) - \
           score(board.player_states[not board.cur_player])

def score(state):

    #Note: we subtract double counts when counting how many 2/3 in a rows there are.
    #      eg. in every 4 in a row there is 2 x three in a rows.
 
    four_in_row = num_in_row(4,state)
    three_in_row = num_in_row(3,state) - 2*four_in_row 
    two_in_row = num_in_row(2,state) - 3*four_in_row - 2*three_in_row
    return bin(state).count("1") + 10*two_in_row + 100*three_in_row + 1000*four_in_row

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

#Useful for debugging states.
def print_board(board):
    print("Move " + str(board.moves_made))
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

def min_max(board, depth):
    j,v = max_value(board,depth)
    print(j,v)

def max_value(board, depth):
    #check terminal states
    if num_in_row(4,board.player_states[not board.cur_player]):
        if board.cur_player == board.our_player:
            return -1,10000
        else:
            return -1,-10000
    elif depth == 0:
        return evaluation(board)
    v = -1000000 #make this more appropriate
    for j in range(0,board.width):
        if board.col_height[j] % 7 != 6: #check if col is full
            make_move(board,j)
            print("AFTER MOVE")
            print_board(board)
            v = max(v,min_value(board, depth-1)[1])
            print(v)
            print_board(board)
    return j,v

def min_value(board, depth):
    #check terminal states
    if num_in_row(4,board.player_states[not board.cur_player]):
        if board.cur_player == board.our_player:
            return -1,10000
        else:
            return -1,-10000
    elif depth == 0:
        return -1,evaluation(board)
    v = -1000000 #make this more appropriate
    for j in range(0,board.width):
        if board.col_height[j] % 7 != 6: #check if col is full
            make_move(board,j)
            print_board(board)
            v = max(v,max_value(board, depth-1)[1])
            undo_move(board)
    return j,v

def connect_four_mm(contents, turn, max_depth):

    board = convert_state_to_player_pos(turn[0],contents)
    print("STARTING BOARD")
    print_board(board)
    return min_max(board, max_depth)

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    #connect_four_mm(".ryyrry,.rryry.,..y.r..,..y....,.......,.......", "red", 4)
    connect_four_mm("..yyrrr,..ryryr,....y..,.......,.......,.......", "red", 1)