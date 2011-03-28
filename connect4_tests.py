import unittest, connect4

correct_moves_sequence = [
	('red', 1)	,
	('blue', 2)	,
	('red', 1)	,
	('blue', 4)	,
	('red', 1)	,
	('blue', 2)	,
	('red', 1)	,
	('blue', 4)	,
]

inccorrect_moves_sequence = [
	('red', 1)	,
	('red', 4)	,
]

valid_fields = [
	(2, 7),
	(1, 1),
	(4, 2),
]

invalid_fields = [
	(0, 6),
	(1, -1),
	(3, 10),
	(7, 7),
]

colortest_moves = [
	('red', 5), 
	('blue', 5),
	('red', 6), 
	('blue', 6), 
	('red', 6), 
	('blue', 7), 
]

colortest_checks = [
	[ (1, 5), 'red'],
	[ (2, 5), 'blue'],
	[ (1, 6), 'red'],
	[ (2, 6), 'blue'],
	[ (3, 6), 'red'],
	[ (1, 7), 'blue'],
]

colortest_checks_none = [
	(1, 1),
	(2, 7),
	(6, 4),
	(2, 12),
	(1, 3)
]

horziontals_checks = {
	(1, 1) : [[(1, 1), (1, 2), (1, 3), (1, 4)]],
	(2, 4) : [
				[(2, 1), (2, 2), (2, 3), (2, 4)], 
				[(2, 2), (2, 3), (2, 4), (2, 5)],
				[(2, 3), (2, 4), (2, 5), (2, 6)],
				[(2, 4), (2, 5), (2, 6), (2, 7)],
			]
}

verticals_checks = {
	(1, 1) : [[(1, 1), (2, 1), (3, 1), (4, 1)]],
	(3, 4) : [
				[(1, 4), (2, 4), (3, 4), (4, 4)], 
				[(2, 4), (3, 4), (4, 4), (5, 4)], 
				[(3, 4), (4, 4), (5, 4), (6, 4)], 
			]
}

diagonals_checks = {
	(2, 1) : [[(2, 1), (3, 2), (4, 3), (5, 4)]],
	(3, 4) : [
				[(6, 1), (5, 2), (4, 3), (3, 4)], 
				[(5, 2), (4, 3), (3, 4), (2, 5)], 
				[(4, 3), (3, 4), (2, 5), (1, 6)],
				[(1, 2), (2, 3), (3, 4), (4, 5)],
				[(2, 3), (3, 4), (4, 5), (5, 6)],
				[(3, 4), (4, 5), (5, 6), (6, 7)],
			]
}

won_sequences = [
	[('red', 5), ('blue', 5), ('red', 6)],
	[('red', 5), ('blue', 5), ('red', 6), ('blue', 6), ('red', 4), ('blue', 3), ('red', 7),], #Horizontal
	[('blue', 6), ('red', 5), ('blue', 6), ('red', 5), ('blue', 6), ('red', 5), ('blue', 6),], #Vertical
	[('blue', 6), ('red', 5), ('blue', 5), ('red', 4), ('blue', 3), ('red', 4), ('blue', 4), ('red', 3), ('blue', 3), ('red', 2), ('blue', 3),], #Diagonal
	[('blue', 6), ('red', 5), ('blue', 5), ('red', 4), ('blue', 3), ('red', 4), ('blue', 4), ('red', 3), ('blue', 3), ('red', 2), ('blue', 2),],
]

won_results = [False, 'red', 'blue', 'blue', False]

class TestGameBoard(unittest.TestCase):
	def setUp(self):
		self.board = connect4.GameBoard()
		
	def test_copy_constructor(self):
		for s in correct_moves_sequence:
			self.board.make_move(*s)
		board2 = connect4.GameBoard(self.board)
		self.assertEqual(self.board._moves_list, board2._moves_list)
		self.assertNotEqual(self.board, board2)
		
	def test_valid_fields(self):
		for f in valid_fields:
			self.assertTrue(self.board.is_valid_field(*f))
	
	def test_invalid_fields(self):
		for f in invalid_fields:
			self.assertFalse(self.board.is_valid_field(*f))
	
	def test_moves_correct(self):
		for s in correct_moves_sequence:
			self.board.make_move(*s)
		self.assertEqual(self.board.moves_no(), len(correct_moves_sequence))
		
	def test_moves_incorrect(self):
		self.board.make_move(*inccorrect_moves_sequence[0])
		self.assertRaises(ValueError, self.board.make_move, *inccorrect_moves_sequence[1])
		
	def test_moves_num_zero(self):
		self.assertEqual(self.board.moves_no(), 0)
		
	def test_get_colors(self):
		for i, m in enumerate(colortest_moves):
			self.board.make_move(*m)
			self.assertEqual(self.board.get_color(*colortest_checks[i][0]), colortest_checks[i][1])
		for f in colortest_checks_none:
			self.assertEqual(self.board.get_color(*f), None)
			
	def test_get_horizontalz(self):
		for k in horziontals_checks:
			self.assertEqual(self.board.get_horizontals(*k), horziontals_checks[k])
			
	def test_get_verticals(self):
		for k in verticals_checks:
			self.assertEqual(self.board.get_verticals(*k), verticals_checks[k])
			
	def test_get_diagonals(self):
		for k in diagonals_checks:
			self.assertEqual(self.board.get_diagonals(*k), diagonals_checks[k])
	
	def test_won(self):
		for i, seq in enumerate(won_sequences):
			for move in seq:
				self.board.make_move(*move)
			self.assertEqual(self.board.is_won(), won_results[i])
			self.setUp()
		
if __name__ == "__main__":
	unittest.main()