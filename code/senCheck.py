import sys
import editdistance
from metaphone import doublemetaphone
import stopwords
gramcount = 2

class candInfo:
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


def findCandidates(word1, wordAssoBigrams1, dict, totalWC, wordAssoPhn1):
    word1 = word1.upper()
    grams1 = bigrams(word1)
    candidates1 = []



    for gr in grams1:
        if gr in wordAssoBigrams1:
            for listword in wordAssoBigrams1[gr]:
                ed1 = editdistance.eval(listword, word1)
                if ed1 <= 4:
                    candidates1.append(listword)

    phn = doublemetaphone(word1)[0]
    if phn in wordAssoPhn1:
        candidates1 = candidates1 + wordAssoPhn1[phn]

    candidates1 = list(set(candidates1))

    finalcand = []
    for cand in candidates1:
        ed1 = editdistance.eval(word1,cand)

        score = (max(len(cand),len(word1)) - ed1) + (float(dict[cand])/totalWC)

        if cand[:0] == word1[:0]:
            score += 1
        if cand[:1] == word1[:1]:
            score += 1
        if cand[-1:] == word1[-1:]:
            score += 1
        if cand[-2:] == word1[-2:]:
            score += 1

        if len(cand) == len(word1):
            score += 1

        # score = score*(dict[cand]/totalWC)
        m = candInfo(cand, score, ed1)
        finalcand.append(m)
    finalcand.sort(key=lambda x: x.score, reverse=True)
    return finalcand


# ifile = sys.argv[1]
# ofile = sys.argv[2]

ifile = 'sentences_input.txt'
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
wordAssoPhone = {}
for word in dic:
    grams = bigrams(word)
    for gram in grams:
        biglist = []
        if gram in wordAssoBigrams:
            biglist = wordAssoBigrams[gram]
        biglist.append(word)
        wordAssoBigrams[gram] = biglist

    # For matching the phonetics
    phone = doublemetaphone(word)[0]
    phnlist = []
    if phone in wordAssoPhone:
        phnlist = wordAssoPhone[phone]
    phnlist.append(word)
    wordAssoPhone[phone] = phnlist

of = open(ofile,'w')
of.close()

with open(ifile, 'r') as sen_input:
    sentences = sen_input.readlines()
    # For finding wrong words in a sentence
    words = []
    stop = set(stopwords.get_stopwords('english'))
    for line in sentences:
        line = line.strip()
        for w in line.split(' '):
            if w.upper() not in dic and w.lower() not in stop:
                words.append(w)
    for word in words:
        candi = []
        if word not in dic:
            candi = findCandidates(word, wordAssoBigrams, dic, totalWordCount,wordAssoPhone)
        else:
            candi.append('Word is Correct')

        output = word + '\t'

        if len(candi) != 0:
            i = 0
            for w in  candi:
                if i == min(3, len(candi)):
                    break
                output = output + str(w.getCand()).lower() + '\t'
                i = i + 1
        with open(ofile, 'a') as words_output:
            words_output.write(output + '\n')
