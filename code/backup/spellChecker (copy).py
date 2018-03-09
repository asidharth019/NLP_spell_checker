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
		return self.word + " " #+  str(self.score)

class SpellChecker:
	invertTriMap = {}
	invertSoundexMap = {}
	invertMetaMap = {}
	dictCountMap = {}
	invertMapGram=2
	jackardGram=2
	totalCount = 0

	def readDitionary(self,fileName):
		dict_map={}
		words = []		
		with open(fileName) as inpFile:
			lines = inpFile.readlines()
			for line in lines:
				tmp = line.strip().split("\t")
				dict_map[tmp[0]] = float(tmp[1])
		return dict_map

	def getGrams(self,word,gram):
		tGramList = []
		if len(word)==2:
			tGramList.append(word)
		else:
			tGramList= [word[i:i+gram] for i in range(len(word)-(gram-1))]
		return tGramList
		

	def readFiletoList(self,fileName):
		wordsList = []
		with open(fileName) as inpFile:
			lines = inpFile.readlines()
			for line in lines:
				wordsList.append(line.strip().upper())
		return wordsList
		
	def compED(self,str1, str2):
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


	def getJackSim(self,a,b):	
		return len(list(set(a) & set(b))) / float(len(list(set(a) | set(b))))


	def __init__(self):
		SpellChecker.dictCountMap = self.readDitionary('../data/count_1w100k.txt')
		for key in SpellChecker.dictCountMap:
			SpellChecker.totalCount += SpellChecker.dictCountMap[key]
		for word in  SpellChecker.dictCountMap:
			tGList = self.getGrams(word,SpellChecker.invertMapGram)
			for tgram in tGList:
				tmpWordList = []
				if tgram in SpellChecker.invertTriMap:
					tmpWordList = SpellChecker.invertTriMap[tgram]
				tmpWordList.append(word)
				SpellChecker.invertTriMap[tgram] = tmpWordList
			tmpWordList = []

			soundexHash = jellyfish.soundex(word)
			if soundexHash in SpellChecker.invertSoundexMap:
					tmpWordList = SpellChecker.invertSoundexMap[soundexHash]
			tmpWordList.append(word)
			SpellChecker.invertSoundexMap[soundexHash] = tmpWordList
			
			metaHash = jellyfish.metaphone(word)
			if metaHash in SpellChecker.invertMetaMap:
					tmpWordList = SpellChecker.invertMetaMap[metaHash]
			tmpWordList.append(word)
			SpellChecker.invertMetaMap[metaHash] = tmpWordList


	def correct(self,wrongWord):
		candidates = []
		candidateDistList =[]
		wWTGrams = self.getGrams(wrongWord,SpellChecker.invertMapGram)

		for trigram in wWTGrams:
			if trigram in SpellChecker.invertTriMap:
				addList=[]
				tmpList =  SpellChecker.invertTriMap[trigram]
				for tmp in tmpList:
					ed = self.compED(tmp,wrongWord)
					if ed<=2:
						addList.append(tmp)
				candidates = candidates + addList
		

		#soundexHash = jellyfish.soundex(wrongWord)
		#if soundexHash in SpellChecker.invertSoundexMap:
		#	candidates = candidates + SpellChecker.invertSoundexMap[soundexHash]
		#candidates = list(set(candidates))

		metaHash = jellyfish.metaphone(wrongWord)
		if metaHash in SpellChecker.invertMetaMap:
			candidates = candidates + SpellChecker.invertMetaMap[metaHash]
		candidates = list(set(candidates))	
		
		#print (len(candidates))

		for candidate in candidates:		
			if abs(len(candidate) - len(wrongWord)) > 2:
				continue
			if wrongWord==candidate:
				continue
			ed = self.compED(candidate,wrongWord)
			jd=jellyfish.jaro_distance(wrongWord,candidate)
			gd = self.getJackSim(self.getGrams(candidate,SpellChecker.jackardGram),self.getGrams(wrongWord,SpellChecker.jackardGram))
			score = float(SpellChecker.dictCountMap[candidate]) / float(SpellChecker.totalCount) + (max(len(candidate),len(wrongWord))-ed)
			if jellyfish.metaphone(wrongWord) == jellyfish.metaphone(candidate):
				score = score+0.1
			#if jellyfish.soundex(wrongWord) == jellyfish.soundex(candidate):
			#	score = score+0.1
			#if jellyfish.nysiis(wrongWord) == jellyfish.nysiis(candidate):
			#	score = score+0.1
			#if jellyfish.match_rating_codex(wrongWord) == jellyfish.match_rating_codex(candidate):
			#	score = score+0.1
			tmpCandidate = ScoreRcd(candidate,ed, score) ;
			candidateDistList.append(tmpCandidate)
		candidateDistList.sort()
		return candidateDistList
	
	def inDictionary(self,word):
		return (word in self.dictCountMap)

	def getTopN(self,candidateDistList,N):
		maxIter = N
		if len(candidateDistList) < maxIter:
			maxIter = len(candidateDistList)
		return candidateDistList[:N]
			




def main():
	spellChecker = SpellChecker()
	wrongWords =  spellChecker.readFiletoList('../input/errorList')

	for wrongWord in wrongWords:
		out=wrongWord + ' '
		candidateDistList = spellChecker.correct(wrongWord)
		topN=spellChecker.getTopN(candidateDistList,10)
		for topNi in topN:
			out =  out + topNi.getScore() + ' '
		print (out)

if __name__ == "__main__":
    main()







