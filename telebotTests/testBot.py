import telebot

with open("../token", "r") as f:
	bot = telebot.TeleBot(f.read(), parse_mode=None) # You can set parse_mode by default. HTML or MARKDOWN

@bot.message_handler(commands = ['start', 'help'])
def send_welcome(message):
	print("chat or user ID:" + str(message.chat.id))
	print("message text: " + str(message.text))
	output = ("Welcome, adventurer, to Generica, a land of infinite* possibilities!\n\n\n" +

		"* Subject to technical and mechanical limitations. Other limitations may apply. " +
			"Infinite does not necessarily mean interesting. Developer assumes no liability " +
			"for any shortcomings, bugs, bad design, anti-features, or malfeasance. " +
			"May cause cancer.")
	bot.reply_to(message, output)

#@bot.message_handler(func=lambda m: True)
#def echo_all(message):
#	bot.reply_to(message, message.text)

bot.infinity_polling()