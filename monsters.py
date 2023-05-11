import random

class Monster:
	def __init__(self, name, hp, power, xpReward):
		self.name = name
		self.hp = hp
		self.power = power
		self.xpReward = xpReward


# State machine representing an encounter with a monster. The main game loop
# will instantiate Fight and call its methods in a loop until Fight reports that
# the fight is over, along with the outcome. Fight will make victory/loss
# output strings available to the caller and give the player any rewards or
# damage as appropriate.
class Fight:

	DEFEAT = "D"
	FLED = "F"
	VICTORY = "V"
	IN_PROGRESS = "P"
	
	# Lower and upper bounds on random multipliers generated for damage calculation.
	DAM_LOW = 1
	DAM_HIGH = 10
	
	# Chance of failing to flee the fight = 1/FLEE_FAIL_RATE
	FLEE_FAIL_RATE = 4

	def __init__(self, player, monster):
		self.player = player
		self.monster = monster
		self.state = Fight.IN_PROGRESS
	
	def isInProgress(self):
		return self.state == Fight.IN_PROGRESS
	
	# Player attacks.
	def attack(self):
		output = "error"
		damage = self.player.power * random.randrange(Fight.DAM_LOW, Fight.DAM_HIGH + 1) # Upper bound argument is an exclusive endpoint, so + 1.
		self.monster.hp -= damage
		output = "You attack the " + self.monster.name + "!"
		output += "\ndamage: " + str(damage)
		output += "\n" + self.monster.name + " hp: " + str(self.monster.hp)
		if self.monster.hp <= 0:
			self.state = Fight.VICTORY
		else:
			output += "\n\n" + self.__monsterTurn()
		return output
	
	# Player attempts to flee.
	def flee(self):
		adverbList = ["bravely", "heroically", "boldly", "fearlessly", "gallantly", "valiantly"]
		adverb = adverbList[random.randrange(len(adverbList))]
		output = "You " + adverb + " attempt to run away!"
		if random.randrange(Fight.FLEE_FAIL_RATE) > 0:
			self.state = Fight.FLED
			output += "\nYou escape!"
		else:
			output += "\nYou can't escape!"
			output += "\n\n" + self.__monsterTurn()
		return output
	
	# Player skips their turn (probably by running some non-combat command).
	def skip(self):
		return self.__monsterTurn()
	
	def __monsterTurn(self):
		damage = self.monster.power * random.randrange(Fight.DAM_LOW, Fight.DAM_HIGH + 1) # Upper bound argument is an exclusive endpoint, so + 1.
		self.player.hp -= damage
		output = "The " + self.monster.name + " attacks you!"
		output += "\ndamage: " + str(damage)
		output += "\nyour hp: " + str(self.player.hp)
		if self.player.hp <= 0:
			self.state = Fight.DEFEAT
		return output