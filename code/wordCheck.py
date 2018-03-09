import sys
import editdistance
from metaphone import doublemetaphone

gramcount = 2

def bigrams(word):
    bg = []
    for i in range(len(word)):
        bg.append(word[i:i+gramcount])
    return bg

def findCandidates(word, wordAssoBigrams):
    grams = bigrams(word)
    candidates = []
    scores = []

    for gram in grams:
        if gram in wordAssoBigrams:
            for listword in wordAssoBigrams[gram]:
                ed = editdistance.eval(listword)
                if ed <= 1:
                    candidates.append(listword)

ifile = sys.argv[1]
ofile = sys.argv[2]
dictionaryfile = 'count_1w100k.txt'

dic = {}
with open(dictionaryfile,'r') as inputfile:
    lines = inputfile.readlines()
    for i in lines:
        cols = i.split('\t')
        dic[cols[1]] = cols[2]

# For total frequency count
totalWordCount = 0
for word in dic:
    totalWordCount += dic[word]

# For listing the bigrams of all the words present
wordAssoBigrams = {}
for word in dic:
    grams  = bigrams(word)
    for gram in grams:
        biglist = []
        if gram in wordAssoBigrams:
            biglist = wordAssoBigrams[gram]
        biglist.append(word)
        wordAssoBigrams[gram] = biglist


with open(ifile,'r') as words_input:
    words = words_input.readlines()
    for word in words:
        candidates = []
        candidates.append(word)
        if word not in dic:
            candidates, scores = findCandidates(word, wordAssoBigrams)
        else:
            candidates  = candidates.append('Word is Correct')

        with open(ofile,'w') as words_output:
            words_output.write(candidates)

