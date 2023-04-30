#!usr/bin/env python
import game
import re
import state
import telebot

BOT_NAME = "@tiny_rpg_bot"
#BOT_NAME = "@Mltest_bot"

# Dictionary of State objects keyed by chat ID (a number).
gameTable = dict()

with open("token", "r") as f:
	bot = telebot.TeleBot(f.read(), parse_mode=None)
	
combatMarkup = telebot.util.quick_markup({
		"attack": {"callback_data": "attack"},
		"flee": {"callback_data": "flee"},
	}, row_width=2)


# chatId: ChatId to send to.
# output: Output from the game.
# g: Instance of the game.
# s: Instance of the state object.
def sendCombatOutput(chatId, output, g, s):
	newOutput = ""
	# Fight started.
	if g.isInCombat and not s.wasInCombat:
		newOutput = output
		sentMessage = bot.send_message(chatId, newOutput, reply_markup=combatMarkup)
		# Remember this message's ID and text so we can edit it later.
		# Also remember that we're doing combat output (editing a single message).
		s.wasInCombat = True
		s.combatMessageText = newOutput
		s.combatMessageId = sentMessage.message_id
	# Fight continuing.
	elif g.isInCombat:
		newOutput = s.combatMessageText + "\n\n" + output
		# Message text longer than 4096 characters can cause errors.
		# This situation should be unlikely so we'll just get rid of all of
		# the old output from this fight if it happens.
		if len(newOutput) > 4096:
			newOutput = output
		bot.edit_message_text(newOutput, chatId, s.combatMessageId, reply_markup=combatMarkup)
		s.combatMessageText = newOutput
	# Fight ended.
	elif (not g.isInCombat) and s.wasInCombat:
		newOutput = s.combatMessageText + "\n\n" + output
		if len(newOutput) > 4096:
			newOutput = output
		bot.edit_message_text(newOutput, chatId, s.combatMessageId, reply_markup=None)
		s.wasInCombat = False
		s.combatMessageText = ""
		s.combatMessageId = None

@bot.message_handler(commands = ["help"])
def help(message):
        output = ("start - Start the bot.\n" +
                "n - Go North.\n" +
                "e - Go East.\n" +
                "s - Go South.\n" +
                "w - Go West.\n" +
                "stats - View player stats.\n" +
                "list - List your items.\n" +
                "use - Wear, wield, or consume an item. Usage: use item_name\n" +
                "sell - Sell an item. Usage: sell item_name\n" +
                "attack - Attack an opponent.\n" +
                "flee - Run away from a fight.")
        bot.reply_to(message, output)

# Receive all messages and parse them as commands if valid.
@bot.message_handler(commands = ["start", "n", "e", "s", "w", "stats", "list", "use", "sell", "attack", "flee"])
def handle_command(message):
	chatId = message.chat.id
	output = ""
	if chatId not in gameTable:
		s = state.State(str(chatId))
		g = game.Game(s)
		gameTable[chatId] = g
		if s.newGame:
			output += ("Welcome, adventurer, to Generica, a land of infinite* possibilities!\n\n\n" +
						"* Subject to technical and mechanical limitations. Other limitations may apply. " +
						"Infinite does not necessarily mean interesting. Developer assumes no liability " +
						"for any shortcomings, bugs, bad design, anti-features, or malfeasance. " +
						"May cause cancer.\n\n\n")
	else:
		g = gameTable[chatId]
		s = g.gameState
	cmd = message.text
	cmd = re.sub(BOT_NAME, "", cmd)
	cmdSplit = cmd.split(" ", 1)
	
	# Set the command itself to lowercase but leave any arguments in mixed case
	# because I made the item keys in the player inventory's dictionary mixed
	# case, and fixing it now would either require me to throw out saved games
	# or write a program to fix those saved games.
	cmdSplit[0] = cmdSplit[0].lower()
	
	if cmdSplit[0] == "/n":
		output += g.move(game.Game.NORTH)
	elif cmdSplit[0] == "/e":
		output += g.move(game.Game.EAST)
	elif cmdSplit[0] == "/s":
		output += g.move(game.Game.SOUTH)
	elif cmdSplit[0] == "/w":
		output += g.move(game.Game.WEST)
	elif cmdSplit[0] == "/stats":
		output += g.stats()
	elif cmdSplit[0] == "/list":
		output += g.list()
	elif cmdSplit[0] == "/use":
		if len(cmdSplit) > 1:
			output += g.use(cmdSplit[1])
		else:
			output += "Can't use nothing."
	elif cmdSplit[0] == "/sell":
		if (len(cmdSplit) > 1):
			output += g.sell(cmdSplit[1])
		else:
			output += "Can't sell nothing."
	elif cmdSplit[0] == "/attack":
		output += g.attack()
	elif cmdSplit[0] == "/flee":
		output += g.flee()
	if output != "":
		if s.wasInCombat or g.isInCombat:
			sendCombatOutput(chatId, output, g, s)
		else:
			bot.reply_to(message, output)
	#print("output = " + output)
	# Just save after every command. This could be done on a schedule instead but
	# telebot makes this the more convenient approach.
	s.save()

@bot.callback_query_handler(lambda a : True)
def callBackQueryHandler(callbackQuery):
	chatId = callbackQuery.message.chat.id
	output = ""
	g = gameTable[chatId]
	s = g.gameState
	if callbackQuery.data == "attack":
		output += g.attack()
	else:
		output += g.flee()
	sendCombatOutput(chatId, output, g, s)
	
	
bot.infinity_polling()
