from collections import namedtuple, defaultdict
import itertools, copy, random, operator

class _GameBoardMeta(type):
	"""Metaclass for defining and blocking access to some atributes of a gameboard"""
	
	_reserved_attrs = ['color', 'width', 'height']
	
	def __new__(cls, name, bases, dict):
		dict['colors'] = {'red': 'r', 'blue': 'b'} #TODO: Should be immutable dict created by descriptors
		dict['width'] = 7
		dict['height'] = 6
		
		def setattr(self, name, value):
			"""Defined to prevent tampering with colors"""
			if name not in cls._reserved_attrs:
				super(self.__class__, self).__setattr__(name, value)
			else:
				raise AttributeError, "Field %s cannot be changed." %name

		dict['__setattr__'] = setattr

		return type(name, bases, dict)


class GameBoard(object):
	"""Class representing the game bord with it's states and actions"""
	
	def __init__(self, copy = None):
		if copy:
			self._moves_list = copy._moves_list[:]
		else:
			self._moves_list = [] #Moves taken on this board in the game - defines the state of the game completely
		self._move = namedtuple("_move", ["color", "column"])
		
	def moves_no(self):
		"""Current number of moves played"""
		return len(self._moves_list)
		
	def get_last_move(self):
		if self._moves_list:
			return self._moves_list[-1]
		return None
		
	def revoke_last_move(self):
		if self._moves_list:
			return self._moves_list.pop()
		return None
		
	def get_height(self, column):
		"""retuns the hight (y-coordinte) of a particular column"""
		return len(filter(lambda m: m.column == column, self._moves_list))
		
	def get_color(self, row, column):
		"""Return the color of the piece on the particular position or None if the pos is empty"""
		if column not in xrange(1, self.width+1) or row > self.get_height(column):
			return None
		else:
			return filter(lambda m: m.column == column, self._moves_list)[row-1].color
			
	@classmethod
	def is_valid_field(cls, row, column):
		"""Checks if field is valid"""
		if 0 < row <= cls.height and 0 < column <= cls.width:
			return True
		return False
	
	@classmethod
	def get_horizontals(cls, row, column):
		"""Returns a list of lists of field (tuples) that are valid horizontals for the given field"""
		
		valid_fields = [(row, column+i) for i in xrange(-3, 4) if cls.is_valid_field(row, column+i)] #get valid fields
		return [valid_fields[i:4+i] for i in xrange(0, len(valid_fields)-3)]
		
	@classmethod
	def get_verticals(cls, row, column):
		"""Returns a list of lists of field that are valid verticals for the given field"""
		
		valid_fields = [(row+i, column) for i in xrange(-3, 4) if cls.is_valid_field(row+i, column)]
		return [valid_fields[i:4+i] for i in xrange(0, len(valid_fields)-3)]
			
	@classmethod
	def get_diagonals(cls, row, column):
		"""Returns a list of lists of field that are valid diagonals for the given field"""
		
		up2down_fields = [(row-i, column+i) for i in xrange(-3, 4) if cls.is_valid_field(row-i, column+i)]
		down2up_fields = [(row+i, column+i) for i in xrange(-3, 4) if cls.is_valid_field(row+i, column+i)]
		diagonals = [up2down_fields[i:4+i] for i in xrange(0, len(up2down_fields)-3)]
		diagonals.extend([down2up_fields[i:4+i] for i in xrange(0, len(down2up_fields)-3)])
		return diagonals
			
	def is_won(self):
		"""check if the game is currently won by somebody"""
		
		#Game cannot be won with less than 7 moves played
		if self.moves_no() < 7:
			return False
		
		#Do not check all the rows, only the ones that will not be caught by the previous search
		columns = xrange(1, self.width+1)
		rows = [m*4 + 1 for m in xrange(0, self.height//4 + 1)]
		
		fields = [(r, c) for r in rows for c in columns]
		
		for field in fields:
			combinations = self.get_horizontals(*field) + self.get_verticals(*field) + self.get_diagonals(*field)
			for c in combinations:
				field_colors = [self.get_color(*f) for f in c]
				if not filter(operator.not_, field_colors) and field_colors[1:] == field_colors[:-1]:
					return field_colors[0]
		return False
		
	def make_move(self, color, column):
		"""Make the next move, move is a namedtuple of (color, column)"""
		
		if self.get_height(column) == self.height or column > self.width:
			raise ValueError, "Illegal column %d, column is either full or does not exist" %column
		
		if color in self.colors:
			if not self._moves_list or self._moves_list[-1].color != color:
				self._moves_list.append(self._move(color, column))
			else:
				raise ValueError, "Illegal move. Player %s cannot play twice in a row" %color
		else:
			raise ValueError, "Illegal color %s" %color
			
	def move_and_check(self, color, column):
		"""Combination of the two previous methods"""
	
		self.make_move(color, column)
		return self.is_won()
	
	def __repr__(self):
		#Create a list of columns - a matrix
		column_list = [[t.color for t in self._moves_list if t.column == i] for i in xrange(1, self.width+1)]
		#Add padding to each column so that we have propper matrix
		for col in column_list:
			col.extend([None for cnt in xrange(self.height+1-len(col))])
		#transpose matrix and convert rows to strings
		repr = ["| " + " | ".join([self.colors[c] if c else " " for c in row]) + " |" for row in zip(*column_list)]
		#Finally add line feeds
		return "\n".join(reversed(repr))
	
	__metaclass__ = _GameBoardMeta
	
class ComputerPlayer(object):
	"""Class implementing a computer player AI and has a copy of the boeard being played"""

	def __init__(self, board, color, first_move=False):
		self.board = board
		self.color = color
		self.first_move = first_move
		self.moves_ahead = 5
	
	def _calculate_next_move(self):
		"""The function that does the AI for the game"""
		import datetime
		start = datetime.datetime.now() 
		#If making the first move always play the center
		if self.board.moves_no() == 0:
			return 4
			
		last_move = self.board.get_last_move().column
		
		wins = losses = {}
		
		#All posible moves eg. all valid columns
		all_moves = xrange(1, self.board.width+1)
		needed_moves = [mov for mov in all_moves if self.board.get_height(mov) or (self.board.get_height(mov-1) or self.board.get_height(mov+1))]
		moves = needed_moves
			
		#number of moves ahead to calculate - one more if the opponent played first#
		moves_ahead = self.moves_ahead
		colors = self.board.colors.keys()
		
		#Sequence of moves
		moves_color_seq = colors * (moves_ahead/2) if colors[1] == self.color else  colors[::-1] * (moves_ahead/2)
		if moves_ahead%2:
			moves_color_seq.append(moves_color_seq[-2])
		
		for move in moves:
			#check if this move can lead to an immediate win
			first_move_board = GameBoard(self.board)
			try:
				first_move_board.make_move(self.color, move)
			except ValueError:
				continue

			if first_move_board.is_won() == self.color:
				return move
			
			#Calculate all possibilities for the next 5 or 6 moves (see above)
			moves_tree = itertools.product(moves, repeat=moves_ahead)
			
			#Count wins and losses according to the number of moves it takes to get there
			win_dict = defaultdict(int)
			loss_dict = defaultdict(int)
			
			boards_cache = {}
			
			#Now go through them and count wins and losses
			for moves_branch in moves_tree:
				#Find the sub-branch that is not laready calculated
				sub_branches = [(tuple(moves_branch[:i]), moves_color_seq[:i], i-1) for i in xrange(1, len(moves_branch)) if tuple(moves_branch[:i]) not in boards_cache]

				for sub_branch, sub_colors, move_cnt in sub_branches:
					if len(sub_branch) == 1:
						next_moves_board = GameBoard(first_move_board)
					else:
						next_moves_board = GameBoard(boards_cache[sub_branch[:-1]])
					boards_cache[sub_branch] = next_moves_board
					next_move = sub_branch[-1]
					
					try:
						next_moves_board.make_move(sub_colors[move_cnt], next_move)
					except ValueError: #impossible move
						continue
					win = next_moves_board.is_won()
					if win == self.color:
						win_dict[move_cnt+2] += 1
					elif win:
						loss_dict[move_cnt+2] += 1

			wins[move] = win_dict.copy()
			losses[move] = loss_dict.copy()
		
		#Now analize the data and try to eliminate moves that are bad 
		candidates = [move for move in moves if 2 not in losses[move]] #eliminate all the ones that will lead to an immediate loss
		
		if not candidates:
			#means that all of the moves will lead to defeat so might as well play anything
			return random.randint(1, len(moves))
		
		#Order cqandidates by those that are most likely to lead to victory eg. more victories possible
		candidates = sorted(candidates, key=lambda m: sum(wins[m].values()), reverse=True)
		return candidates[0]
		
	def play(self):
		print "Thinking..."
		move = self._calculate_next_move()
		return self.board.move_and_check(self.color, move)
		
if __name__ == "__main__":
	g = GameBoard()
	cp = ComputerPlayer(g, 'red', True)
	valid_moves = "".join([str(i) for i in range(1,g.width+1)])
	while 1:
		if cp.play():
			print g, "\nComputer wins!"
			exit()
		print g
		player_move = -1
		while player_move not in xrange(1, g.width+1):
			player_move = raw_input("Make your move blue (1-7) or q->")
			if player_move in 'qQ':
				exit()
			player_move = int(player_move) if player_move in valid_moves else -1

		if g.move_and_check('blue', player_move):
			print g, "\nYou win!"
			exit()
		print g