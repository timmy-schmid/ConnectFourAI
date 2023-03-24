# COMP3608-Ass1

Improvements to be made on standard Alpha-Beta version to save on computation so we can go deeper.

ideas from
* http://blog.gamesolver.org/solving-connect-four/03-minmax/)
* https://github.com/denkspuren/BitboardC4/blob/master/BitboardDesign.md
* https://towardsdatascience.com/creating-the-perfect-connect-four-ai-bot-c165115557b0

* Implementing timing functions so that if we approach the 1 second mark we stop our search and return the best result.
* Storage of the first X optimal moves. (not sure if this is possible since we can't access file system).
* Implement Negamax variant. Rather than taking the difference of scores to calculate eval we can just calculate the opposite
* Changing ordering of analysing columns to benefit those that are more promising. Ie. start searching from middle columns first.
* Create Transposition tables (Dynamic Programming) of states that have already been calculated to save computation
* Iterative deepening. Explore shallow first then deep -> this ensures we capture wins that are on the next few levels before conducting DFS.
* Anticipate direct losing moves
  * We should always play a column on which the opponent has a winning position in the bottom of the column.
  * We should never play under an opponent winning positions.
  * If the opponent has more than two directly playable winning positions, then we cannot do anything and we will lose.
* Order moves at each level based off a score function

