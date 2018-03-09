#!/usr/bin/env python
import editdistance
import sys

# sys.path.insert(0, '../lib/metaphone')
from metaphone import doublemetaphone

class ScoreRcd:
    wordCount = 0

    def __init__(self, word, editDist, score):
        self.word = word
        self.editDist = editDist
        self.score = score
        ScoreRcd.wordCount += 1

    def __lt__(self, other):
        return self.score > other.score

    def getScore(self):
        return self.word  # + " " +  str(self.score)

    def getScore1(self):
        return self.score


def checkCmdAgs():
    if len(sys.argv) != 3:
        print("pgm <InputFile> <OutputFile>")
        exit()
    return (sys.argv[1], sys.argv[2])


class SpellChecker:
    invertTriMap = {}
    invertSoundexMap = {}
    invertMetaMap = {}
    dictCountMap = {}
    invertMapGram = 2
    jackardGram = 2
    totalCount = 0

    def readDitionary(self, fileName):
        dict_map = {}
        words = []
        with open(fileName) as inpFile:
            lines = inpFile.readlines()
            for line in lines:
                tmp = line.strip().split("\t")
                dict_map[tmp[0].upper()] = float(tmp[1])
        return dict_map

    def getGrams(self, word, gram):
        tGramList = []
        if len(word) <= 2:
            tGramList.append(word)
        else:
            tGramList = [word[i:i + gram] for i in range(len(word) - (gram - 1))]
        # tGramList= [word[i:i+gram] for i in range(len(word)-(gram-1))]
        return tGramList

    def readFiletoList(self, fileName):
        wordsList = []
        with open(fileName) as inpFile:
            lines = inpFile.readlines()
            for line in lines:
                wordsList.append(line.strip().upper())
        return wordsList

    def getJackSim(self, a, b):
        return len(list(set(a) & set(b))) / float(len(list(set(a) | set(b))))

    def __init__(self):
        SpellChecker.dictCountMap = self.readDitionary('data/count_1w100k.txt')
        for key in SpellChecker.dictCountMap:
            SpellChecker.totalCount += SpellChecker.dictCountMap[key]
        for word in SpellChecker.dictCountMap:
            tGList = self.getGrams(word, SpellChecker.invertMapGram)
            for tgram in tGList:
                tmpWordList = []
                if tgram in SpellChecker.invertTriMap:
                    tmpWordList = SpellChecker.invertTriMap[tgram]
                tmpWordList.append(word)
                SpellChecker.invertTriMap[tgram] = tmpWordList
            tmpWordList = []


            # soundexHash = jellyfish.soundex(word)
            # if soundexHash in SpellChecker.invertSoundexMap:
            #		tmpWordList = SpellChecker.invertSoundexMap[soundexHash]
            # tmpWordList.append(word)
            # SpellChecker.invertSoundexMap[soundexHash] = tmpWordList

            # metaHash = jellyfish.metaphone(word)
            # if metaHash in SpellChecker.invertMetaMap:
            #		tmpWordList = SpellChecker.invertMetaMap[metaHash]
            # tmpWordList.append(word)
            # SpellChecker.invertMetaMap[metaHash] = tmpWordList

            metaHash = doublemetaphone(word)[0]
            if metaHash in SpellChecker.invertMetaMap:
                tmpWordList = SpellChecker.invertMetaMap[metaHash]
            tmpWordList.append(word)
            SpellChecker.invertMetaMap[metaHash] = tmpWordList

    def correct(self, wrongWord):
        candidates = []
        candidateDistList = []
        wWTGrams = self.getGrams(wrongWord, SpellChecker.invertMapGram)
        # addList=[]
        # for key in SpellChecker.dictCountMap:
        #	ed = editdistance.eval(key,wrongWord)
        #	if ed<=1:
        #		addList.append(key)
        #		candidates = candidates + addList

        for trigram in wWTGrams:
            if trigram in SpellChecker.invertTriMap:
                addList = []
                tmpList = SpellChecker.invertTriMap[trigram]
                for tmp in tmpList:
                    ed = editdistance.eval(tmp, wrongWord)
                    if ed <= 1:
                        addList.append(tmp)
                candidates = candidates + addList

        # soundexHash = jellyfish.soundex(wrongWord)
        # for soundexHash1 in SpellChecker.invertSoundexMap:
        #	if int(soundexHash1[1:]) - int(soundexHash[1:]) < 5:
        #		candidates = candidates + SpellChecker.invertSoundexMap[soundexHash1]
        #		candidates = list(set(candidates))

        # soundexHash = jellyfish.soundex(wrongWord)
        # if soundexHash in SpellChecker.invertSoundexMap:
        #	candidates = candidates + SpellChecker.invertSoundexMap[soundexHash]
        # candidates = list(set(candidates))

        metaHash = doublemetaphone(wrongWord)[0]
        if metaHash in SpellChecker.invertMetaMap:
            candidates = candidates + SpellChecker.invertMetaMap[metaHash]
            candidates = list(set(candidates))
        # print (len(candidates))

        for candidate in candidates:
            if abs(len(candidate) - len(wrongWord)) > 2:
                if doublemetaphone(candidate)[0] == doublemetaphone(wrongWord)[0] and doublemetaphone(candidate)[1] == \
                        doublemetaphone(wrongWord)[1]:
                    st = ""
                else:
                    continue
            if wrongWord == candidate:
                continue
            ed = editdistance.eval(candidate, wrongWord)
            # jd=jellyfish.jaro_distance(wrongWord,candidate)
            # if min(len(candidate),len(wrongWord)) < 5:
            #	gd = self.getJackSim(self.getGrams(candidate,2),self.getGrams(wrongWord,2))
            # else:
            #	gd = self.getJackSim(self.getGrams(candidate,3),self.getGrams(wrongWord,3))
            weight = 0.5
            score = (max(len(candidate), len(wrongWord)) - ed) + (
                        float(SpellChecker.dictCountMap[candidate]) / float(SpellChecker.totalCount))
            if candidate[:1] == wrongWord[:1]:
                score = score + 1;
            if candidate[:2] == wrongWord[:2]:
                score = score + 1;
            if candidate[:3] == wrongWord[:4]:
            	score=score+3;
            if candidate[-1:] == wrongWord[-1:]:
                score = score + 1;
            if candidate[-2:] == wrongWord[-2:]:
                score = score + 1;
            if candidate[-3:] == wrongWord[-3:]:
                score = score + 1;
            if doublemetaphone(candidate)[0] == doublemetaphone(wrongWord)[0] and doublemetaphone(candidate)[1] == \
                    doublemetaphone(wrongWord)[1]:
                score = score + 1;
            tmpCandidate = ScoreRcd(candidate, ed, score);
            candidateDistList.append(tmpCandidate)
        candidateDistList.sort()
        return candidateDistList

    def inDictionary(self, word):
        return (word in self.dictCountMap)

    def getTopN(self, candidateDistList, N):
        maxIter = N
        if len(candidateDistList) < maxIter:
            maxIter = len(candidateDistList)
        return candidateDistList[:N]


def main():
    # (inpFile, outFile) = checkCmdAgs()
    inpFile = 'words_input.txt'
    outFile = 'output.txt'
    spellChecker = SpellChecker()
    wrongWords = spellChecker.readFiletoList(inpFile)
    target = open(outFile, "w");
    for wrongWord in wrongWords:
        out = wrongWord + '\t'
        candidateDistList = spellChecker.correct(wrongWord)
        topN = spellChecker.getTopN(candidateDistList, 10)
        maxscore = 0.0
        for topNi in topN:
            maxscore = maxscore + topNi.getScore1()
        for topNi in topN:
            if str(format(topNi.getScore1() / maxscore, '.2f')) != '0.00':
                # out = out + topNi.getScore() + '\t' + str(format(topNi.getScore1(), '.4f')) + '\t'
                out = out + topNi.getScore() + '\t'
        print(out)
        target.write(out)
        target.write('\n')
    target.close()


if __name__ == "__main__":
    main()
