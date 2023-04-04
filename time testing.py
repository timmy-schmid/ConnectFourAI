import timeit
import statistics
from tqdm import tqdm
# 2 boards appended to each other
x = int("101010101010101101010110111100100010101010101010101010101101010110111100100010101010", 2)
# 2 boards, separate already
x1 = int("100000000000000000001000000000000000000001", 2)
x2 = int("000000001000000000000000000000000100000000", 2)
x3 = int("100000002000000000001000000000000200000001", 3)



PRECOMPUTED_POWERS = [0, 3, 9,
                      27, 81, 243,
                      729, 2187, 6561,
                      19683, 59059, 177147,
                      531441, 1494323, 4782969,
                      14348907, 43046721, 129140163,
                      387420489, 1162261467, 3486784401,
                      10460353203, 31381059609, 94143178827,
                      282429536481, 847288609443, 2541865828329,
                      7625597484987, 22876792454961, 68630377364883,
                      205891132094649, 617673396283947, 1853020188851841,
                      5559060566555523, 16677181699666569, 50031545098999707,
                      150094635296999121, 450283905890997363, 1350851717672992089,
                      4052555153018976267, 12157665459056928801, 36472996377170786403,
                      109418989131512359209]


board = [x1,x2]

# Given 2 ints
def v1 ():
    return timeit.timeit("""\
y = x1 | x2
""", globals=globals(), number=1000000)

# Given 1 int
def v2():
    return timeit.timeit("""\
y = (x >> 42) | x
""", globals=globals(), number=1000000)

# Given an array of 2 ints
def v3():
    return timeit.timeit("""\
b = board.copy()
y = b[0] | b[1]
""", globals=globals(), number=1000000)

# 2 ints with copying
def v4():
    return timeit.timeit("""\
a = x1
b = x2
y = a | b
""", globals=globals(), number=1000000)


def v5():
    return timeit.timeit("""\
x % 2
""", globals=globals(), number=1000000)

def v6():
    return timeit.timeit("""\
x % 3
""", globals=globals(), number=1000000)

def v7():
    return timeit.timeit("""\
x >> 2
""", globals=globals(), number=1000000)

def v8():
    return timeit.timeit("""\
x // 2
""", globals=globals(), number=1000000)

def v9():
    return timeit.timeit("""\
x // 3
""", globals=globals(), number=1000000)

def v10():
    return timeit.timeit("""\
x1 >> 41
""", globals=globals(), number=1000000)


bit_num = 39
xk = int("000100000000000000000000000000000000000000", 2)
def v11():  # we want the 39th bit (from the right). 42 - 39 = 3
    return timeit.timeit("""\
(xk << (42 - bit_num)) >> (41)
""", globals=globals(), number=1000000)

def v12():  # we want the 39th bit (from the right). 42 - 39 = 3
    return timeit.timeit("""\
(xk * (3**(42 - bit_num))) // (3 ** 41)
""", globals=globals(), number=1000000)


def v13():
    return timeit.timeit("""\
(x3 * PRECOMPUTED_POWERS[42 - bit_num]) // PRECOMPUTED_POWERS[41]
""", globals=globals(), number=1000000)


# FINAL COMPARISON OF base 3 vs 2x base 2: second is faster.
# i.e. avg of 71.9% of time; 140% faster (tested 200 million times)
# interestingly we could use a library called 'gmpy' to speed up bigint (bignum( operations, though I'm not sure
# it'd speed up bitshifts. Python converts the number from base 10 to base 2**30.
# https://www.codementor.io/@arpitbhayani/how-python-implements-super-long-integers-12icwon5vk

three_41_power = PRECOMPUTED_POWERS[41]
def v14():
    return timeit.timeit("""\
(x3 * PRECOMPUTED_POWERS[42 - bit_num]) // three_41_power
""", globals=globals(), number=10000000)


def v15():
    return timeit.timeit("""\
((x1 | x2) << (42 - bit_num)) >> (41)
""", globals=globals(), number=10000000)



def v16():
    return timeit.timeit("""\
((x1 | x2) >> (41-bit_num)) % 2
""", globals=globals(), number=10000000)

# we'd like to design a method that gets the columns you can play in.
# if we represent as a series of rows, we can easily


# 35 36 37 38 39 40 41
# 28 29 30 31 32 33 34
# 21 22 23 24 25 26 27
# 14 15 16 17 18 19 20
# 7  8  9  10 11 12 13
# 0  1  2  3  4  5  6


testing_vertical = [0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0, 0, 0,
                    1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1, 1, 1] # Top 3 rows will need custom values (indices 21-41 inclusive)


def v17(): # this returns an int either 0 or greater than. Greater than implies intersection.
    return timeit.timeit("""\
(x1 | x2) & (1 << bit_num)
""", globals=globals(), number=10000000)

def v18():
    return timeit.timeit("""\
get_num_set_bits((x1 | x2) & testing_vertical[4]) == 4
""", globals=globals(), number=1000000)

def v19():
    return timeit.timeit("""\
get_num_set_bits((x1 | x2) & testing_vertical[4]) > 3
""", globals=globals(), number=1000000)

def v20():
    return timeit.timeit("""\
get_num_set_bits((x1 | x2) & testing_vertical[4]) >= 4
""", globals=globals(), number=1000000)

def v20():
    return timeit.timeit("""\
get_num_set_bits((x1 | x2) & testing_vertical[4]) & 4
""", globals=globals(), number=1000000)


def get_num_set_bits(n: int):   # " Brian Kernighan's Algorithm "
    c = 0
    while n > 0:
        n &= (n-1)
        c += 1
    return c


print(get_num_set_bits(3))
print(get_num_set_bits(5))
print(get_num_set_bits(92525)) # Should be 10

def v21():
    return timeit.timeit("""\
if False:
    if True:
        pass
""", number=1000000)

def v22():
    return timeit.timeit("""\
if False and True:
    pass
""", number=1000000)

def do_something(a, b, c):
    pass

def do_something2(a, b):
    c = get_num_set_bits(a | b)

def v23():
    return timeit.timeit("""\
do_something(1, 9, 14)
""", globals=globals(), number=1000000)

def v24():
    return timeit.timeit("""\
do_something2(1, 9)
""", globals=globals(), number=1000000)

def v25():
    return timeit.timeit("""\
if True:
    pass
""", globals=globals(), number=1000000)

def v26():
    return timeit.timeit("""\
if 1 >= 0:
    pass
""", globals=globals(), number=1000000)





NUM_TIMES = 20
RANGE_Vs = [25, 26]
result_Vs = []

for j in range(RANGE_Vs[0], RANGE_Vs[1]+1):
    result_Vs.append([None]*NUM_TIMES)



for i in tqdm(range(0, NUM_TIMES)):
    for j in range(RANGE_Vs[0], RANGE_Vs[1] + 1):
        result_Vs[j - RANGE_Vs[0]][i] = eval(f"v{j}()")


for j in range(RANGE_Vs[0], RANGE_Vs[1]+1):
    print(f"Avg time for v{j}: {statistics.mean(result_Vs[j-RANGE_Vs[0]])}")



# Hence we conclude we should:
# Only maintain the board as two integers, one for opponent and one for self.
#

# Using base 3 instead of base 2 means about a 20% increased time for getting value at specific position.


# we could precompute powers of 3 and then 'bitshift' (by multiples of 3) in order to obtain positions.
# But this is far more computationally expensive. Though each instance will occupy log_2(3**42) instead of 2 * log_2(2**42)
# i.e. storing two copies of base 2: 84 bits. Storing one copy of base 3: 66.57 = 67. I.e. using two numbers takes 126%.
# However storing in base 3 requires performing floor division and then modulo which is much more expensive

# additionally, sending through 1 int instead of 2




# additionally: should we keep it in rows or columns?
# columns increases the likelihood that