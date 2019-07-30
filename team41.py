from copy import deepcopy
import random
import sys
import traceback
import time
import signal
from time import time

class Team41:

	def __init__(self):
		
		self.pos_weight = ((4, 6, 4),(6, 3, 6),(4, 6, 4))                                         # Predefined weight of winning smallboard[i][j]
		self.startTime = 0                                                                        # Starting time of game
		self.timeLimit = 1                                                                  # Maximum time for single move
		self.is_bonus = 0                                                                         # Check if there is bonus move
		# self.Util_Matrix = [[1, 0, 0, 0],[3, 0, 0, 0],[9, 0, 0, 0],[27, 0, 0, 0]]                 # Matrix to calculate utility for smallboard
		self.boardHash = long(0)                                                                  # Hash for board                      
		self.blockHash = [[[long(0) for j in xrange(3)] for i in xrange(3)] for k in xrange(2)]   # Hash for blocks
		self.blockpoint = 10000;                                                                      # Points for winning a block
		self.boardHeuriStore = {}                                                                 # Dictionary to store hash values and heuristic for board
		self.blockHeuriStore = {}                                                                 # Dictionary to store hash values and heuristic for 3 * 3 block 
		# self.patterns = [];                                                                       # Patterns for winning in smallboard
		self.blockH = [[[[long(0) for i in xrange(3)] for j in xrange(3)] for k in xrange(2)] for l in xrange(2)]
		# # Straight Line Patterns (for both rows and columns)
		# for i in xrange(3):
		#     row_array = [];                            # For the i th row
		#     col_array = [];                            # For i th column
		#     for j in xrange(3):
		#         row_array.append((i, j));
		#         col_array.append((j, i));
		#     self.patterns.append(row_array);
		#     self.patterns.append(col_array);    
				
		# diagonal1_array = [(0, 0), (1, 1), (2, 2)];    # Pattern for first diagonal
		# diagonal2_array = [(2, 0), (1, 1), (0, 2)];    # Pattern for second diagonal

		# self.patterns.append(diagonal1_array);
		# self.patterns.append(diagonal2_array);

		# Hash for each (position(x, y), board, player)
		self.rand_table = [[[[long(0) for i in xrange(2)] for j in xrange(9)] for k in xrange(9)] for l in xrange(2)]
		
		self.hash_init();
				
		# big_boards_status is the game board
		# small_boards_status shows which small_boards have been won/drawn and by which player
		self.big_boards_status = ([['-' for i in range(9)] for j in range(9)], [['-' for i in range(9)] for j in range(9)])
		self.small_boards_status = ([['-' for i in range(3)] for j in range(3)], [['-' for i in range(3)] for j in range(3)])

	# Initialise the values of rand_table to random values
	def hash_init(self):
		
		for i in xrange(9):
			for j in xrange(9):
				for k in xrange(2):
					for l in xrange(2):
						self.rand_table[k][i][j][l] = long(random.randint(1, 2**64));

	# NOT operation on flag
	def oppFlag(self, flag):
		
		return 'o' if flag == 'x' else 'x'

	# Calculate updated board and block hash after making the move in cell                  
	def addMovetoHash(self, cell, player):

		# cell[0] = board number, cell[1] = x, cell[2] = y
		# Player = 0 means oponent, player = 1 means us

		# Updating Hash for board and block
		self.boardHash ^= self.rand_table[cell[0]][cell[1]][cell[2]][player];
		self.blockHash[cell[0]][cell[1] / 3][cell[2] / 3] ^= self.rand_table[cell[0]][cell[1]][cell[2]][player];

	def sig_handler(self, signum, frame):
		raise Exception("timeout")

	def find_valid_move_cells(self, old_move):
		#returns the valid cells allowed given the last move and the current board state
		
		allowed_cells = []
		allowed_small_board = [old_move[1] % 3, old_move[2] % 3]
		#checks if the move is a free move or not based on the rules

		if old_move == (-1, -1, -1) or (self.small_boards_status[0][allowed_small_board[0]][allowed_small_board[1]] != '-' and self.small_boards_status[1][allowed_small_board[0]][allowed_small_board[1]] != '-'):
			for k in range(2):
				for i in range(9):
					for j in range(9):
						if self.big_boards_status[k][i][j] == '-' and self.small_boards_status[k][i/3][j/3] == '-':
							allowed_cells.append((k,i,j))

		else:
			for k in range(2):
				if self.small_boards_status[k][allowed_small_board[0]][allowed_small_board[1]] == "-":
					for i in range(3*allowed_small_board[0], 3*allowed_small_board[0]+3):
						for j in range(3*allowed_small_board[1], 3*allowed_small_board[1]+3):
							if self.big_boards_status[k][i][j] == '-':
								allowed_cells.append((k,i,j))

		return allowed_cells    

	def find_terminal_state(self,board):
		#checks if the game is over(won or drawn) and returns the player who have won the game or the player who has higher small_boards in case of a draw

		cntx = 0
		cnto = 0
		cntd = 0
	
		for k in range(2):
			bs = board.small_boards_status[k]
			for i in range(3):
				for j in range(3):
					if bs[i][j] == 'x':
						cntx += 1
					if bs[i][j] == 'o':
						cnto += 1
					if bs[i][j] == 'd':
						cntd += 1
			for i in range(3):
				row = bs[i]
				col = [x[i] for x in bs]
				#print row,col
				#checking if i'th row or i'th column has been won or not
				if (row[0] =='x' or row[0] == 'o') and (row.count(row[0]) == 3):
					return (row[0],'WON')
				if (col[0] =='x' or col[0] == 'o') and (col.count(col[0]) == 3):
					return (col[0],'WON')
			#check diagonals
			if(bs[0][0] == bs[1][1] == bs[2][2]) and (bs[0][0] == 'x' or bs[0][0] == 'o'):
				return (bs[0][0],'WON')
			if(bs[0][2] == bs[1][1] == bs[2][0]) and (bs[0][2] == 'x' or bs[0][2] == 'o'):
				return (bs[0][2],'WON')

		if cntx+cnto+cntd < 18:     #if all small_boards have not yet been won, continue
			return ('CONTINUE', '-')
		elif cntx+cnto+cntd == 18:                          #if game is drawn
			return ('NONE', 'DRAW')

	def update(self, old_move, new_move, ply, board):
		#updating the game board and small_board status as per the move that has been passed in the arguements
		
		board.big_boards_status[new_move[0]][new_move[1]][new_move[2]] = ply

		x = new_move[1]/3
		y = new_move[2]/3
		k = new_move[0]
		fl = 0

		#checking if a small_board has been won or drawn or not after the current move
		bs = board.big_boards_status[k]
		for i in range(3):
			#checking for horizontal pattern(i'th row)
			if (bs[3*x+i][3*y] == bs[3*x+i][3*y+1] == bs[3*x+i][3*y+2]) and (bs[3*x+i][3*y] == ply):
				board.small_boards_status[k][x][y] = ply
				return 'SUCCESSFUL', True
			#checking for vertical pattern(i'th column)
			if (bs[3*x][3*y+i] == bs[3*x+1][3*y+i] == bs[3*x+2][3*y+i]) and (bs[3*x][3*y+i] == ply):
				board.small_boards_status[k][x][y] = ply
				return 'SUCCESSFUL', True
		#checking for diagonal patterns
		#diagonal 1
		if (bs[3*x][3*y] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y+2]) and (bs[3*x][3*y] == ply):
			board.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#diagonal 2
		if (bs[3*x][3*y+2] == bs[3*x+1][3*y+1] == bs[3*x+2][3*y]) and (bs[3*x][3*y+2] == ply):
			board.small_boards_status[k][x][y] = ply
			return 'SUCCESSFUL', True
		#checking if a small_board has any more cells left or has it been drawn
		for i in range(3):
			for j in range(3):
				if bs[3*x+i][3*y+j] =='-':
					return 'SUCCESSFUL', False
		board.small_boards_status[k][x][y] = 'd'
		return 'SUCCESSFUL', False

	#Function to calculate utility of both the boards together    
	def board_heuristic(self, board, flag):

		ans = [0,0]
		#Calculation for rows
		for k in xrange(2):
			countp = 0
			counto = 0
			countd = 0
			for i in xrange(3):
				for j in xrange(3):
					if board.small_boards_status[k][i][j] == flag:
						countp += 1
					elif board.small_boards_status[k][i][j] == self.oppFlag(flag):
						counto += 1
					elif board.small_boards_status[k][i][j] == 'd':
						countd += 1
				if countd == 0:
					if counto != 0 and countp == 0:
						value = 0;
						for j in xrange(3):
							if board.small_boards_status[k][i][j] == self.oppFlag(flag):
								value += 4;
							else:
								value += self.blockH[0][k][i][j] - self.blockH[1][k][i][j] 

						ans[k] += - (2**value + value**2)

					elif countp != 0 and counto == 0:    
						value = 0;
						for j in xrange(3):
							if board.small_boards_status[k][i][j] == flag:
								value += 4;
							else:
								value += self.blockH[1][k][i][j] - self.blockH[0][k][i][j] 

						ans[k] += (2**value + value**2)

		#Calculation for columns
		for k in xrange(2):
			countp = 0
			counto = 0
			countd = 0
			for j in xrange(3):
				for i in xrange(3):
					if board.small_boards_status[k][i][j] == flag:
						countp += 1
					elif board.small_boards_status[k][i][j] == self.oppFlag(flag):
						counto += 1
					elif board.small_boards_status[k][i][j] == 'd':
						countd += 1
				if countd == 0:
					if counto != 0 and countp == 0:
						value = 0;
						for i in xrange(3):
							if board.small_boards_status[k][i][j] == self.oppFlag(flag):
								value += 4;
							else:
								value += self.blockH[0][k][i][j] - self.blockH[1][k][i][j] 

						ans[k] += - (2**value + value**2)

					elif countp != 0 and counto == 0:    
						value = 0;
						for i in xrange(3):
							if board.small_boards_status[k][i][j] == flag:
								value += 4;
							else:
								value += self.blockH[1][k][i][j] - self.blockH[0][k][i][j] 

						ans[k] += (2**value + value**2)
		#Calculation for first diagonal
		for k in xrange(2):
			countp = 0
			counto = 0
			countd = 0
			for i in xrange(3):
				if board.small_boards_status[k][i][i] == flag:
					countp += 1
				elif board.small_boards_status[k][i][i] == self.oppFlag(flag):
					counto += 1
				elif board.small_boards_status[k][i][i] == 'd':
					countd += 1
			if countd == 0:
				if counto != 0 and countp == 0:
					value = 0;
					for i in xrange(3):
						if board.small_boards_status[k][i][i] == self.oppFlag(flag):
							value += 4;
						else:
							value += self.blockH[0][k][i][i] - self.blockH[1][k][i][j] 

					ans[k] += - (2**value + value**2)

				elif countp != 0 and counto == 0:    
					value = 0;
					for j in xrange(3):
						if board.small_boards_status[k][i][i] == flag:
							value += 4;
						else:
							value += self.blockH[1][k][i][i] - self.blockH[0][k][i][j] 

					ans[k] += (2**value + value**2)

		#Calculation for second diagonal
		for k in xrange(2):
			countp = 0
			counto = 0
			countd = 0
			for i in xrange(3):
				if board.small_boards_status[k][i][2 - i] == flag:
					countp += 1
				elif board.small_boards_status[k][i][2 - i] == self.oppFlag(flag):
					counto += 1
				elif board.small_boards_status[k][i][2 - i] == 'd':
					countd += 1
			if countd == 0:
				if counto != 0 and countp == 0:
					value = 0;
					for j in xrange(3):
						if board.small_boards_status[k][2-j][j] == self.oppFlag(flag):
							value += 4;
						else:
							value += self.blockH[0][k][2-j][j] - self.blockH[1][k][i][j] 

					ans[k] += - (2**value + value**2)

				elif countp != 0 and counto == 0:    
					value = 0;
					for j in xrange(3):
						if board.small_boards_status[k][2-j][j] == flag:
							value += 4;
						else:
							value += self.blockH[1][k][2-j][j] - self.blockH[0][k][i][j] 

					ans[k] += (2**value + value**2)
		return max(ans[0],ans[1])**2 + min(ans[0],ans[1]);   

	# Function to calculate utility of a single 3 * 3 smallboard    
	def block_heuristic(self, block, flag, start_x, start_y, board_num):

		loseSteps = 4;
		winSteps = 4;

		loseHash = [0 for i in xrange(5)];
		winHash = [0 for i in xrange(5)];

		# Calculation for rows
		for i in xrange(3):
			count1 = 0;
			count2 = 0;
			for j in xrange(3):
				if block.big_boards_status[board_num][i+start_x][j+start_y] == self.who:
					count1 += 1;
				elif block.big_boards_status[board_num][i+start_x][j+start_y] == self.oppFlag(self.who):
					count2 += 1;
			if count2 == 0:
				winSteps = min(winSteps, 3 - count1);
				winHash[3 - count1] += 1;    

			if count1 == 0:
				loseSteps = min(loseSteps, 3 - count2);
				loseHash[3 - count2] += 1;

		# Calculation for columns            
		for j in xrange(3):
			count1 = 0;
			count2 = 0;
			for i in xrange(3):
				if block.big_boards_status[board_num][i+start_x][j+start_y] == self.who:
					count1 += 1;
				elif block.big_boards_status[board_num][i+start_x][j+start_y] == self.oppFlag(self.who):
					count2 += 1;
			if count2 == 0:
				winSteps = min(winSteps, 3 - count1);
				winHash[3 - count1] += 1;    

			if count1 == 0:
				loseSteps = min(loseSteps, 3 - count2);
				loseHash[3 - count2] += 1;          

		# Calculation for first diagonal            
		count1 = 0;
		count2 = 0;
		for i in xrange(3):
			if block.big_boards_status[board_num][i+start_x][i+start_y] == self.who:
				count1 += 1;
			elif block.big_boards_status[board_num][i+start_x][i+start_y] == self.oppFlag(self.who):
				count2 += 1;
		if count2 == 0:
				winSteps = min(winSteps, 3 - count1);
				winHash[3 - count1] += 1;    

		if count1 == 0:
			loseSteps = min(loseSteps, 3 - count2);
			loseHash[3 - count2] += 1;

		# Calculation for second diagonal            
		count1 = 0;
		count2 = 0;
		for i in xrange(3):
			if block.big_boards_status[board_num][i+start_x][2+start_y - i] == self.who:
				count1 += 1;
			elif block.big_boards_status[board_num][i+start_x][2+start_y - i] == self.oppFlag(self.who):
				count2 += 1;
		if count2 == 0:
				winSteps = min(winSteps, 3 - count1);
				winHash[3 - count1] += 1;    

		if count1 == 0:
			loseSteps = min(loseSteps, 3 - count2);
			loseHash[3 - count2] += 1;

		self.blockH[0][board_num][start_x / 3][start_y / 3] = winSteps
		self.blockH[1][board_num][start_x / 3][start_y / 3] = loseSteps

		# print winSteps, loseSteps
		return winSteps,loseSteps;                                         

	def count1(self,board):
		ans = 0
		for k in xrange(2):
			for i in xrange(3):
				for j in xrange(3):
					if board.small_boards_status[k][i][j] != '-':
						ans += 1
		return ans        

	def count(self,flag,board_num, board):
		output = 0;
		for i in xrange(9):
			for j in xrange(9):
				if board.big_boards_status[board_num][i][j] == self.who:
					output +=1;
		return output;
	
	# Function to assign heuristic value to a board state   
	def heuristic(self, flag, board,cell):
		[win1,lose1] = self.block_heuristic(board,flag,(cell[1]/3) * 3,(cell[2]/3) * 3,cell[0]);
		mybonus = 0;
		dontchoose = 0;
		if win1 == 4 and lose1 == 4:
			dontchoose = 1;
		prev = self.count1(board)
		self.update([1, 1, 1], cell, flag, board)
		new = self.count1(board)
		mybonus = new-prev;

		checkGoal = self.find_terminal_state(board)
		if checkGoal[1] == 'WON':
			if checkGoal[0] == self.who:
				return 10000000000

		oppbonus = 0;
		validCell = board.find_valid_move_cells(cell)

		if len(validCell) > 18:
			return -10000000000

		for i in xrange(len(validCell)):
			board1 = deepcopy(board)
			prevopp = self.count1(board1)
			self.update(cell,validCell[i],self.oppFlag(flag),board1)
			newopp = self.count1(board1)
			checkGoal = self.find_terminal_state(board1)
			if checkGoal[1] == 'WON':
				if checkGoal[0] == self.who:
					return 100000000000
				else:
					return -100000000000
			if newopp - prevopp > 0:
				valid = board1.find_valid_move_cells(validCell[i])
				for j in xrange(len(valid)):
					board2 = deepcopy(board1)
					self.update(validCell[i],valid[j],self.oppFlag(flag),board2)
					checkGoal = self.find_terminal_state(board2)
					if checkGoal[1] == 'WON':
						if checkGoal[0] == self.who:
							return 100000000000
						else:
							return -10000000000
					del board2
			del board1

		[win2,lose2] = self.block_heuristic(board,flag,(cell[1]/3) * 3,(cell[2]/3) * 3,cell[0]);
		[win3, lose3] = self.block_heuristic(board,flag,(cell[1] % 3) * 3,(cell[2] % 3) * 3, 0);
		[win4, lose4] = self.block_heuristic(board,flag,(cell[1] % 3) * 3,(cell[2] % 3) * 3, 1);
		if lose3 == 0:
			lose3 = 4
		if lose4 == 0:
			lose4 = 4
		return 12 * (win1-win2) + 10 * (lose2 - lose1) + 10*self.count(flag,cell[0],board) + 10*min(lose3, lose4) -1000*dontchoose;
							
	# Minimax function with alpha - beta prunnning to explore achievable states in time limit   
	def minimax(self, board, flag, depth, maxDepth, alpha, beta, old_move):

		validCells = board.find_valid_move_cells(old_move)
		random.shuffle(validCells)
		checkGoal = self.find_terminal_state(board)

		if checkGoal[1] == 'WON':
			if checkGoal[0] == self.who:
				return float("inf"),validCells[random.randrange(len(validCells))]
			else:
				return float("-inf"),validCells[random.randrange(len(validCells))]
		elif checkGoal[1] == 'DRAW':
			return 0, validCells[random.randrange(len(validCells))]
		
		if depth == maxDepth:
			maxv =float("-inf");
			ind = 0;
			for i in xrange(len(validCells)):
				heurist = self.heuristic(flag,deepcopy(board),validCells[i]);
				if maxv < heurist:
					maxv = heurist;
					ind = i
			return maxv , validCells[ind];

		if flag == self.who:
			isMax = 1;
		else: 
			isMax = 0;

		if self.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.who:
			isMax = 1;

		if isMax:
			maxVal = float("-inf")
			maxInd = 0
			for i in xrange(len(validCells)):

				cell = validCells[i]
				self.update(old_move, cell, flag, board)
				self.addMovetoHash(cell, 1)

				val = self.minimax(board,self.oppFlag(flag),depth+1,maxDepth,alpha,beta,cell)[0]

				if val > maxVal:
					maxVal = val
					maxInd = i
				if maxVal > alpha:
					alpha = maxVal

				board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
				board.small_boards_status[cell[0]][cell[1] / 3][cell[2] / 3] = '-'

				if (time() - self.startTime) > self.timeLimit:
					return 0, validCells[0]
				self.addMovetoHash(cell,1)
				if beta <= alpha:
					break
			return maxVal, validCells[maxInd]

		else:
			minVal = float("inf")
			minInd = 0
			for i in xrange(len(validCells)):

				cell = validCells[i]
				self.update(old_move, cell, flag, board)
				self.addMovetoHash(cell, 0)

				val = self.minimax(board,self.oppFlag(flag),depth+1,maxDepth,alpha,beta,cell)[0]

				if val < minVal:
					minVal = val
					minInd = i
				if minVal < beta:
					beta = minVal

				board.big_boards_status[cell[0]][cell[1]][cell[2]] = '-'
				board.small_boards_status[cell[0]][cell[1] / 3][cell[2] / 3] = '-'

				if (time() - self.startTime) > self.timeLimit:
					return 0, validCells[0]
				
				self.addMovetoHash(cell,0)
				if beta <= alpha:
					break
			return minVal,  validCells[minInd]

	def move(self, board, old_move, flag):
		self.startTime = time()

		if old_move == (-1, -1, -1):
			self.addMovetoHash((0 ,1, 1), 1)
			return (0, 0, 0)
		else:
			if board.big_boards_status[old_move[0]][old_move[1]][old_move[2]] == self.oppFlag(flag):
				self.addMovetoHash(old_move, 0)

		self.who = flag

		maxDepth = 1

		validCells = board.find_valid_move_cells(old_move)
		random.shuffle(validCells)
		bestMove = validCells[0]
		try:
			self.boardHashSafeCopy = self.boardHash
			self.blockHashSafeCopy = deepcopy(self.blockHash)
			b = deepcopy(board)
			if (time() - self.startTime) < self.timeLimit:
				move = self.minimax(b, flag, 1, maxDepth, float("-inf"), float("inf"), old_move)[1]
				if (time() - self.startTime) < self.timeLimit:
					bestMove = move
				maxDepth += 1   
			del b
			self.addMovetoHash( bestMove, 1);
		except:
			pass
		return bestMove