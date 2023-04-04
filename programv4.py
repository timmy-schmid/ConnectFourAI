# SID: 500687806

from operator import itemgetter
import statistics
from functools import lru_cache
import threading

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7


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
    return get_num_set_bits(col_values) + col*7 # Offset by the column


@lru_cache(maxsize=2000000)
def make_move(board, col):
    board ^= 1 << get_col_height(board, col)
    return board


@lru_cache(maxsize=2000000)
def get_available_cols(board):
    return [i for i in range(0,7) if (board >> i*7) & 63 != 63]


def column_is_playable(board, c):
    return (board >> c*7) & 32 != 32    # 32 = 0100000, i.e. returns whether or not the top bit is set.


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
    combined_board = primary_board | secondary_board
    if column_is_playable(combined_board, 0):
        if is_winning_state(make_move(combined_board, 0) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 1):
        if is_winning_state(make_move(combined_board, 1) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 2):
        if is_winning_state(make_move(combined_board, 2) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 3):
        if is_winning_state(make_move(combined_board, 3) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 4):
        if is_winning_state(make_move(combined_board, 4) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 5):
        if is_winning_state(make_move(combined_board, 5) ^ secondary_board):
            return True

    if column_is_playable(combined_board, 6):
        if is_winning_state(make_move(combined_board, 6) ^ secondary_board):
            return True

    return False


def player_can_win_get_pos(primary_board, secondary_board):
    combined_board = primary_board | secondary_board
    if column_is_playable(combined_board, 0):
        if is_winning_state(make_move(combined_board, 0) ^ secondary_board):
            return 0

    if column_is_playable(combined_board, 1):
        if is_winning_state(make_move(combined_board, 1) ^ secondary_board):
            return 1

    if column_is_playable(combined_board, 2):
        if is_winning_state(make_move(combined_board, 2) ^ secondary_board):
            return 2

    if column_is_playable(combined_board, 3):
        if is_winning_state(make_move(combined_board, 3) ^ secondary_board):
            return 3

    if column_is_playable(combined_board, 4):
        if is_winning_state(make_move(combined_board, 4) ^ secondary_board):
            return 4

    if column_is_playable(combined_board, 5):
        if is_winning_state(make_move(combined_board, 5) ^ secondary_board):
            return 5

    if column_is_playable(combined_board, 6):
        if is_winning_state(make_move(combined_board, 6) ^ secondary_board):
            return 6

    return -1


def heuristic_score(state):
    three_in_row = num_in_row(3, state)
    two_in_row = num_in_row(2, state)
    return get_num_set_bits(state) + 10 * two_in_row + 80 * three_in_row


def num_in_row(count, state):
    total = 0
    directions = {VERTICAL, RIGHT_DIAG, LEFT_DIAG, HORIZONTAL}

    # Some bitshifting magic to found how many in a row we have.
    # See: https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0

    for dir in directions:
        m = state
        for j in range(1, count):
            m = m & (m >> dir)
        total += bin(m).count("1")

    return total



def render_board(o_board, e_board, depth):
    print("\t"*depth + '+===============+')
    for i in range(6, -1, -1):
        print('\t'*depth + '| ', end="")
        for j in range(0, 7):
            cur = (i + j * 7)
            if o_board & (1 << cur):
                print('O ', end='')
            elif e_board & (1 << cur):
                print('E ', end='')
            else:
                print('. ', end='')

        print('|')
    print('\t'*depth + '+===============+')



@lru_cache(maxsize=2000000)
def evaluate_score(depth, max_depth, o_board, e_board, is_maximiser, alpha=-1000000, beta=1000000):
    #print(" "*depth + "X")
    highest_depth_achieved = depth + 1

    best_minmax_move = 0
    c = 6
    depth_achieved = highest_depth_achieved
    while c >= 0:
        if column_is_playable(o_board | e_board, c):
            if is_maximiser:
                new_board = make_move(o_board | e_board, c) ^ e_board

                if player_can_win(e_board, new_board):    # reversed because it's the next turn
                    max_score = -10000  # The score for this is -10000 since the enemy can win next turn.
                elif depth > max_depth:
                    print("e")
                    max_score = heuristic_score(o_board) - heuristic_score(e_board)
                else:
                    max_score, depth_achieved = evaluate_score(depth + 1, max_depth, new_board, e_board, False, alpha, beta)

                if max_score > alpha:
                    alpha, best_minmax_move, highest_depth_achieved = max_score, c, depth_achieved
                elif alpha < 10000:
                    if alpha == max_score:
                        if depth_achieved > highest_depth_achieved:
                            # If we're going to get the same score, stall for as long as possible.
                            alpha, best_minmax_move, highest_depth_achieved = max_score, c, depth_achieved

            else:
                new_board = make_move(o_board | e_board, c) ^ o_board
                if player_can_win(o_board, new_board):    # reversed because it's the next turn
                    min_score = 10000
                elif depth > max_depth:
                    min_score = heuristic_score(e_board) - heuristic_score(o_board)
                else:
                    min_score, depth_achieved = evaluate_score(depth + 1, max_depth, o_board, new_board, True, alpha, beta)
                if min_score < beta:
                    beta, highest_depth_achieved = min_score, depth_achieved

        if beta <= alpha:
            break
        c -= 1 # Most algorithms will attempt from the left. We attempt from the right.

    if depth == 0:
        if is_maximiser:
            return alpha, highest_depth_achieved, best_minmax_move
        return beta, highest_depth_achieved, best_minmax_move
    else:
        if is_maximiser:
            return alpha, highest_depth_achieved
        return beta, highest_depth_achieved


def play_game(o_board, e_board):
    if get_num_set_bits(o_board | e_board) >= 42 or \
            is_winning_state(o_board) or \
            is_winning_state(e_board):  # State is either already full or a player has already won.
        return

    c = player_can_win_get_pos(o_board, e_board)
    if c >= 0:
        return c    # Play to win
    c = player_can_win_get_pos(e_board, o_board)
    if c >= 0:
        return c    # Play to not lose

    # highest_score = -10000
    # max_depth = 6
    # c = 6
    # best_move = 0
    # while c >= 0:
    #     new_board = make_move(o_board | e_board, c) ^ o_board
    #     #...
    #     max_score, depth_achieved, _ = evaluate_score(0, max_depth, new_board, e_board, False)
    #     print(max_score)
    #     if max_score > highest_score:
    #         highest_score = max_score
    #         best_move = c
    #     print(c)
    #     c -= 1
    # print(f"Best move: {best_move}")



    # otherwise, find the most optimal option.
    max_depth = 10
    score, highest_depth_achieved, best_move = evaluate_score(0, max_depth, own_board, enemy_board, True)
    print(f"Score: {score}, best move: {best_move}, highest depth: {highest_depth_achieved}")
    return best_move


if __name__ == '__main__':
    #own_board, enemy_board = convert_state_to_player_pos('r', "r..y..r,r..y..r,......r,.......,.......,.......")
    #own_board, enemy_board = convert_state_to_player_pos('r', "rrryyyr,yyyrrry,rrryyyr,ryy.r..,yyrry..,rrr....")
    #own_board, enemy_board = convert_state_to_player_pos('y', "...ryr.,...yr..,...ry..,...y...,...r...,...y...")
    own_board, enemy_board = convert_state_to_player_pos('r', "...ryr.,...yr..,...ry..,...y...,...r...,...y...")

    # theoretically red can win this.
    render_board(own_board, enemy_board, 0)
    best_move = play_game(own_board, enemy_board)
    print(best_move)
    #render_board(own_board, enemy_board, 0)




# we can change the existing algorithm to only return score.
# and then for the first iteration we run the existing algorithm on each column (and if score == 10000 then break)



# See:
# http://www.informatik.uni-trier.de/~fernau/DSL0607/Masterthesis-Viergewinnt.pdf

# Note that if we're given a board with a floating piece, it'll crash. But that should be ok
# and it would be a waste of computation to test for it since we're guaranteed it won't happen