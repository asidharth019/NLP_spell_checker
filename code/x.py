import math

class PhraseChecker:	
	def getLikelihood(self,in_wrd, inAllWrds, k):
		#in_wrd="jury".lower()
		#inAllWrds= ['On', 'other', 'matters', 'the' , 'recommended', 'that', 'Four' , 'additional']
		#k=3

		corpus='../data/brown.txt'	
		inAllWrds=[x.lower() for x in inAllWrds] # converting all to lowercase
		THRES=10 
		flagCond2=1
		A={}
		B={}
		count=0
		with open(corpus,'r') as f:
			for line in f:
				line = line.strip().lower()
				wordList = line.split()
				if in_wrd in wordList:
					count = count + 1
					indx = wordList.index(in_wrd)
					leftSubArray=[]
					rightSubArray=[]
					if (indx-k > 0):
						leftSubArray = wordList[indx-k : indx]	
					if (indx+k < len(wordList)):
						rightSubArray = wordList[indx+1 : indx+k+1]
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
			if B[key] > THRES and count - B[key]> THRES:  # All keys supporting the condition
				sub.append(key)
		#	if count - B[key] > NUM  and flagCond2==1:
		#		sub.append(key)

		sub_set = set (sub) # these words satifies the condition

		A={x: B[x] for x in sub_set if x in B} # finally taking only those which satifies the conditions

		lkh = 0
		if count > 0:
			deno=math.log(count)
			for key in A: # since rest of the keys are 0 their lkh will be 0 	
				tmp =  math.log(A[key]) - deno
				lkh = lkh + tmp
		else:
			print ("count = 0 | The word is not there in corpus")

		#print (lkh)
		return lkh

def main():
	phraseChecker = PhraseChecker()
	in_wrd="jury".lower()
	inAllWrds=['On','other','matters','the','recommended','that','Four','additional']
	k=3
	
	lkh = phraseChecker.getLikelihood(in_wrd, inAllWrds,k)

	print ('In Main: ', lkh)

if __name__ == "__main__":
    	main()



