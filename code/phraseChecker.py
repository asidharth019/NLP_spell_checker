from spellChecker import SpellChecker
from contextChecker import ContextChecker
from nltk.corpus import stopwords


class PhraseScoreRcd:
    phraseCount = 0

    def __init__(self, phrase, correctIdx, score):
        self.phrase = phrase
        self.correctIdx = correctIdx
        self.score = score
        PhraseScoreRcd.phraseCount += 1

    def __lt__(self, other):
        return self.score > other.score

    def getScore(self):
        return "-".join(self.phrase) + " " + str(self.correctIdx) + " " + str(self.score)


def removestopwords(text):
    cachedStopWords = stopwords.words("english")

    return ' '.join([word for word in text.split() if word not in cachedStopWords])


def readFiletoList(fileName):
    wordsList = []
    with open(fileName) as inpFile:
        lines = inpFile.readlines()
        for line in lines:
            # line = removestopwords(line)
            wordsList.append(line.strip().upper())
    return wordsList


class PhraseChecker:
    confusionMap = {}
    spellChecker = SpellChecker()
    contextChecker = ContextChecker()
    cachedStopWords = []

    def __init__(self):
        tmpConfLines = readFiletoList('../data/cset.csv')
        for stopword in stopwords.words("english"):
            self.cachedStopWords.append(stopword.upper())
        # print(self.cachedStopWords)
        for tmpconfLine in tmpConfLines:
            confTokens = tmpconfLine.split(',')
            currentWord = confTokens[0]
            for c in range(1, len(confTokens)):
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

    def generatePhrase(self, phraseList, wordList, position):
        newPhList = []
        for phrase in phraseList:
            for word in wordList:
                tmpPhrase = list(phrase)
                tmpPhrase[position] = word
                tmpPhraseRcd = PhraseScoreRcd(tmpPhrase, position, -100)
                newPhList.append(tmpPhraseRcd)
        return newPhList

    def getCandidateConfSet(self, wPTokenList):
        suggestions = [];
        for i in range(0, len(wPTokenList)):

            tmpSug = []
            tmpSug.append(wPTokenList)
            wPToken = wPTokenList[i]
            # print(wPToken)
            if wPToken in PhraseChecker.confusionMap:
                # print (PhraseChecker.confusionMap[wPToken])
                tmpSug = self.generatePhrase(tmpSug, PhraseChecker.confusionMap[wPToken], i)
                suggestions = suggestions + tmpSug
        # for suggestion in suggestions:
        #	print(suggestion.getScore())

        return suggestions

    def getCandidatesFromDictF(self, wPTokenList):
        suggestions = []
        for i in range(0, len(wPTokenList)):
            tmpSug = []
            tmpSug.append(wPTokenList)
            replacement = []
            wPToken = wPTokenList[i]
            candidateDistList = self.spellChecker.correct(wPToken)
            topNCandidates = self.spellChecker.getTopN(candidateDistList, 10)
            for topNi in topNCandidates:
                replacement.append(topNi.word)
            tmpSug = self.generatePhrase(tmpSug, replacement, i)
            suggestions = suggestions + tmpSug
        # for suggestion in suggestions:
        #	print(suggestion.getScore())

        return suggestions

    def getCandidatesFromDict(self, wPTokenList, wrongIdx):
        suggestions = []
        i = wrongIdx
        wPToken = wPTokenList[i]
        tmpSug = []
        tmpSug.append(wPTokenList)
        replacement = []

        candidateDistList = self.spellChecker.correct(wPToken)
        topNCandidates = self.spellChecker.getTopN(candidateDistList, 10)
        for topNi in topNCandidates:
            replacement.append(topNi.word)
        tmpSug = self.generatePhrase(tmpSug, replacement, i)
        suggestions = suggestions + tmpSug
        # for suggestion in suggestions:
        #	print(suggestion.getScore())
        return suggestions

    def splitter(self, word):
        for i in range(1, len(word)):
            start = word[0:i]
            end = word[i:]
            yield (start, end)
            for split in self.splitter(end):
                result = [start]
                result.extend(split)
                yield result

    def getCombinations(self, word):
        combinations = list(self.splitter(word.upper()))
        prune_list = []
        for i in range(len(combinations)):
            k = 0
            for j in range(len(combinations[i])):
                if not (self.spellChecker.inDictionary(combinations[i][j])):
                    k = 1
                    break
                if len(combinations[i][j]) == 1 and not (combinations[i][j] == 'A' or combinations[i][j] == 'I'):
                    k = 1
                    break
            if (k == 0):
                prune_list.append(combinations[i])

        return prune_list

    def getSplitCorrections(self, wrongPhrase):
        suggestions = []
        prune_list = self.getCombinations(wrongPhrase)
        for phr in prune_list:
            tmpPhraseRcd = PhraseScoreRcd(phr, 0, -100)
            suggestions.append(tmpPhraseRcd)

        # print(len(suggestions))

        for suggestion in suggestions:
            dummyIdx = int(len(suggestion.phrase) / 2)
            K = 3
            # print(suggestion.phrase)
            contextWords = []
            contextWords += suggestion.phrase[max(0, dummyIdx - K):dummyIdx]
            contextWords += suggestion.phrase[dummyIdx + 1:min(len(suggestion.phrase), dummyIdx + K + 1)]
            # print(contextWords)
            # print('------')
            suggestion.score = self.contextChecker.getRank(suggestion.phrase[dummyIdx], contextWords, K)
        suggestions.sort()
        return suggestions

    def getCorrect(self, wrongPhrase, K):
        wPTokenList = wrongPhrase.split(' ')
        suggestions = []
        wrongIdx = -1
        for i in range(0, len(wPTokenList)):
            word = wPTokenList[i]
            if not self.spellChecker.inDictionary(word):
                wrongIdx = i
        if wrongIdx != -1:
            suggestions = suggestions + self.getCandidatesFromDict(wPTokenList, wrongIdx)
        # print("WrongWord")
        else:
            suggestions = suggestions + self.getCandidateConfSet(wPTokenList)
            # print("ConfWord")
            if len(suggestions) == 0:
                suggestions = suggestions + self.getCandidatesFromDictF(wPTokenList)
            # print("AllRight")

        for suggestion in suggestions:
            # print(suggestion.correctIdx)
            contextWords = []
            contextWords += suggestion.phrase[max(0, suggestion.correctIdx - K):suggestion.correctIdx]
            contextWords += suggestion.phrase[
                            suggestion.correctIdx + 1:min(len(suggestion.phrase), suggestion.correctIdx + K + 1)]
            suggestion.score = self.contextChecker.getRank(suggestion.phrase[suggestion.correctIdx], contextWords, K)
        suggestions.sort()

        # Find candidate
        # for suggestion in suggestions:
        #	print(suggestion.getScore())

        return suggestions

    def rank(self, suggestions, wPTokenList):
        prunedSuggestions = []
        repeatingIdx = {}
        for i in range(0, len(wPTokenList)):
            repeatingIdx[i] = 0;

        for suggestion in suggestions:
            if suggestion.score == -1000:
                continue
            repeatingIdx[suggestion.correctIdx] += 1
            prunedSuggestions.append(suggestion)

        if len(prunedSuggestions) == 0:
            if len(suggestions) > 0:
                suggestions[0].score = 1
                prunedSuggestions.append(suggestions[0])

            else:
                prunedSuggestions.append(PhraseScoreRcd(wPTokenList, 1, 1))

        # print(repeatingIdx)
        maxRep = 0
        for key in repeatingIdx:
            if repeatingIdx[key] > maxRep:
                maxRep = repeatingIdx[key]
        # print(maxRep)

        suggestIdx = -1
        for suggestion in prunedSuggestions:
            if repeatingIdx[suggestion.correctIdx] == maxRep:
                suggestIdx = suggestion.correctIdx
                maxScore = suggestion.score
                break

        sumScore = 0
        minScore = maxScore
        for suggestion in prunedSuggestions:
            if suggestion.correctIdx == suggestIdx:
                sumScore = sumScore + suggestion.score
                if suggestion.score < minScore:
                    minScore = suggestion.score

        if minScore != maxScore:
            normFact = maxScore - minScore
        else:
            normFact = maxScore

        return (prunedSuggestions, suggestIdx)


def main():
    pCorrect = PhraseChecker()
    wrongPhraseList = readFiletoList('../input/errorsPhrase')
    for wrongPhrase in wrongPhraseList:
        wPTokenList = wrongPhrase.split(' ')
        if (len(wPTokenList) > 1):
            suggestions = pCorrect.getCorrect(wrongPhrase, 3)
            (prunedSuggestions, suggestIdx) = pCorrect.rank(suggestions, wPTokenList)
            count = 0
            out = wPTokenList[suggestIdx]
            for suggestion in prunedSuggestions:
                if suggestion.correctIdx == suggestIdx and count < 3:
                    count = count + 1
                    out = out + '\t' + suggestion.phrase[suggestIdx] + '\t' + str(suggestion.score)

            print(out)
        else:
            out = wrongPhrase + ' '
            suggestions = pCorrect.getSplitCorrections(wrongPhrase)
            count = 0
            for suggestion in suggestions:
                if count < 5:
                    count = count + 1
                    out = out + '\t'
                    for phraseTerm in suggestion.phrase:
                        out = out + ' ' + phraseTerm
                    out = out + '\t' + str(suggestion.score)

            print(out)


if __name__ == "__main__":
    main()
