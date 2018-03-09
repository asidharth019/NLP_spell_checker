import ScoreRcd,SpellChecker from spellChecker
def readFiletoList(fileName):
	wordsList = []
	with open(fileName) as inpFile:
		lines = inpFile.readlines()
		for line in lines:
			wordsList.append(line.strip().upper())
	return wordsList

phrases = readFiletoList('../input/errorsPhrase')
