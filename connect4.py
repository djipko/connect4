from collections import namedtuple, defaultdict
import itertools, copy, random, operator

class _GameBoardMeta(type):
	_reserved_attrs = ['color', 'width', 'height']
	
	def __new__(cls, name, bases, dict):
		dict['colors'] = {'red': 'r', 'blue': 'b'} #Should be immutable dict created by descriptors
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
		
		# print "\n"
		# print self
		# print fields
		
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
			
	
	def __repr__(self):
		#create a list of columns - a matrix
		column_list = [[t.color for t in self._moves_list if t.column == i] for i in xrange(1, self.width+1)]
		#Add padding to each column so that we have propper matrix
		for col in column_list:
			col.extend([None for cnt in xrange(self.height+1-len(col))])
		#transpose matrix and convert rows to strings
		repr = ["| " + " | ".join([self.colors[c] if c else " " for c in row]) + " |" for row in zip(*column_list)]
		#Finally add line feeds
		return "\n".join(reversed(repr))
	
	__metaclass__ = _GameBoardMeta
	
def printdict(d):
	print "{"
	for k in d:
		print "\t%r - %r" %(k, d[k])
	print "}"
		
class ComputerPlayer(object):
	def __init__(self, board, color, first_move=False):
		self.board = board
		self.color = color
		self.first_move = first_move
	
	def _calculate_next_move(self):
		"""The function that does the AI for the game"""
		import datetime
		print datetime.datetime.now() 
		#If making the first move allways play the center
		if self.board.moves_no() == 0:
			return 4
			
		last_move = self.board.get_last_move().column
			
		#If this is the second move of the game play always next to the last
		if self.board.moves_no() == 1:
			if last_move in xrange(1, self.board.width/2):
				return last_move + 1
			else:
				return last_move - 1

		wins = {}
		losses = {}
		
		#All posible moves eg. all valid columns
		all_moves = xrange(1, self.board.width)
		needed_moves = xrange(last_move-2 if last_move-2 in all_moves else 1, last_move+3 if last_move+3 in all_moves else 8)
		moves = list(needed_moves)
			
		#number of moves ahead to calculate - one more if the opponent played first#
		moves_ahead = 5
		colors = self.board.colors.keys()
		
		#Sequence of moves
		moves_color_seq = colors * (moves_ahead/2) if colors[1] == self.color else  colors[::-1] * (moves_ahead/2)
		if moves_ahead%2:
			moves_color_seq.append(moves_color_seq[-2])
		
		for move in moves:
			#check if this move can lead to an immediate win
			first_move_board = GameBoard(self.board)
			first_move_board.make_move(self.color, move)
			if first_move_board.is_won() == self.color:
				return move
			
			#Calculate all possibilities for the next 5 or 6 moves (see above)
			moves_tree = itertools.product(moves, repeat=moves_ahead)
			
			#Count wins and losses according to the number of moves it takes to get there
			win_dict = defaultdict(int)
			loss_dict = defaultdict(int)
			
			#Now go through them and count wins and losses
			for next_moves in moves_tree:
				print next_moves
				next_moves_board = GameBoard(first_move_board)
				for i, next_move in enumerate(next_moves):
					try:
						next_moves_board.make_move(moves_color_seq[i], next_move)
					except ValueError: #impossible move
						continue
					win = next_moves_board.is_won()
					if win:
						#print "found win"
						if win == self.color:
							win_dict[i+1] += 1
						else:
							loss_dict[i+1] += 1
			print "Done with da loop"
			#Save the dictionaries
			wins[move] = win_dict.copy()
			losses[move] = loss_dict.copy()
			
		for k in wins:
			print k
			printdict(wins[k])
		for k in losses:
			print k
			printdict(losses[k])
		
		#Now analize the data and try to eliminate moves that are bad 
		#Also try to find the move that has the moste potentials for winning
		candidates = [move for move in moves if 1 not in losses[move]] #eliminate all the ones that will lead to an immediate loss
		print candidates
		
		if not candidates:
			#means that all of the moves will lead to defeat so might as well play anything
			return random.randint(1, len(moves))
		
		#eliminate those that have no wins
		candidates = [move for move in candidates if wins[move]] 
		print candidates
		
		#elliminate those that can lead to loss before a win
		candidates = [move for move in candidates if not losses[move] or sorted(wins[move].keys())[0] <= sorted(losses[move].keys())[0]+1] 
		print candidates
		
		#Order cqandidates by those that are most likely to lead to victory eg. more victories possible
		candidates = sorted(candidates, key=lambda m: sum(wins[m].values()), reverse=True)
		print candidates
		print datetime.datetime.now()
		return candidates[0]
		
	def play(self):
		move = self._calculate_next_move()
		self.board.make_move(self.color, move)
		
if __name__ == "__main__":
	g = GameBoard()
	cp = ComputerPlayer(g, 'red', True)
	while 1:
		cp.play()
		won = g.is_won()
		if won:
			print "Won %s" %won
			exit()
		print g
		g.make_move('blue',int(raw_input("Make your move ->")))
		print g
		if won:
			print "Won %s" %won
			exit()