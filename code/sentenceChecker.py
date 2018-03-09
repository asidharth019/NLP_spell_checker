from spellChecker import SpellChecker
from contextChecker import ContextChecker
from phraseChecker import PhraseChecker
from nltk.corpus import stopwords
import sys


def removestopwords(text):
    cachedStopWords = stopwords.words("english")

    return ' '.join([word for word in text.split() if word not in cachedStopWords])


def readSenFiletoList(fileName):
    sentenceList = []
    with open(fileName) as inpFile:
        lines = inpFile.readlines()
        for line in lines:
            line = line.strip()
            line = ''.join([c for c in line if c.isalnum() or c.isspace()])
            line = removestopwords(line)
            sentenceList.append(line.strip().upper())
    return sentenceList


# class SentenceChecker:
#	def __init__(self):
#		spellChecker = SpellChecker()
#		contextChecker = ContextChecker()
#		phraseChecker = PhraseChecker()

def checkCmdAgs():
    if len(sys.argv) != 3:
        print("pgm <InputFile> <OutputFile>")
        exit()
    return (sys.argv[1], sys.argv[2])


def main():
    (inpFile, outFile) = checkCmdAgs()
    pCorrect = PhraseChecker()
    wrongSentenceList = readSenFiletoList(inpFile)
    fout = open(outFile, "w");
    for sentence in wrongSentenceList:
        wPTokenList = sentence.split(' ')
        suggestions = pCorrect.getCorrect(sentence, 5)
        (prunedSuggestions, suggestIdx) = pCorrect.rank(suggestions, wPTokenList)
        count = 0
        out = wPTokenList[suggestIdx]
        for suggestion in prunedSuggestions:
            if suggestion.correctIdx == suggestIdx and count < 3:
                count = count + 1
                out = out + '\t' + suggestion.phrase[suggestIdx] + '\t' + str(suggestion.score)
        out = out + "\n"
        fout.write(out)
    fout.close()


if __name__ == "__main__":
    main()
