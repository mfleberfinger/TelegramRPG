# Script to update the required experience to level up to fit the fixed xp curve.
import math
import pickle

FILENAME = "savedGames/133621483"

with open(FILENAME, "rb+") as f:
	gameState = pickle.load(f)
	player = gameState.player
	# Calculate the correct xp requirement for the next level by starting from
	# the xp requirement for level 2.
	xpReq = 100
	level = player.level
	for i in range(level):
		xpReq += round(100 * math.pow(1.1, level))
	print("fixed xp = " + str(xpReq))
	player.xpForNextLevel = xpReq
	f.seek(0)
	f.truncate()
	pickle.dump(gameState, f)
