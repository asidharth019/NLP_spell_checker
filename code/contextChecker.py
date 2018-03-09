import math
from nltk.corpus import stopwords

def removestopwords(text,cachedStopWords):
	return ' '.join([word for word in text.split() if word not in cachedStopWords])

class ContextChecker:
	textLines = []
	def __init__(self):
		corpusList =['../data/CS/w5.txt','../data/brown.txt']
		cachedStopWords = stopwords.words("english")
		for corpus in corpusList:
			with open(corpus) as f1:
				for line in f1.readlines():
					line = line.strip().upper()
					#line = removestopwords(line,cachedStopWords)
					lineTokens = line.split()
					self.textLines.append(lineTokens)
		
	def getRank(self,in_wrd, inAllWrds, k):
		#in_wrd="jury".lower()
		#inAllWrds= ['On', 'other', 'matters', 'the' , 'recommended', 'that', 'Four' , 'additional']
		#k=3

		corpus=''	
		inAllWrds=[x.upper() for x in inAllWrds] # converting all to lowercase
		THRES=1
		flagCond2=1
		A={}
		B={}
		count=0
		for wordList in self.textLines:
			if in_wrd in wordList:
				count = count + 1
				indx = wordList.index(in_wrd)
				leftSubArray=[]
				rightSubArray=[]
				minI = indx-k
				if (minI < 0):
					minI=0
				leftSubArray = wordList[minI: indx]	
			
				maxI = indx+k
				if (maxI > len(wordList)):
					maxI = len(wordList)
				rightSubArray = wordList[indx+1 : maxI]

				subArray=[]
				subArray= leftSubArray + rightSubArray		
				#print (subArray)	 
				#print ("---------")
				for word in subArray:
					if not word in A:
			        		A[word] = 1
					else:
						A[word] += 1

		B={x: A[x] for x in inAllWrds if x in A}

		A={}
		sub=[]
		for key in B:
			if B[key] > THRES: #and count - B[key]> THRES:  # All keys supporting the condition
				sub.append(key)
		#	if count - B[key] > NUM  and flagCond2==1:
		#		sub.append(key)

		sub_set = set (sub) # these words satifies the condition

		A={x: B[x] for x in sub_set if x in B} # finally taking only those which satifies the conditions

		lkh = 0
		if count > 0:
			deno=math.log(count)
			if len(A)==0:
				lkh=-1000
			else:
				for key in A: # since rest of the keys are 0 their lkh will be 0 	
					tmp =  math.log(A[key]) - deno
					lkh = lkh + tmp
				lkh = lkh + deno
		else:
			#print (in_wrd)
			#print ("count = 0 | The word is not there in corpus")
			lkh=-1000

		#print (lkh)
		return lkh



def main():
	contextChecker = ContextChecker()
	sourceWord='BROKEN'
	contextWords=['HEART']
	K=3
	print(contextChecker.getRank(sourceWord, contextWords, K))
if __name__ == "__main__":
    main()

