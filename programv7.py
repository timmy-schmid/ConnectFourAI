# SID: 500687806 and 510427771

from functools import lru_cache
import time
from multiprocessing import Pool, cpu_count
import sys

VERTICAL = 1
RIGHT_DIAG = 6
LEFT_DIAG = 8
HORIZONTAL = 7

def render_board(o_board, e_board, depth):
    print("\t" * depth + '+===============+')
    for i in range(6, -1, -1):
        print('\t' * depth + '| ', end="")
        for j in range(0, 7):
            cur = (i + j * 7)
            if o_board & (1 << cur):
                print('O ', end='')
            elif e_board & (1 << cur):
                print('E ', end='')
            else:
                print('. ', end='')

        print('|')
    print('\t' * depth + '+===============+')



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


def init_pool(given_int, max_depth, o_board, e_board):
    global start_time
    start_time = given_int
    global pool_depth
    pool_depth = max_depth
    global pool_o_board
    pool_o_board = o_board
    global pool_e_board
    pool_e_board = e_board


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
        return red_state, yel_state  # own_board, enemy_board
    else:
        return yel_state, red_state  # own_board, enemy_board


@lru_cache(maxsize=2000000)
def get_num_set_bits(n: int):  # " Brian Kernighan's Algorithm "
    c = 0
    while n > 0:
        n &= (n - 1)
        c += 1
    return c


# !!! Could be optimised.
@lru_cache(maxsize=2000000)
def get_col_height(board, col):
    col_values = (board >> col * 7) & 63  # 63 = b0111111 i.e. values in the column.
    return get_num_set_bits(col_values) + col * 7  # Offset by the column


@lru_cache(maxsize=2000000)
def make_move(board, col):
    board ^= 1 << get_col_height(board, col)
    return board


@lru_cache(maxsize=2000000)
def column_is_playable(board, c):
    return (board >> c * 7) & 32 != 32  # 32 = 0100000, i.e. returns whether or not the top bit is set.


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


@lru_cache(maxsize=200000)
def evaluate_score_maximise(depth,  o_board, e_board, alpha, beta):
    if time.time() - start_time > 0.95:
        #print('exiting')
        return heuristic_score(o_board) - heuristic_score(e_board)

    c = 6
    while c >= 0:
        if column_is_playable(o_board | e_board, c):
            new_board = make_move(o_board | e_board, c) ^ e_board

            if player_can_win(e_board, new_board):  # reversed because it's the next turn
                max_score = -10000  # The score for this is -10000 since the enemy can win next turn.
            elif depth < 0:
                max_score = heuristic_score(o_board) - heuristic_score(e_board)
            else:
                max_score = evaluate_score_minimise(depth - 1, new_board, e_board, alpha, beta)

            if max_score > alpha:
                alpha = max_score
        if beta <= alpha:
            break
        c -= 1  # Most algorithms will attempt from the left. We attempt from the right.
    return alpha


@lru_cache(maxsize=200000)
def evaluate_score_minimise(depth, o_board, e_board, alpha, beta):
    if time.time() - start_time > 0.95:
        #print('exiting')
        return heuristic_score(o_board) - heuristic_score(e_board)

    c = 6
    while c >= 0:
        if column_is_playable(o_board | e_board, c):
            new_board = make_move(o_board | e_board, c) ^ o_board
            if player_can_win(o_board, new_board):  # reversed because it's the next turn
                min_score = 10000
            elif depth <= 0:
                min_score = heuristic_score(o_board) - heuristic_score(e_board)
            else:
                min_score = evaluate_score_maximise(depth - 1, o_board, new_board, alpha, beta)

            if min_score < beta:
                beta = min_score
        if beta <= alpha:
            break
        c -= 1  # Most algorithms will attempt from the left. We attempt from the right.
    return beta


# Performs score calculation for a given column
def get_first_alpha_of_col(c, depth=None, o_board=None, e_board=None):
    if depth is None:  # i.e. multiprocessing
        depth = pool_depth
        o_board = pool_o_board
        e_board = pool_e_board

    if column_is_playable(o_board | e_board, c):
        # Guaranteed it's maximiser
        new_board = make_move(o_board | e_board, c) ^ e_board
        if player_can_win(e_board, new_board):  # reversed because it's the next turn
            max_score = -10000  # The score for this is -10000 since the enemy can win next turn.
        elif time.time() - start_time > 0.95:
            #print('EXITING')
            return heuristic_score(o_board) - heuristic_score(e_board)
        else:
            max_score = evaluate_score_maximise(depth, new_board, e_board, -1000000, 1000000)
        return max_score

    return -1000000  # Can't play


def evaluate_score_first_maximiser_single(depth, o_board, e_board):
    highest_score = -1000000
    c = 0
    while c < 7:
        score = get_first_alpha_of_col(c, depth, o_board, e_board)
        if score > highest_score:
            highest_score = score
            optimal_move = c
        c += 1
    return optimal_move


# Performs score calculation for the first 6 columns.
def evaluate_score_first_maximiser(depth, o_board, e_board):
    optimal_move = 0
    if depth < 9:
        return evaluate_score_first_maximiser_single(depth, o_board, e_board)
    else:   # Around this point, the overhead of multiprocessing is justifiable
        try:
            t1 = time.time()
            if t1 - start_time > 0.95:
                return evaluate_score_first_maximiser_single(depth, o_board, e_board)
            columns = [3, 2, 1, 4, 5, 6, 0]  # Centred
            p = Pool(processes=min(cpu_count(), 7), initializer=init_pool, initargs=(start_time, depth, o_board, e_board))
            if time.time() - start_time > 0.95:
                return evaluate_score_first_maximiser_single(depth, o_board, e_board)

            scores = p.map(get_first_alpha_of_col, columns)
            return columns[max(range(len(scores)), key=scores.__getitem__)]  # Get index

        except (RuntimeError, BlockingIOError):
            return evaluate_score_first_maximiser_single(depth, o_board, e_board)




def connect_four(contents, turn):
    global start_time
    start_time = time.time()
    o_board, e_board = convert_state_to_player_pos(turn, contents)

    if get_num_set_bits(o_board | e_board) >= 42 or \
            is_winning_state(o_board) or \
            is_winning_state(e_board):  # State is either already full or a player has already won.
        return

    # Manual strategy
    if get_num_set_bits(o_board | e_board) == 0:
        return 3

    # if game_has_been_played_by_us: return play_with_manual_strat()

    c = player_can_win_get_pos(o_board, e_board)
    if c >= 0:
        return c  # Play to win
    c = player_can_win_get_pos(e_board, o_board)
    if c >= 0:
        return c  # Play to not lose

    best_move = 0
    max_depth = 5
    while time.time() - start_time < 0.85:   # We'd like to guarantee that it explores the next level entirely.
        #print(f"Starting depth {max_depth}")
        best_move = evaluate_score_first_maximiser(max_depth, o_board, e_board)
        evaluate_score_maximise.cache_clear()   # These results will be from heuristics.
        evaluate_score_minimise.cache_clear()   # These results will be from heuristics.
        max_depth += 1
    return best_move


if __name__ == '__main__':
    t = time.time()
    if len(sys.argv) <= 1:
        board = ".rryy..,.......,.......,.......,.......,......."
        player = "red"
    else:
        board = sys.argv[1]
        player = sys.argv[2]

    print(connect_four(board, player))
    print(time.time() - t)

# See:
# http://www.informatik.uni-trier.de/~fernau/DSL0607/Masterthesis-Viergewinnt.pdf
