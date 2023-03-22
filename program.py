#SID: 500687806

'''
UTILITY(state):
	if red is winner:
		return 10000
	if yellow is winner
		return -10000

EVALUATION(state):
	return SCORE(state, red player) – SCORE(state, yellow player)

SCORE(state, player):
	return number of tokens of player’s colour +
		10 * NUM_IN_A_ROW(2, state, player) +
		100 * NUM_IN_A_ROW(3, state, player) +
		1000 * NUM_IN_A_ROW(4 or more, state, player)

NUM_IN_A_ROW(count, state, player):
	returns the number of times that <state> contains a <count>-in-a-row
for the given <player>
'''


'''
https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0
Bitboard Representation of state

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

HEIGHT = 6
WIDTH = 7

class Board:
    def __init__(self):
        self.col_pos = [0]*WIDTH
        self.cur_player_state = b''
        self.board_state = b''
        self.moves_made = 0


def convert_state_to_player_pos(turn, contents):

    board = Board()
    
    cur_player_state, board_state = '', ''
    

    rows = contents.split(',')

    for i in range (0,WIDTH):
        col_pos_found = False
        for j in range(0,HEIGHT):
            if rows[j][i] == '.':
                if not col_pos_found: 
                    board.col_pos[i] = j
                    col_pos_found = True
                cur_player_state += '0'
                board_state += '0'
            elif rows[j][i] == turn:
                cur_player_state += '1'
                board_state += '1'

            else:
                cur_player_state += '0'
                board_state += '1'
            
        #add auxilary row for bitwise manipulation
        cur_player_state += '0'
        board_state += '0'

    board.cur_player_state = int(cur_player_state,2)
    board.board_state = int(board_state,2)
    board.moves_made = board.board_state.bit_count()

    return board

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7


def evaluation(board):

    opponent = board.cur_player_state ^ board.board_state

    return score(board.cur_player_state) - score(opponent)


def score(pos):
    four_in_row = num_in_row(4,pos)
    three_in_row = num_in_row(3,pos) - 2*four_in_row
    two_in_row = num_in_row(2,pos) - 3*four_in_row - 2*three_in_row
    return pos.bit_count() + 10*two_in_row + 100*three_in_row + 1000*four_in_row

def num_in_row(count, pos):
    total = 0
    directions = {VERTICAL,RIGHT_DIAG,LEFT_DIAG,HORIZONTAL}
    
    for dir in directions:
        m = pos
        for j in range(1,count):
            m = m & (m >> dir)
        total += m.bit_count()

    return total


def connect_four_mm(contents, turn, max_depth):

    board = convert_state_to_player_pos(turn[0],contents)

    print(board.col_pos)
    print(evaluation(board))

    return ''

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    #connect_four_mm(".ryyrry,.rryry.,..y.r..,..y....,.......,.......", "red", 4)
    connect_four_mm("..yyrrr,..ryryr,....y..,.......,.......,.......", "red", 4)