**States**
1. agent position [X, Y]
2. platform position [X, Y]\
(*nearest below, nearest top, middle top, farthest top*)
3. nearest coin platform [X, Y]\
(*state vector contains 6 coordinates*)

**Actions**
1. sh jump + none
2. sh jump + left
3. sh jump + right
4. ln jump + none
5. ln jump + left
6. ln jump + right
7. left
8. right
9. none

**Reference**\
(1) Pygame used in this project [link](https://coderslegacy.com/python/pygame-platformer-game-development/)

(2) Reinforcement Learning Explained Visually (Part 5): Deep Q Networks, step-by-step [link](https://towardsdatascience.com/reinforcement-learning-explained-visually-part-5-deep-q-networks-step-by-step-5a5317197f4b)