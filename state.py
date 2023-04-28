import items
import os
import pickle
import player
import world



class State:

	SAVE_DIRECTORY = "savedGames/"

	def __init__(self, saveName):
		self.saveName = saveName
		# If a file for the save name already exists, load it.
		if os.path.isfile(State.SAVE_DIRECTORY + saveName):
			loadedState = self.load()
			self.player = loadedState.player
			self.inventory = loadedState.inventory
			self.world = loadedState.world
			self.newGame = False # If True, the Telegram bot will send an intro message.
		else:
			self.player = player.Player()
			self.inventory = items.Inventory()
			self.world = world.World()
			self.newGame = True
	
	def load(self):
		with open(State.SAVE_DIRECTORY + self.saveName, "rb") as f:
			return pickle.load(f)

	def save(self):
		with open(State.SAVE_DIRECTORY + self.saveName, "w+b") as f:
			return pickle.dump(self, f)
	
	# Probably won't actually need this.
	def delete(self):
		raise NotImplementedError("Delete is not implemted. Maybe you should implement it...?")