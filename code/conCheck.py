import sys
import stopwords
import doublemetaphone
import re
import nltk
from nltk.corpus import brown



import sys
import editdistance
from metaphone import doublemetaphone
import stopwords
gramcount = 2

class candInfo:
    def __init__(self, can, score):
        self.can = can
        self.score = score

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
                if ed1 <= 1:
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
        m = candInfo(cand, score)
        finalcand.append(m)
    finalcand.sort(key=lambda x: x.score, reverse=True)
    return finalcand


def findContextIncorrectCand(listword,pos,window,wordAssphones,dict,totWC,wordAssBig):
    corpus = open('brownCleaned.txt', 'r')
    phone = doublemetaphone(listword[pos])[0]
    # if phone in wordAssphones:
    listword = [str(listword[i]).upper() for i in range(len(listword))]
    candlist = []
    candlistInfo = findCandidates(listword[pos], wordAssBig, dict, totWC, wordAssphones)
    for c in candlistInfo:
        candlist.append(c.getCand())
    if phone in wordAssphones:
        candlist = candlist + wordAssphones[phone]
    candlist = list(set(candlist))
    probCand = []
    finalcand = []
    for candid in candlist:
        lines = corpus.readlines()
        candWordCount = 0
        listOfCandLines = []
        for line in lines:
            # if re.findall(candi, line):
            #     candWordCount += 1
            line = str(line).upper()
            line = line.strip()
            line = line.split(' ')
            if candid in line:
                candWordCount += 1
                listOfCandLines.append(line)

        startOfContext = -1
        endOfContext = -1
        if (pos - window) < 0:
            startOfContext = 0
        else:
            startOfContext = pos - window

        if (pos + window) > (len(listword) - 1):
            endOfContext = len(listword) - 1
        else:
            endOfContext = pos + window

        contextWordCount = 0
        contextWordProb = 1
        flag = 0
        if candWordCount != 0:
            for w in listword[startOfContext:endOfContext+1]:
                for candline in listOfCandLines:
                    if w in candline:
                        contextWordCount += 1
                        flag = 1
                contextWordProb *= contextWordCount/candWordCount
        if flag == 1:
            probCand.append(contextWordProb)
            m = candInfo(candid, contextWordProb)
        else:
            probCand.append(0)
            m = candInfo(candid, 0)
        finalcand.append(m)
    finalcand.sort(key=lambda x: x.score, reverse=True)
    return finalcand

def findContextCorrectCand(listword,window,wordAssphones,dict,totWC,wordAssBig):
    a=1

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
window = 3
with open(ifile, 'r') as sen_input:
    sentences = sen_input.readlines()
    # For finding wrong words in a sentence
    words = []
    stop = set(stopwords.get_stopwords('english'))
    for line in sentences:
        newline = line.strip()
        lineWords = newline.split(' ')
        finalInputWords = []
        for w in lineWords:
            if w.lower() not in stop:
                finalInputWords.append(w)
        pos = -1
        for w in finalInputWords:
            if w.upper() not in dic:
                words.append(w)
                pos = finalInputWords.index(w)
        wrongword = ''
        if pos != -1:
            wrongword = finalInputWords[pos]
            contextCand = findContextIncorrectCand(finalInputWords,pos,  window, wordAssoPhone,dic,totalWordCount,wordAssoBigrams)
        else:
            # contextCand = findContextCorrectCand(finalInputWords, window, wordAssoPhone,dic,totalWordCount,wordAssoBigrams)
            a = 1
        output = wrongword + '\t'

        if len(contextCand) != 0:
            i = 0
            for w in  contextCand:
                if i == min(3, len(contextCand)):
                    break
                output = output + str(w.getCand()).lower() + '\t'
                i = i + 1
        with open(ofile, 'a') as words_output:
            words_output.write(output + '\n')
