def deduplicate(fileName):
	splitName = fileName.split(".", 1)
	with open(fileName, "r") as f:
		words = f.read().split("\n")
	wordsDeduplicated = []
	wordSet = set()
	for w in words:
		if w not in wordSet:
			wordSet.add(w)
			wordsDeduplicated.append(w)
	if len(splitName) > 1:
		newFileName = splitName[0] + "_deduplicated." + splitName[1]
	else:
		newFileName = splitName[0] + "_deduplicated"
	with open(newFileName, "w+") as f:
		f.write("\n".join(wordsDeduplicated))