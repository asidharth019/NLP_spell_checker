import sys
import editdistance
from metaphone import doublemetaphone

gramcount = 2

class candInfo():
    def __init__(self, can, score, ed):
        self.can = can
        self.score = score
        self.ed = ed

    def getCand(self):
        return self.can

    def getScore(self):
        return self.score


def bigrams(word):
    bg = []
    for i in range(len(word) - 2):
        bg.append(word[i:i + gramcount])
    return bg


def findCandidates(word1, wordAssoBigrams1, dict, totalWC):
    word1 = word1.upper()
    grams1 = bigrams(word1)
    candidates1 = []

    for gr in grams1:
        if gr in wordAssoBigrams1:
            for listword in wordAssoBigrams1[gram]:
                ed1 = editdistance.eval(word1, listword)
                if ed1 <= 1:
                    candidates1.append(listword)

    for cand in candidates1:
        ed1 = editdistance.eval(word1,cand)

        score = ed1

        if cand[:1] == word1[:1]:
            score += 1
        if cand[:2] == word1[:2]:
            score += 1
        if cand[-1:] == word1[-1:]:
            score += 1
        if cand[-1:] == word1[-1:]:
            score += 1

        score = score*(dict[cand]/totalWC)
        m = candInfo(cand, score, ed1)
        candidates1.append(m)
    return candidates1


# ifile = sys.argv[1]
# ofile = sys.argv[2]

ifile = 'words_input.txt'
ofile = 'output.txt'
dictionaryfile = 'count_1w100k.txt'

dic = {}
with open(dictionaryfile, 'r') as inputfile:
    lines = inputfile.readlines()
    for i in lines:
        cols = i.split('\t')
        dic[cols[0]] = int(cols[1])

# For total frequency count
totalWordCount = 0
for word in dic:
    totalWordCount += dic[word]

# For listing the bigrams of all the words present
wordAssoBigrams = {}
for word in dic:
    grams = bigrams(word)
    for gram in grams:
        biglist = []
        if gram in wordAssoBigrams:
            biglist = wordAssoBigrams[gram]
        biglist.append(word)
        wordAssoBigrams[gram] = biglist

with open(ifile, 'r') as words_input:
    words = words_input.readlines()
    for word in words:
        candi = []
        if word not in dic:
            candi = findCandidates(word, wordAssoBigrams)
        else:
            candi.append('Word is Correct')

        if len(candi) != 0:
            output = word + '\t'
            for w in  candi:
                output = output + w.getCand() + '\t'
                if i == min(3, len(candi)):
                    break;
                i = i + 1
            with open(ofile, 'w') as words_output:
                words_output.write(output)
