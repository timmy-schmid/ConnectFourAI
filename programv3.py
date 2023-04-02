# SID: 500687806

from operator import itemgetter
import statistics
from functools import lru_cache
import threading

'''
Bitboard Representation of board
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


def convert_state_to_player_pos(turn, contents):
    red_state, yel_state = '', '',
    rows = contents.split(',')
    for i in range(6, -1, -1):

        # add auxilary row for bitwise manipulation
        red_state += '0'
        yel_state += '0'

        # setup states for the overall board and current player (us)
        for j in range(5, -1, -1):
            if rows[j][i] == '.':
                red_state += '0'
                yel_state += '0'
            elif rows[j][i] == 'r':
                red_state += '1'
                yel_state += '0'
            elif rows[j][i] == 'y':
                red_state += '0'
                yel_state += '1'

    red_state = int(red_state, 2)
    yel_state = int(yel_state, 2)

    if turn == 'r':
        return red_state, yel_state # own_board, enemy_board
    else:
        return yel_state, red_state # own_board, enemy_board


@lru_cache(maxsize=2000000)
def get_num_set_bits(n: int):   # " Brian Kernighan's Algorithm "
    c = 0
    while n > 0:
        n &= (n-1)
        c += 1
    return c


# !!! Could be optimised.
@lru_cache(maxsize=2000000)
def get_col_height(board, col):
    col_values = (board >> col*7) & 63  # 63 = b0111111 i.e. values in the column.
    return get_num_set_bits(col_values) + col*7


@lru_cache(maxsize=2000000)
def make_move(board, col):
    board ^= 1 << get_col_height(board, col)
    return board


@lru_cache(maxsize=2000000)
def get_available_cols(board):
    return [i for i in range(0,7) if (board >> i*7) & 63 != 63]


@lru_cache(maxsize=2000000)
def is_winning_state(state):
    # including in a series of if takes approx 0.3x the for loop
    # Some bitshifting magic to found how many in a row we have.
    # See: https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0
    m = state & (state >> 1)
    if m & (m >> 2):
        return True

    m = state & (state >> 6)
    if m & (m >> 12):
        return True

    m = state & (state >> 7)
    if m & (m >> 14):
        return True

    m = state & (state >> 8)
    if m & (m >> 16):
        return True

    return False


def player_can_win(primary_board, secondary_board):
    cols = get_available_cols(primary_board | secondary_board)
    for c in cols:
        if is_winning_state(make_move(primary_board | secondary_board, c) ^ secondary_board):
            return True
    return False



def render_board(own_board, enemy_board):
    print('+===============+')
    for i in range(6, -1, -1):
        print('| ', end="")
        for j in range(0, 7):
            cur = (i + j * 7)
            if own_board & (1 << cur):
                print('O ', end='')
            elif enemy_board & (1 << cur):
                print('E ', end='')
            else:
                print('. ', end='')

        print('|')
    print('+===============+')


@lru_cache(maxsize=2000000)
def evaluate_score(depth, o_board, e_board, is_maximiser, return_best_move, alpha=-1000000, beta=1000000):

    if is_maximiser:
        if is_winning_state(o_board):
            return 1
    elif is_winning_state(e_board):
        return -1

    if (get_num_set_bits(o_board | e_board)) >= 42:
        return 0

    cols = get_available_cols(o_board | e_board)
    best_minmax_move = 0

    for i, c in enumerate(cols):
        if is_maximiser:
            # if it would make a loss...
            new_board = make_move(o_board | e_board, c) ^ e_board
            render_board(new_board, e_board)
            if player_can_win(e_board, o_board):    # reversed because it's the next turn
                max_score = -1
            else:
                max_score = evaluate_score(depth + 1, new_board, e_board, False, False, alpha, beta)
            if max_score > alpha:
                alpha, best_minmax_move = max_score, c
            print(max_score)
        else:
            new_board = make_move(o_board | e_board, c) ^ o_board
            #print("min")
            #render_board(o_board, new_board)
            if player_can_win(o_board, e_board):    # reversed because it's the next turn
                min_score = 1
            else:
                min_score = evaluate_score(depth + 1, o_board, new_board, True, False, alpha, beta)
            if min_score < beta:
                beta, best_minmax_move = min_score, c

        if beta <= alpha:
            break

    if return_best_move:
        if is_maximiser:
            return alpha, best_minmax_move
        return beta, best_minmax_move
    else:
        if is_maximiser:
            return alpha
        return beta






def run_simulation(own_board, enemy_board, current_turn):
    score, best_move = evaluate_score(0, own_board, enemy_board, current_turn, True)
    print(score, best_move)


if __name__ == '__main__':
    import timeit
    analysed_moves = 0
    #own_board, enemy_board = convert_state_to_player_pos('r', "r..y..r,r..y..r,......r,.......,.......,.......")
    own_board, enemy_board = convert_state_to_player_pos('r', "rrryyyr,yyyrrry,rrryyyr,yyy..rr,.......,.......")
    render_board(own_board, enemy_board)
    if get_num_set_bits(own_board|enemy_board) < 42 and \
            not is_winning_state(own_board) and \
            not is_winning_state(enemy_board): # i.e. board isn't full
        x = run_simulation(own_board, enemy_board, True)
        #own_board = make_move(own_board | enemy_board, 3) ^ enemy_board
        #render_board(own_board, enemy_board)

    else:
        print("State is either already full or a player has already won.")
    #render_board(own_board, enemy_board)







# See:
# http://www.informatik.uni-trier.de/~fernau/DSL0607/Masterthesis-Viergewinnt.pdf