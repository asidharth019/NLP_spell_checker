import editdistance
import sys

def spellCheck(wrongWord,):

    gramcount = 2
    bigrams = []
    for i in range(len(wrongWord)):
        bigrams.append(wrongWord[i:i+gramcount])

