#!usr/bin/env python
import state
import game

run = True
s = state.State("testGame")
g = game.Game(s)
while run:
	cmd = input().lower().split(" ", 1)
	if len(cmd) == 0:
		cmd = ["bad command"]
	if (cmd[0] == "exit"):
		run = False
		s.save()
	elif cmd[0] == "n":
		print(g.move(game.Game.NORTH))
	elif cmd[0] == "e":
		print(g.move(game.Game.EAST))
	elif cmd[0] == "s":
		print(g.move(game.Game.SOUTH))
	elif cmd[0] == "w":
		print(g.move(game.Game.WEST))
	elif cmd[0] == "stats":
		print(g.stats())
	elif cmd[0] == "list":
		print(g.list())
	elif cmd[0] == "use":
		if len(cmd) > 1:
			print(g.use(cmd[1]))
		else:
			print("Argument required.")
	elif cmd[0] == "sell":
		if (len(cmd) > 1):
			print(g.sell(cmd[1]))
		else:
			print("Argument required.")
	elif cmd[0] == "attack":
		print(g.attack())
	elif cmd[0] == "flee":
		print(g.flee())
	else:
		print("Bad command.")
