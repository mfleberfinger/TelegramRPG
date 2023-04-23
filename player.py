class Player:

	def __init__(self):
		self.maxHp = 100
		self.hp = self.maxHp
		self.power = 2
		# Contains a "constant" from items.Equipment for each equipped item.
		self.equippedSet = set()
		self.xp = 0
		self.xpForNextLevel = 100
		self.level = 1
		self.gold = 0
		self.locationCoords = (0, 0)
		self.placesDiscovered = set()
		self.placesDiscovered.add(self.locationCoords)
		self.monstersKilled = 0
		self.itemsFound = 0
		self.deaths = 0
	
	# Monster xp reward at difficulty level N: round(30 * math.pow(1.085, N))
	# Player xp required to level up: previousRequirement + round(previousRequirement * 1.1)
	def levelUp(self):
		self.level += 1
		self.xpForNextLevel += round(self.xpForNextLevel * 1.1)
		self.power += 1
		self.hp += 50
		self.maxHp += 50