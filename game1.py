import numpy as np

class unit_generator:
	def __init__(self,locationx,locationy,ID):
		self.locationx = locationx
		self.locationy = locationy
		self.ID = ID # type of spawner 4 for for AA 5 heli 6 for tank
		self.owner = 0 # 0 no player owns, 1 P1 owns, 2 P2 owns
	def check_owner(self,grid):
		contesting = 0 # used to see if 2 players contest
		for i in range(-1,2):
			for j in range(-1,2):
				x = self.locationx+i
				y = self.locationy+j
				if(grid[x,y] != 0 and not(i==0 and j==0)):
					if(contesting != 0):
						if(contesting == 1 and grid[x,y]>9):
							self.owner = 0
							print('spawner contested no owner')
							return None
						if(contesting == 2 and grid[x,y]<9):
							self.owner = 0
							print('spawner contested no owner')
							return None

					else:
						if(grid[x,y]>9):
							contesting = 2
							print('player 2 contesting at x: %d y: %d' % (x,y))
						else:
							contesting = 1
							print('player 1 contesting at x: %d y: %d' % (x,y))
		self.owner = contesting
		print('player %d owns spawner' % self.owner)		

#must not be next to each other, next to an edge, next to mirror line at y = gridsize/2				
def generator_locations(number,gridsize):
	num_added = 0
	generator_list = []
	while(num_added<number):
		acceptable_coords = 1
		x = int(np.random.rand()*gridsize)
		y = int(np.random.rand()*(gridsize/2-1))
		#is spawner too close to capital?
		if(np.abs(x-gridsize/2)<2 and np.abs(y)<2):
			acceptable_coords=0
		#spawner on edge?
		if(x==0 or y==0 or x==gridsize-1 or y==gridsize-1):
			acceptable_coords=0
		else:
			#is it too close to another spawner?
			for i in range(0,len(generator_list)):
				if(np.abs(x-generator_list[i].locationx)<2 and np.abs(y-generator_list[i].locationy)<2):
					acceptable_coords = 0
		if(acceptable_coords):
			generator_list.append(unit_generator(x,y,int(np.random.rand()*3+4)))
			num_added = num_added+1
	return generator_list
def resolve_combat(unit1,unit2):
	if(unit1 > 9):
		unit1 = unit1/10
	if(unit2 > 9):
		unit2 = unit2/10
	#check error
	if(not(unit1==(np.array([3,2,1]))).any() and not(unit2==(np.array([3,2,1]))).any()):
		print('[ERROR]:resolve_combat called with inputs that are not a unit!')
	#draw
	if(unit1==unit2):
		return 0
	#P2 wins
	if(unit2==unit1-1 or unit1==unit2-2):
		return 2
	#P1 wins
	else:
		return 1							
def setup_game():
	params = np.loadtxt('parameters') 
	# grid values 7 for capital, 6 for tank building, 5 for heli building, 4 for AA building, 3 for tank, 2 for heli, 1 for AA, 0 for empty *1 for P1 stuff *10 for P2 stuff
	grid = np.zeros((int(params[0]),int(params[0])),dtype=int)
	# set capital note other capital set later with array flip 
	grid[int(grid.shape[0]/2),0] = 7
	#set initial tanks
	grid[int(grid.shape[0]/2+1),0]=3
	grid[int(grid.shape[0]/2)-1,0]=3
	grid[int(grid.shape[0]/2),1]=3
	grid = grid + (np.fliplr(grid)*10)
	#set unit spawners
	generator_list = generator_locations(int(params[1]),grid.shape[0])
	tmp_grid = np.zeros((int(params[0]),int(params[0])),dtype=int)
	for i in range(0,len(generator_list)):
		tmp_grid[generator_list[i].locationx,generator_list[i].locationy] = generator_list[i].ID
	tmp_grid = tmp_grid + np.fliplr(tmp_grid)
	grid = grid+tmp_grid
	return grid
def process_turn(grid_num):
	#option for saving every frame or only the last one if 0 load "grid" 
	if(grid_num == 0):
		grid = np.loadtxt('grid',dtype=int)
	else:
		name = 'grid_%d' % grid_num
		grid = np.loadtxt(name,dtype=int)
	grid_size = grid.shape[0]
	#check to see if someone has won
	for i in range(-1,2):
		for j in range(0,2):
			x = int(i + grid_size/2)
			y = j
			if(grid[x,y]>9):
				print('P2 wins')
				return 2
			y = grid_size-j-1
			if(grid[x,y]<4 and grid[x,y] != 0):
				print('P1 wins')
				return 1
	move = np.loadtxt('move',dtype=int)
	player_num = move[0]
	#Is target location valid?
	if(grid[move[1],move[2]] == 0):
		print('Invalid move: attempting to move empty square')
		return -1
	if(grid[move[1],move[2]]<4 and move[0] == 2):
		print('Invalid move: P2 trying to move P1 unit')
		return -1
	if(grid[move[1],move[2]]>9 and move[0] == 1):
		print('Invalid move: P1 trying to move P2 unit')
		return -1
	if(grid[move[1],move[2]] == 7 or grid[move[1],move[2]] == 70):
		print('Invalid move: trying to move capital')
		return -1
	#Is destination valid
	if(grid[move[3],move[4]] == 7 or grid[move[3],move[4]] == 70):
		print('Invalid move: trying to move on top of capital')
		return -1
	if(np.abs(move[3]-move[1])>1 or np.abs(move[4]-move[2])>1):
		print('Invalid move: trying to move too far')
		return -1
	if(grid[move[3],move[4]]==6 or grid[move[3],move[4]]==5 or grid[move[3],move[4]]==4):
		print('Invalid move: destination is unit generator')
		return -1
	if(player_num==2 and (grid[move[3],move[4]]==30 or grid[move[3],move[4]]==20 or grid[move[3],move[4]]==10)):
		print('Invalid move: P2 attempting to move on top of own unit')
		return -1
	if(player_num==1 and (grid[move[3],move[4]]==3 or grid[move[3],move[4]]==2 or grid[move[3],move[4]]==1)):
		print('Invalid move: P1 attempting to move on top of own unit')
		return -1
	#Using a unit generator?
	if(grid[move[1],move[2]]==6 or grid[move[1],move[2]]==5 or grid[move[1],move[2]]==4):
		generator = unit_generator(move[1],move[2],grid[move[1],move[2]])
		generator.check_owner(grid)
		if(generator.owner != player_num):
			print('Invalid move: attempting to use generator not under control')
			return -1
		else:
			#valid generator use and empty square
			if(grid[move[3],move[4]]==0):
				grid[move[3],move[4]]=(generator.ID-3)*(10**(player_num-1))
				np.savetxt('grid',grid,fmt='%d')
				return 0
			#No other option possible, enemy unit present -> cannot use generator, 2 generators cannot be next to each other or capital
			#if other friendly unit at destination then violates previous if
	#Moving unit to empty square
	if(grid[move[3],move[4]]==0):
		grid[move[3],move[4]]=np.copy(grid[move[1],move[2]])
		grid[move[1],move[2]]=0
		np.savetxt('grid',grid,fmt='%d')
		return 0
	#only remaining option is combat
	result = resolve_combat(grid[move[1],move[2]],grid[move[3],move[4]])
	#if draw
	if(result == 0):
		grid[move[3],move[4]]=0
		grid[move[1],move[2]]=0
		np.savetxt('grid',grid,fmt='%d')
		return 0
	#if win
	if(result == 1):
		grid[move[3],move[4]]=np.copy(grid[move[1],move[2]])
		grid[move[1],move[2]]=0
		np.savetxt('grid',grid,fmt='%d')	
		return 0
	#if loss
	else:
		grid[move[1],move[2]]=0
		np.savetxt('grid',grid,fmt='%d')
		return 0		
