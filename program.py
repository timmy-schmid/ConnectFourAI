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

def connect_four_mm(contents, turn, max_depth):
    #TODO
    return ''

if __name__ == '__main__':
    # Example function call below, you can add your own to test the connect_four_mm function
    connect_four_mm(".......,.......,.......,.......,.......,.......", "red", 1)

    
    