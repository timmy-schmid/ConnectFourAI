#SID: 500687806
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

        self.cur_player_state = b''
        self.cur_player_colour = ''

        self.other_player_state = b''
        self.other_player_colour = ''

        self.board_state = b''
        self.moves_made = 0

def convert_state_to_player_pos(turn, contents):

    board = Board()
    
    cur_player_state, board_state = '', ''

    rows = contents.split(',')
    for i in range (board.width-1,-1,-1):

        #add auxilary row for bitwise manipulation
        cur_player_state += '0'
        board_state += '0'

        #setup states for the overall board and current player (us)
        for j in range(board.height-1,-1,-1):
            if rows[j][i] == '.':
                board.col_height[i] = i*(board.height+1)+j
                cur_player_state += '0'
                board_state += '0'
            elif rows[j][i] == turn:
                cur_player_state += '1'
                board_state += '1'

            else:
                cur_player_state += '0'
                board_state += '1'

    board.cur_player_state = int(cur_player_state,2)
    board.board_state = int(board_state,2)

    #calcuate other player's state by XOR the main board with us
    board.other_player_state = board.cur_player_state ^ board.board_state

    board.moves_made = board.board_state.bit_count()
    board.cur_player_colour = turn

    #setup player colours (important for printing)
    if turn == 'r':
        board.other_player_colour = 'y'
    else:
        board.other_player_colour = 'r'     

    return board

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7

def make_move(board, col):
    board.cur_player_state = board.cur_player_state ^ board.board_state
    board.board_state = board.board_state | 1 << board.col_height[col]
    board.other_player_state = board.cur_player_state ^ board.board_state
    board.moves_made+=1

    #swap colours
    temp_colour = board.cur_player_colour
    board.cur_player_colour = board.other_player_colour
    board.other_player_colour = temp_colour

def evaluation(board):

    return score(board.cur_player_state) - score(board.other_player_state)


def score(pos):

    #Note: we subtract double counts when counting how many 2/3 in a rows there are.
    #      eg. in every 4 in a row there is 2 x three in a rows.
 
    four_in_row = num_in_row(4,pos)
    three_in_row = num_in_row(3,pos) - 2*four_in_row 
    two_in_row = num_in_row(2,pos) - 3*four_in_row - 2*three_in_row
    return pos.bit_count() + 10*two_in_row + 100*three_in_row + 1000*four_in_row

def num_in_row(count, pos):
    total = 0
    directions = {VERTICAL,RIGHT_DIAG,LEFT_DIAG,HORIZONTAL}
    
    #Some bitshifting magic to found how many in a row we have.
    #See: https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0
    
    for dir in directions:
        m = pos
        for j in range(1,count):
            m = m & (m >> dir)
        total += m.bit_count()

    return total

#Useful for debugging states.
def print_board(board):
    print("Move " + str(board.moves_made))
    print('+===============+')
    for i in range(board.height,-1,-1):
        print('| ', end="")
        for j in range(0,board.width):
            cur = (i + j*(board.height+1))

            if (board.cur_player_state & (1 << cur)):
                print(board.cur_player_colour + ' ', end='')
            elif (board.other_player_state & (1 << cur)):
                print(board.other_player_colour + ' ', end='')
            else:
                print('. ', end='')

        print('|')
    print('+===============+')

def connect_four_mm(contents, turn, max_depth):

    board = convert_state_to_player_pos(turn[0],contents)
    print_board(board)

    #print(board.col_height)
    make_move(board, 6)
    print_board(board)
    #print(evaluation(board))

    return ''

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    #connect_four_mm(".ryyrry,.rryry.,..y.r..,..y....,.......,.......", "red", 4)
    connect_four_mm("..yyrrr,..ryryr,....y..,.......,.......,.......", "red", 4)