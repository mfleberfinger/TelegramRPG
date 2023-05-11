class Item:

	EQUIP_ARMOR = "EQUIP_ARMOR"
	EQUIP_WEAPON = "EQUIP_WEAPON"
	CONSUME = "CONSUME"
	
	def __init__(self, name, use, effectDescription, value):
		self.name = name
		self.use = use
		self.quantity = 1
		self.effectDescription = effectDescription
		self.value = value


class Equipment(Item):
	
	TORSO = "torso"
	HEAD = "head"
	LEGS = "legs"
	WEAPON = "weapon"
	
	def __init__(self, name, use, effectDescription, bodyPart, boost, value):
		Item.__init__(self, name, use, effectDescription, value)
		self.bodyPart = bodyPart
		self.isEquipped = False
		self.boost = boost


class Armor(Item):
	
	def __init__(self, name, bodyPart, hpBoost, value):
		Equipment.__init__(self, name, Item.EQUIP_ARMOR, "+" + str(hpBoost) + " max hp", bodyPart, hpBoost, value)


class Weapon(Item):

	def __init__(self, name, powerBoost, value):
		Equipment.__init__(self, name, Item.EQUIP_WEAPON, "+" + str(powerBoost) + " attack power", Equipment.WEAPON, powerBoost, value)


# Just healing items for now (forever?).
class Consumable(Item):

	def __init__(self, name, hpRestored, value):
		Item.__init__(self, name, Item.CONSUME, "restores " + str(hpRestored) + " hp", value)
		self.hpRestored = hpRestored


class Inventory:
	
	def __init__(self):
		self.items = dict()
	
	def listItems(self):
		output = ""
		for itemName in self.items:
			item = self.items[itemName]
			isConsumable = item.use == Item.CONSUME
			output += itemName
			if isConsumable or not item.isEquipped:
				output += ":"
			else:
				output += " (equipped):"
			output += "\n   effect: " + item.effectDescription
			output += "\n   quantity: " + str(item.quantity)
			output += "\n"
		if len(self.items) == 0:
			output = "You have no items. " # This trailing space is a hacky way to avoid cutting off the period when returning.
		return output[:-1] # Don't return the extra newline.
	
	def addItem(self, item):
		if item.name in self.items:
			self.items[item.name].quantity += 1
		else:
			# Create a new instance to avoid side-effects.
			if item.use == Item.CONSUME:
				newItem = Consumable(item.name, item.hpRestored, item.value)
			elif item.bodyPart == Equipment.WEAPON:
				newItem = Weapon(item.name, item.boost, item.value)
			else:
				newItem = Armor(item.name, item.bodyPart, item.boost, item.value)
			self.items[item.name] = newItem
	
	def use(self, itemName, player):
		output = ""
		if itemName in self.items:
			item = self.items[itemName]
			if item.use == Item.CONSUME:
				player.hp += item.hpRestored
				item.quantity -= 1
				if item.quantity <= 0:
					del self.items[itemName]
				if player.hp > player.maxHp:
					player.hp = player.maxHp
				output = "You use the " + item.name + ", regaining " + str(item.hpRestored) + " hp."
			elif item.use == Item.EQUIP_ARMOR:
				if item.isEquipped:
					player.maxHp -= item.boost
					if player.hp > player.maxHp:
						player.hp = player.maxHp
					item.isEquipped = False
					player.equippedSet.remove(item.bodyPart)
					output = "You take off the " + item.name + "."
				elif item.bodyPart not in player.equippedSet:
					if player.hp == player.maxHp:
						player.hp += item.boost
					player.maxHp += item.boost
					item.isEquipped = True
					player.equippedSet.add(item.bodyPart)
					output = "You put on the " + item.name + "."
				else: # player already wearing something on this item's body part
					output = "It's pretty hard to wear two of those, buddy."
			else: # item.use = Item.EQUIP_WEAPON
				if item.isEquipped:
					player.power -= item.boost
					item.isEquipped = False
					player.equippedSet.remove(item.bodyPart)
					output = "You put away the " + item.name + "."
				elif item.bodyPart not in player.equippedSet:
					player.power += item.boost
					item.isEquipped = True
					player.equippedSet.add(item.bodyPart)
					output = "You pick up the " + item.name + "."
				else: # player already wearing something on this item's body part
					output = "You distinctly recall your sensei informing you that dual wielding is a good way to hurt yourself."
		else:
			output = "You don't have one of those."
		return output
	
	def sell(self, itemName, player):
		output = ""
		if itemName in self.items:
			item = self.items[itemName]
			if item.use == Item.EQUIP_ARMOR:
				if item.isEquipped:
					player.maxHp -= item.boost
					if player.hp > player.maxHp:
						player.hp = player.maxHp
					item.isEquipped = False
					player.equippedSet.remove(item.bodyPart)
					output = "You take off the " + item.name + "."
			elif item.use == Item.EQUIP_WEAPON:
				if item.isEquipped:
					player.power -= item.boost
					item.isEquipped = False
					player.equippedSet.remove(item.bodyPart)
					output = "You put away the " + item.name + "."
			soldFor = item.quantity * item.value
			player.gold += soldFor
			del self.items[itemName]
			output += "\nYou sell the " + item.name + " for " + str(soldFor) + " gold coins."
		else:
			output = "Trying to sell something you don't own is a form of fraud."
		return output