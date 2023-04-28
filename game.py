# Ties the various parts of the game together.
# Provides functions that the UI can call to control the game.
import random
import monsters
import items

class Game:
	
	NORTH = "N"
	EAST = "E"
	SOUTH = "S"
	WEST = "W"
	
	# Decide whether a noun should be preceded by "a" or "an" in a sentence.
	def aAn(word):
		if word[0] in ["a", "e", "i", "o", "u"]:
			article = "an"
		else:
			article = "a"
		return article
	
	# Passing state in from the caller so the Telegram bot can manage multiple states.
	def __init__(self, gameState):
		self.gameState = gameState
		self.isInCombat = False
		self.fight = None
		
	# Move the player. Decide whether a monster is encountered and start a fight if so.
	def move(self, direction):
		verb = random.choice(["march", "skip", "stride", "jog", "run", "sprint", "gallop", "hop", "crawl",
							"glide", "walk", "hike", "stroll", "saunter", "slide", "roll", "dance", "frolic",
							"drift", "charge", "rush", "struggle", "wander", "explore", "roam"])
		adverb = random.choice(self.gameState.world.adverbs)
		output = "You {0} {1} ".format(verb, adverb)
		if not self.isInCombat:
			# Move the player.
			coords = self.gameState.player.locationCoords
			if direction == Game.NORTH:
				coords = (coords[0], coords[1] + 1)
				output += "north."
			elif direction == Game.EAST:
				coords = (coords[0] + 1, coords[1])
				output += "east."
			elif direction == Game.SOUTH:
				coords = (coords[0], coords[1] - 1)
				output += "south."
			elif direction == Game.WEST:
				coords = (coords[0] - 1, coords[1])
				output += "west."
			else:
				return "ERROR: Direction invalid."
			place = self.gameState.world.getPlace(coords)
			self.gameState.player.locationCoords = coords
			self.gameState.player.placesDiscovered.add(coords)
			the = ""
			if not place.name[0].isupper():
				the = "the "
			output += "\nYou arrive at {0}{1}.".format(the, place.name)
			# Decide whether to start a fight.
			if coords != (0, 0) and random.randrange(2) == 0:
				output += "\n" + self.__startFight()
		else:
			output = "You're free to leave, but you'll have to admit that you want to flee."
		return output

	def __startFight(self):
		output = ""
		monsterTemplate = random.choice(self.gameState.world.map[self.gameState.player.locationCoords].monsterList)
		monster = monsters.Monster(monsterTemplate.name, monsterTemplate.hp, monsterTemplate.power, monsterTemplate.xpReward)
		self.isInCombat = True
		self.fight = monsters.Fight(self.gameState.player, monster)
		# Generate the output.
		aAn = Game.aAn(monster.name)
		verb = random.choice(["advances towards you", "lunges at you", "charges you", "rushes you", "leaps at you",
							"speeds towards you", "runs at you"])
		adverb = random.choice(self.gameState.world.adverbs)
		output = "You encounter {0} {1}. It {2} {3}!".format(aAn, monster.name, verb, adverb)
		return output

	# list the player's stats
	def stats(self):
		p = self.gameState.player
		# location name
		# level
		# hp/maxHp
		# power
		# xp
		# xp to level up
		# equipment
		# gold
		# places discovered
		# kills
		# deaths
		# items found
		output = (
			"location: {0}\n" +
			"coordinates: {1}\n" +
			"level: {2}\n" +
			"hp: {3}/{4}\n" +
			"power: {5}\n" +
			"experience points: {6}\n" +
			"next level at: {7}\n" +
			"gold coins: {8}\n" +
			"places discovered: {9}\n" +
			"kills: {10}\n" +
			"deaths: {11}\n" +
			"items found: {12}")
		output = output.format(self.gameState.world.map[p.locationCoords].name, p.locationCoords, p.level, p.hp, p.maxHp,
						p.power, p.xp, p.xpForNextLevel, p.gold, len(p.placesDiscovered),
						p.monstersKilled, p.deaths, p.itemsFound)
		return output

	# list the player's items
	def list(self):
		return self.gameState.inventory.listItems()

	# use an item
	# takes the player's turn if in combat
	def use(self, itemName):
		output = self.gameState.inventory.use(itemName, self.gameState.player)
		if self.isInCombat:
			output += "\n" + self.fight.skip()
			if self.fight.state != monsters.Fight.IN_PROGRESS:
				output += "\n" + self.__endFight()
		return output

	def sell(self, itemName):
		return self.gameState.inventory.sell(itemName, self.gameState.player)

	# attack if in combat
	def attack(self):
		output = "Shadow boxing?"
		if self.isInCombat:
			output = self.fight.attack()
			if self.fight.state != monsters.Fight.IN_PROGRESS:
				output += "\n" + self.__endFight()
		return output

	# flee if in combat
	def flee(self):
		output = "What are you running from?"
		if self.isInCombat:
			output = self.fight.flee()
			if self.fight.state != monsters.Fight.IN_PROGRESS:
				output += self.__endFight()
		return output
	
	# End a fight in victory, defeat, or flight.
	# Reward the player or handle death if appropriate.
	def __endFight(self):
		output = ""
		self.isInCombat = False
		p = self.gameState.player
		if self.fight.state == monsters.Fight.DEFEAT:
			p.locationCoords = (0, 0)
			cost = random.randrange(50, 101)
			costMessage = ""
			if cost > p.gold:
				costMessage = "\"No money? Not a problem; I never forget a debt.\""
			else:
				costMessage = "The wizard takes {0} gold coins from you.".format(cost)
			p.gold -= cost
			p.hp = p.maxHp
			p.deaths += 1
			output = ("\nThe blow is too much for your body to handle.\n" +
						"As the darkness closes in, you regret that your life couldn't " +
						"have been more {0} {1}.\n" +
						"...\n...\n...\n" +
						"You wake up in town with an old wizard standing over you.\n" +
						"He says, {2}, \"This is the part where you pay me. Resurrection ain't free.\"\n" +
						"{3} ")
			adverb1 = random.choice(self.gameState.world.adverbs)
			adjective = random.choice(self.gameState.world.itemAdjectives)
			adverb2 = random.choice(self.gameState.world.adverbs)
			output = output.format(adverb1, adjective, adverb2, costMessage)
			debtPhrase = ""
			if p.gold < 0:
				debtPhrase = "a debt of "
			output += "\nYou are left with {0}{1} gold coins.".format(debtPhrase, abs(p.gold))
		elif self.fight.state == monsters.Fight.VICTORY:
			output = "\nYou've defeated the {0}!".format(self.fight.monster.name)
			p.xp += self.fight.monster.xpReward
			p.monstersKilled += 1
			output += "\nYou gain {0} experience points!".format(self.fight.monster.xpReward)
			while p.xp >= p.xpForNextLevel:
				p.levelUp()
				output += "\nYou advance to level {0}!".format(p.level)
			if random.randrange(2) == 0:
				itemTemplate = random.choice(self.gameState.world.map[p.locationCoords].lootList)
				item = None
				if itemTemplate.use == items.Item.EQUIP_ARMOR:
					item = items.Armor(itemTemplate.name, itemTemplate.bodyPart, itemTemplate.boost, itemTemplate.value)
				elif itemTemplate.use == items.Item.EQUIP_WEAPON:
					item = items.Weapon(itemTemplate.name, itemTemplate.boost, itemTemplate.value)
				else: # consumable
					item = items.Consumable(itemTemplate.name, itemTemplate.hpRestored, itemTemplate.value)
				self.gameState.inventory.addItem(item)
				p.itemsFound += 1
				aAn = Game.aAn(item.name)
				output += "\nYou find {0} {1}!".format(aAn, item.name)
		elif self.fight.state != monsters.Fight.FLED:
			return "Error. Fight object in unexpected state."
		return output