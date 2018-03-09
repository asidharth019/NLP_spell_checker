#!/usr/bin/env python
import jellyfish
class ScoreRcd:
	wordCount = 0
	def __init__(self, word,editDist, score):
		self.word = word
		self.editDist = editDist
		self.score=score
		ScoreRcd.wordCount += 1

	def __lt__(self, other):
		return self.score > other.score

	def getScore(self):
		return self.word + " " +  str(self.score)


def readDitionary(fileName):
	dict_map={}
	with open(fileName) as inpFile:
		lines = inpFile.readlines()
		for line in lines:
			tmp = line.strip().split("\t")
			dict_map[tmp[0]] = float(tmp[1])
	return dict_map

def getGrams(word,gram):
	tGramList = []
	if len(word)==2:
		tGramList.append(word)
	else:
		tGramList= [word[i:i+gram] for i in range(len(word)-(gram-1))]
	return tGramList
		

def readFiletoList(fileName):
	wordsList = []
	with open(fileName) as inpFile:
		lines = inpFile.readlines()
		for line in lines:
			wordsList.append(line.strip().upper())
	return wordsList
		
def compED(str1, str2):
	len1 = len(str1)
	len2 = len(str2)

	dist=[[0 for i in range(0,len2+1)] for j in range(0,len1+1)]
	for i in range(0,len1+1):
		dist[i][0] = i
	for j in range(0,len2+1):
		dist[0][j] = j
	for j in range(1,len2+1):
		for i in range(1,len1+1):
			if str1[i-1] == str2[j-1]:
				substitutionCost = 0
			else:
				substitutionCost = 1
			dist[i][j] = min(dist[i-1][j]+1,dist[i][j-1]+1,dist[i-1][j-1])+substitutionCost
			#CHECK THE ABOVE LINE. VIKRAM
	return dist[len1][len2]


def getJackSim(a,b):
	return len(list(set(a) & set(b))) / float(len(list(set(a) | set(b))))


class SpellChecker:
	invertTriMap = {}
	dictCountMap = {}
	invertMapGram=3
	jackardGram=2
	totalCount = 0

	def __init__(self):
		SpellChecker.dictCountMap = readDitionary('../data/count_1w100k.txt')
		for key in SpellChecker.dictCountMap:
			SpellChecker.totalCount += SpellChecker.dictCountMap[key]
		for word in  SpellChecker.dictCountMap:
			tGList = getGrams(word,SpellChecker.invertMapGram)
			for tgram in tGList:
				tmpWordList = []
				if tgram in SpellChecker.invertTriMap:
					tmpWordList = SpellChecker.invertTriMap[tgram]
				tmpWordList.append(word)
				SpellChecker.invertTriMap[tgram] = tmpWordList

	def correct(self,wrongWord):
		candidates = []
		candidateDistList =[]
		wWTGrams = getGrams(wrongWord,SpellChecker.invertMapGram)

		for trigram in wWTGrams:
			if trigram in SpellChecker.invertTriMap:
				candidates = candidates + SpellChecker.invertTriMap[trigram]
		candidates = list(set(candidates)) 
		print (len(candidates))

		for candidate in candidates:		
			CandTGrams = getGrams(candidate,SpellChecker.invertMapGram)
			ed = compED(candidate,wrongWord)
			if abs(len(candidate)- len(wrongWord)) > 2:
				continue
			jd=jellyfish.jaro_distance(wrongWord,candidate)
			gd = getJackSim(getGrams(candidate,SpellChecker.jackardGram),getGrams(wrongWord,SpellChecker.jackardGram))
			score = gd * SpellChecker.dictCountMap[candidate]/ SpellChecker.totalCount * (1/(ed+1)) * (1/(jd+1))
			if jellyfish.metaphone(wrongWord) == jellyfish.metaphone(candidate):
				score = score+0.1
			if jellyfish.soundex(wrongWord) == jellyfish.soundex(candidate):
				score = score+0.1
			if jellyfish.nysiis(wrongWord) == jellyfish.nysiis(candidate):
				score = score+0.1
			if jellyfish.match_rating_codex(wrongWord) == jellyfish.match_rating_codex(candidate):
				score = score+0.1
			tmpCandidate = ScoreRcd(candidate,ed, score) ;
			candidateDistList.append(tmpCandidate)
			candidateDistList.sort()
		return candidateDistList



wrongWords =  readFiletoList('../input/errorList')
spellChecker = SpellChecker()

for wrongWord in wrongWords:
	out=wrongWord + ' '
	candidateDistList = spellChecker.correct(wrongWord)
	maxIter = 10
	if len(candidateDistList) < maxIter:
		maxIter = len(candidateDistList)

	for i in range(0,maxIter):
		out =  out + candidateDistList[i].getScore() + ' '
	print (out)

		







