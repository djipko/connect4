connect4.py - A very naive python implementation of a Connect Four game
==

The implementation does not use any external data to calculate next move of the computer player eg. it does it on the fly by using a combination of breath first search of the possible moves tree with a touch of dynamic programming to speed things up a bit. The idea was to hack up a working prototype as quickly as possible, while keeping in mind the possible future expansions like adding the database, improving the AI, network play etc.

The algorythm
--

The algorythm is very simple at the moment, and is implemented in the _calculate_next_move method of the ComputerPlayer class. It is very far from optimal, it does not take into consideration the possibility of a perfect game nor does it save already calculated positions between moves to speed up future calculations. Some of the things that can be improved immediately are:
* Saving state of the already calculated moves, which would significantly shorten the 'Thinking' time.
* Adding more sophisticated decision tree
* Ultimately using a pre-calculated moves datbase

The interface
--

Currently the game runs as a command line program. There is no possibility to choose who plays first (computer goes first) or even which color the player will be (defaults to blue, the other possibility being red). The column which to play is chosen by inputing a number between 1 and 7 representing the column the player wishes to play. 

In the future the game may be modified to use a library like game.py to develop a graphical interface for the game. 
