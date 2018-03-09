from spellChecker import SpellChecker
from contextChecker import ContextChecker

class PhraseScoreRcd:
	phraseCount = 0
	def __init__(self, phrase,correctIdx, score):
		self.phrase = phrase
		self.correctIdx = correctIdx
		self.score=score
		PhraseScoreRcd.phraseCount += 1

	def __lt__(self, other):
		return self.score > other.score

	def getScore(self):
		return  "-".join(self.phrase) + " " + str(self.correctIdx) + " " +  str(self.score)

def readFiletoList(fileName):
	wordsList = []
	with open(fileName) as inpFile:
		lines = inpFile.readlines()
		for line in lines:
			wordsList.append(line.strip().upper())
	return wordsList

class PhraseChecker:
	confusionMap={}	
	spellChecker = SpellChecker()
	contextChecker = ContextChecker()
	def __init__(self):		
		tmpConfLines = readFiletoList('../data/cset.csv')
		for tmpconfLine in tmpConfLines:
			confTokens = tmpconfLine.split(',')
			currentWord = confTokens[0]
			for c in range(1,len(confTokens)):
				confToken = confTokens[c]
				if len(confToken) != 0:
					tmpWordList = []
					if currentWord in PhraseChecker.confusionMap:
						tmpWordList = PhraseChecker.confusionMap[currentWord]
					if confToken not in tmpWordList:
						tmpWordList.append(confToken)
					PhraseChecker.confusionMap[currentWord] = tmpWordList
					
					tmpWordList = []
					if confToken in PhraseChecker.confusionMap:
						tmpWordList = PhraseChecker.confusionMap[confToken]
					if currentWord not in tmpWordList:
						tmpWordList.append(currentWord)
					PhraseChecker.confusionMap[confToken] = tmpWordList

	def generatePhrase(self,phraseList,wordList,position):
		newPhList = []
		for phrase in phraseList:
			for word in wordList:
				tmpPhrase = list(phrase)
				tmpPhrase[position] = word
				tmpPhraseRcd = PhraseScoreRcd(tmpPhrase,position,-100)
				newPhList.append(tmpPhraseRcd)
		return newPhList

			
	
	def getCandidateConfSet(self,wPTokenList):
		suggestions = [];
		for i in range(0,len(wPTokenList)):
			tmpSug=[]
			tmpSug.append(wPTokenList)
			wPToken = wPTokenList[i]
			#print(wPToken)
			if wPToken in PhraseChecker.confusionMap:
				#print (PhraseChecker.confusionMap[wPToken])
				tmpSug = self.generatePhrase(tmpSug,PhraseChecker.confusionMap[wPToken],i) 
				suggestions = suggestions +tmpSug
		for suggestion in suggestions:
			print(suggestion.getScore())

		return suggestions
					
	def getCandidatesFromDictF(self,wPTokenList):
		suggestions=[]
		for i in range(0,len(wPTokenList)):
			tmpSug=[]
			tmpSug.append(wPTokenList)
			replacement = []
			wPToken = wPTokenList[i]
			candidateDistList=self.spellChecker.correct(wPToken)
			topNCandidates = self.spellChecker.getTopN(candidateDistList,10)
			for topNi in topNCandidates:
				replacement.append(topNi.word)
			tmpSug = self.generatePhrase(tmpSug,replacement,i) 
			suggestions = suggestions +tmpSug
		for suggestion in suggestions:
			print(suggestion.getScore())
		return suggestions

	def getCandidatesFromDict(self,wPTokenList,wrongIdx):
		suggestions=[]
		i = wrongIdx
		wPToken = wPTokenList[i]
		tmpSug=[]
		tmpSug.append(wPTokenList)
		replacement = []
			
		candidateDistList=self.spellChecker.correct(wPToken)
		topNCandidates = self.spellChecker.getTopN(candidateDistList,10)
		for topNi in topNCandidates:
			replacement.append(topNi.word)
		tmpSug = self.generatePhrase(tmpSug,replacement,i) 
		suggestions = suggestions +tmpSug
		for suggestion in suggestions:
			print(suggestion.getScore())
		return suggestions


	
	def getCorrect(self,wrongPhrase,K):
		wPTokenList = wrongPhrase.split(' ')
		suggestions=[]
		wrongIdx = -1
		for i in range(0,len(wPTokenList)):
			word=wPTokenList[i]
			if not self.spellChecker.inDictionary(word):
				wrongIdx =  i
		if wrongIdx !=-1:
			suggestions = suggestions + self.getCandidatesFromDict(wPTokenList,wrongIdx)
		else:
			suggestions = suggestions + self.getCandidatesFromDictF(wPTokenList)
			suggestions= suggestions + self.getCandidateConfSet(wPTokenList)

		for suggestion in suggestions:
			#print(suggestion.correctIdx)
			contextWords = []
			contextWords += suggestion.phrase[max(0,suggestion.correctIdx-K):suggestion.correctIdx]
			contextWords += suggestion.phrase[suggestion.correctIdx+1:min(len(suggestion.phrase),suggestion.correctIdx+K+1)]
			suggestion.score = self.contextChecker.getRank(suggestion.phrase[suggestion.correctIdx],contextWords,K)
		suggestions.sort()
		
		for suggestion in suggestions:
			print(suggestion.getScore())
				
		


		#rank(suggestions)	
	
		

pCorrect =PhraseChecker()
wrongPhraseList = readFiletoList('../input/errorsPhrase')
for wrongPhrase in wrongPhraseList:
	pCorrect.getCorrect(wrongPhrase,3)
