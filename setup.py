import game1
import numpy as np
grid = game1.setup_game()
np.savetxt('grid',grid,fmt='%d')
