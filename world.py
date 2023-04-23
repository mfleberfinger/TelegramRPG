import items
import math
import monsters
import random


def clamp(num, minVal, maxVal):
	if num < minVal:
		return minVal
	if num > maxVal:
		return maxVal
	return num


class Place:
	
	def __init__(self, name, baseNoun, difficulty):
		self.name = name
		self.baseNoun = baseNoun # Used to make "similar" places spawn near each other.
		self.difficulty = difficulty
		self.monsterList = list()
		self.lootList = list()


class World():
	
	# Typically, would probably want to write things in a way that controls
	# generation with a global seed and doesn't save everything that's generated.
	# However, I want to save everything to prevent reuse of names across places,
	# make items and monsters with the same names have the same stats
	# across places, and avoid having to generate everything at the start of the
	# game and for a preset number of places.
	def __init__(self):
		self.map = {(0, 0): Place("town", "town", 0)}
		self.usedPlaceNames = {"town"}
		self.usedMonsterNames = set()
		self.usedItemNames = set()
		self.loadWordLists()
	
	def getPlace(self, coordinates):
		if coordinates not in self.map:
			self.map[coordinates] = self.__generatePlace(coordinates)
		return self.map[coordinates]

	def __generatePlace(self, coordinates):
		difficulty = World.__generateDifficulty(coordinates)
		name = ""
		baseNoun = ""
		similar = 3
		# Generate place names for the given coordinates until a unique name is generated.
		while name == "":
			(name, baseNoun) = self.__generatePlaceName(coordinates, similar)
			if name not in self.usedPlaceNames:
				self.usedPlaceNames.add(name)
			else:
				name = ""
				# Increase the number of place nouns being considered if we fail
				# to create a unique name.
				similar += 1
		place = Place(name, baseNoun, difficulty)
		# Generate a list of monsters to spawn in the new place.
		place.monsterList = self.__generateMonsterList(difficulty)
		# Generate a list of loot to be dropped by monsters in the new place.
		place.lootList = self.__generateLootList(difficulty)
		return place
	
	# Generate a unique (not in self.usedPlaceNames) place name.
	# similar: How far away can place nouns be from each other in a list and still be
	# considered "similar?"
	def  __generatePlaceName(self, coordinates, similar):
		# 1/ADJECTIVE_CHANCE of using an adjective.
		ADJECTIVE_CHANCE = 4
		# 1/POSTFIX_CHANCE of using a postfix.
		POSTFIX_CHANCE = 4
		# Sometimes we will add a random value to the distance from the nearby noun
		# to avoid just randomly reusing a small number of nouns.
		DISCONTINUITY_CHANCE = 4
		DISCONTINUITY_MAX = 7
		# Pick a place noun similar existing nearby places (if there are any).
		# We can just randomly choose one of the existing places for this check.
		nearbyCoordList = []
		for x in range(-1,2):
			for y in range(-1,2):
				point = (x + coordinates[0], y + coordinates[1])
				if point in self.map and point != coordinates:
					nearbyCoordList.append(point)
		nearbyPlace = self.map[random.choice(nearbyCoordList)]
		# Where is the nearby place's noun in the noun list (there can be more than
		# one copy of the noun in the list)?
		nearbyNounIndices = self.placeNounDict[nearbyPlace.baseNoun]
		nearbyNounIndex = random.choice(nearbyNounIndices)
		newNounIndex = nearbyNounIndex + random.randrange(-similar, similar)
		# To avoid just moving back and forth in a small part of the place noun
		# list, randomly apply a multiplier to jump to dissimilar places.
		if random.randrange(DISCONTINUITY_CHANCE) == 0:
			newNounIndex += random.randrange(1,DISCONTINUITY_MAX)
		newNounIndex = newNounIndex % len(self.placeNounsBySimilarity)
		noun = self.placeNounsBySimilarity[newNounIndex]
		# Decide whether to use an adjective and choose one if yes.
		adjective = ""
		if random.randrange(ADJECTIVE_CHANCE) == 0:
			adjective = random.choice(self.placeAdjectives) + " "
		# Decide whether to use a postfix and choose one if yes.
		postfix = ""
		if random.randrange(POSTFIX_CHANCE) == 0:
			postfix = " " + random.choice(self.postfixes)
		return ((adjective + noun + postfix), noun)
	
	# Return an int based on distance from (0, 0), with some random variation.
	def __generateDifficulty(coordinates):
		# We'll generate difficulty using a normal/gaussian distribution.
		STD_DEV = 3
		distance = coordinates[0] * coordinates[0] + coordinates[1] * coordinates[1]
		distance = math.sqrt(distance)
		meanDifficulty = distance / 20
		difficulty = round(meanDifficulty + random.gauss(meanDifficulty, STD_DEV))
		if difficulty < 1:
			difficulty = 1
		return difficulty
	
	def testGenerateMonsterList(self, difficulty):
		return self.__generateMonsterList(difficulty)
	
	# Generate a list of monsters to spawn based on difficulty.
	def __generateMonsterList(self, difficulty):
		maxHp = difficulty * 35
		minHp = math.ceil(maxHp / 2) # ceiling to make hp > 0
		maxPower = difficulty
		minPower = round(maxPower / 2) # May be 0 at low difficulty. This is acceptable.
		monsterList = []
		for i in range(10): # Generate 10 unique monsters for this place.
			# Generate monster names for the given difficulty until a unique
			# name is generated.
			name = ""
			while name == "":
				name = self.__generateMonsterName(difficulty)
				if name not in self.usedMonsterNames:
					self.usedMonsterNames.add(name)
				else:
					name = ""
			hp = random.randrange(minHp, maxHp + 1)
			power = random.randrange(minPower, maxPower + 1)
			# Player xp required to level up: previousRequirement + round(previousRequirement * 1.1)
			# Monster xp reward at difficulty level N: round(30 * math.pow(1.085, N))
			xpReward = round(30 * math.pow(1.085, difficulty))
			monsterList.append(monsters.Monster(name, hp, power, xpReward))
		return monsterList
	
	def __generateMonsterName(self, difficulty):
		# 1/ADJECTIVE_CHANCE of using an adjective.
		ADJECTIVE_CHANCE = 4
		# 1/POSTFIX_CHANCE of using a postfix.
		POSTFIX_CHANCE = 4
		# Mean and standard deviation used to generate random numbers with a
		# normal (Gaussian) distribution. The mean should be index of the average
		# monster for an area. Standard deviation gives the "typical" spread of
		# monsters in an area. Weird outliers are possible and desirable.
		# Mean will range from the index 10% of the way up the list at difficulty
		# 1 to 90% of the way up the list at difficulty at or above 100.
		# This will be a linear relationship... y = mx + b
		m = 80 / 99
		b = 90 - (8000 / 99)
		percentOfList = clamp(round(m * difficulty + b), 10, 90)
		mean = math.floor((percentOfList / 100) * len(self.monsterNounsByPower))
		# Standard deviation will be 1/13 of the list's length.
		stdDev = round(len(self.monsterNounsByPower) / 13)
		nounIndex = clamp(round(random.gauss(mean, stdDev)), 0, len(self.monsterNounsByPower) - 1)
		noun = self.monsterNounsByPower[nounIndex]
		# Decide whether to use an adjective and choose one if yes.
		adjective = ""
		if random.randrange(ADJECTIVE_CHANCE) == 0:
			adjective = random.choice(self.monsterAdjectives) + " "
		# Decide whether to use a postfix and choose one if yes.
		postfix = ""
		if random.randrange(POSTFIX_CHANCE) == 0:
			postfix = " " + random.choice(self.postfixes)
		return adjective + noun + postfix
	
	def __generateLootList(self, difficulty):
		lootList = []
		for i in range(10):
			lootList.append(self.__generateItem(difficulty))
		return lootList
	
	def testGenerateItem(self, difficulty):
		return self.__generateItem(difficulty)
	
	def __generateItem(self, difficulty):
		# Give consumables the greatest chance of spawning, followed by armor, followed by weapons.
		CONSUMABLE_CHANCE = 6 # 6/15 = 3/5 chance of consumable
		ARMOR_CHANCE = 5 # 5/15 = 1/3 chance of armor
		WEAPON_CHANCE = 4 # 4/15 chance of weapon
		sumOfChances = CONSUMABLE_CHANCE + ARMOR_CHANCE + WEAPON_CHANCE
		randomNumber = random.randrange(sumOfChances)
		item = None
		# Generate consumable.
		if randomNumber < CONSUMABLE_CHANCE:
			item = self.__generateConsumable(difficulty)
		# Generate armor.
		elif randomNumber < CONSUMABLE_CHANCE + ARMOR_CHANCE - 1:
			item = self.__generateArmor(difficulty)
		#Generate weapon.
		else:
			item = self.__generateWeapon(difficulty)
		return item
	
	def testGenerateConsumable(self, difficulty):
		return self.__generateConsumable(difficulty)
	
	def testGenerateArmor(self, difficulty):
		return self.__generateArmor(difficulty)
		
	def testGenerateWeapon(self, difficulty):
		return self.__generateWeapon(difficulty)
	
	def __generateConsumable(self, difficulty):
		maxHp = difficulty * 17
		minHp = round(maxHp / 2) # May be 0 at low difficulty. This is acceptable.
		sellValue = random.randrange(difficulty, 2 * difficulty)
		hp = random.randrange(minHp, maxHp + 1)
		name = ""
		while name == "":
			name = self.__generateConsumableName()
			if name in self.usedItemNames:
				name = ""
			else:
				self.usedItemNames.add(name)
		return items.Consumable(name, hp, sellValue)
	
	def __generateArmor(self, difficulty):
		maxHp = difficulty * 10
		minHp = round(maxHp / 2) # May be 0 at low difficulty. This is acceptable.
		sellValue = random.randrange(difficulty, 2 * difficulty)
		hp = random.randrange(minHp, maxHp + 1)
		bodyPart = random.choice([items.Equipment.TORSO, items.Equipment.HEAD, items.Equipment.LEGS])
		name = ""
		while name == "":
			name = self.__generateArmorName(bodyPart, difficulty)
			if name in self.usedItemNames:
				name = ""
			else:
				self.usedItemNames.add(name)
		return items.Armor(name, bodyPart, hp, sellValue)
	
	def __generateWeapon(self, difficulty):
		maxPower = difficulty
		minPower = round(difficulty / 2) # May be 0 at low difficulty. This is acceptable.
		sellValue = random.randrange(difficulty, 2 * difficulty)
		power = random.randrange(minPower, maxPower + 1)
		name = ""
		while name == "":
			name = self.__generateWeaponName()
			if name in self.usedItemNames:
				name = ""
			else:
				self.usedItemNames.add(name)
		return items.Weapon(name, power, sellValue)
	
	def testGenerateConsumableName(self):
		return self.__generateConsumableName()
	
	def testGenerateArmorName(self, bodyPart, difficulty):
		return self.__generateArmorName(bodyPart, difficulty)
		
	def testGenerateWeaponName(self):
		return self.__generateWeaponName()
	
	def __generateConsumableName(self):
		# 1/ADJECTIVE_CHANCE of using an adjective.
		ADJECTIVE_CHANCE = 4
		# 1/ADVERB_CHANCE of using an adverb, if an adjective was used.
		ADVERB_CHANCE = 4
		# 1/POSTFIX_CHANCE of using a postfix.
		POSTFIX_CHANCE = 4
		noun = random.choice(self.healingItemNouns)
		adjective = ""
		adverb = ""
		if random.randrange(ADJECTIVE_CHANCE) == 0:
			adjective = random.choice(self.itemAdjectives) + " "
			if random.randrange(ADVERB_CHANCE) == 0:
				adverb = random.choice(self.adverbs) + " "
		postfix = ""
		if random.randrange(POSTFIX_CHANCE) == 0:
			postfix = " " + random.choice(self.postfixes)
		return adverb + adjective + noun + postfix
	
	def __generateArmorName(self, bodyPart, difficulty):
		# 1/ADJECTIVE_CHANCE of using an adjective.
		ADJECTIVE_CHANCE = 4
		# 1/ADVERB_CHANCE of using an adverb, if an adjective was used.
		ADVERB_CHANCE = 4
		# 1/POSTFIX_CHANCE of using a postfix.
		POSTFIX_CHANCE = 4
		# Mean and standard deviation used to generate random numbers with a
		# normal (Gaussian) distribution. This works in the same way as monster
		# name generation.
		m = 80 / 99
		b = 90 - (8000 / 99)
		percentOfList = clamp(round(m * difficulty + b), 10, 90)
		nounList = []
		if bodyPart == items.Equipment.TORSO:
			nounList = self.torsoEquipmentNounsByProtection
		elif bodyPart == items.Equipment.HEAD:
			nounList = self.headEquipmentNounsByProtection
		else: #items.Equipment.LEGS
			nounList = self.legEquipmentNounsByProtection
		mean = math.floor((percentOfList / 100) * len(nounList))
		# Standard deviation will be 1/13 of the list's length.
		stdDev = round(len(nounList) / 13)
		nounIndex = clamp(round(random.gauss(mean, stdDev)), 0, len(nounList) - 1)
		noun = nounList[nounIndex]
		adjective = ""
		adverb = ""
		if random.randrange(ADJECTIVE_CHANCE) == 0:
			adjective = random.choice(self.itemAdjectives) + " "
			if random.randrange(ADVERB_CHANCE) == 0:
				adverb = random.choice(self.adverbs) + " "
		postfix = ""
		if random.randrange(POSTFIX_CHANCE) == 0:
			postfix = " " + random.choice(self.postfixes)
		return adverb + adjective + noun + postfix
	
	def __generateWeaponName(self):
		# 1/ADJECTIVE_CHANCE of using an adjective.
		ADJECTIVE_CHANCE = 4
		# 1/ADVERB_CHANCE of using an adverb, if an adjective was used.
		ADVERB_CHANCE = 4
		# 1/POSTFIX_CHANCE of using a postfix.
		POSTFIX_CHANCE = 4
		noun = random.choice(self.weaponNouns)
		adjective = ""
		adverb = ""
		if random.randrange(ADJECTIVE_CHANCE) == 0:
			adjective = random.choice(self.itemAdjectives) + " "
			if random.randrange(ADVERB_CHANCE) == 0:
				adverb = random.choice(self.adverbs) + " "
		postfix = ""
		if random.randrange(POSTFIX_CHANCE) == 0:
			postfix = " " + random.choice(self.postfixes)
		return adverb + adjective + noun + postfix
	
	# This should be called every time the program starts, in case new words were
	# added. We don't want to rely on what we have in the saved state because it
	# these lists might change. I should probably not save the word lists in the
	# save state but that takes more effort than just shoving everything into
	# one big object ¯\_(ツ)_/¯
	def loadWordLists(self):
		with open("wordLists/monsterAdjectives.txt") as f:
			self.monsterAdjectives = f.read().split("\n")
		with open("wordLists/adverbs.txt") as f:
			self.adverbs = f.read().split("\n")
		with open("wordLists/monsterNounsByPower.txt") as f:
			self.monsterNounsByPower = f.read().split("\n")
		with open("wordLists/placeAdjectives.txt") as f:
			self.placeAdjectives = f.read().split("\n")
		with open("wordLists/headEquipmentNounsByProtection.txt") as f:
			self.headEquipmentNounsByProtection = f.read().split("\n")
		with open("wordLists/placeNounsBySimilarity.txt") as f:
			self.placeNounsBySimilarity = f.read().split("\n")
		with open("wordLists/healingItemNouns.txt") as f:
			self.healingItemNouns = f.read().split("\n")
		with open("wordLists/postfixes.txt") as f:
			self.postfixes = f.read().split("\n")
		with open("wordLists/itemAdjectives.txt") as f:
			self.itemAdjectives = f.read().split("\n")
		with open("wordLists/torsoEquipmentNounsByProtection.txt") as f:
			self.torsoEquipmentNounsByProtection = f.read().split("\n")
		with open("wordLists/legEquipmentNounsByProtection.txt") as f:
			self.legEquipmentNounsByProtection = f.read().split("\n")
		with open("wordLists/weaponNouns.txt") as f:
			self.weaponNouns = f.read().split("\n")
		# Dictionary of lists of indices to locate all instances of a place noun
		# in self.placeNounsBySimilarity for the purpose of naming nearby places
		# "similarly."
		self.placeNounDict = dict()
		for i in range(0, len(self.placeNounsBySimilarity)):
			if self.placeNounsBySimilarity[i] in self.placeNounDict:
				self.placeNounDict[self.placeNounsBySimilarity[i]].append(i)
			else:
				self.placeNounDict[self.placeNounsBySimilarity[i]] = [i]
