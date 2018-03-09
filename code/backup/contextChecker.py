import math
class ContextChecker:
	textLines = []
	def __init__(self):
		with open('/home/kraj/MEGA/NLP/data/CS/w5.txt') as f1:
			for line in f1.readlines():
				line = line.strip().upper()
				lineTokens = line.split()
				self.textLines.append(lineTokens)
		
	def getCoOccuranceCount(self,sourceWord,destWord,K):
		occurance_source = 0;
		occurance_dest = 0;
		occurance_candidate_context = 0;
		for lineTokens in self.textLines:
			flag =False
			if sourceWord in lineTokens[1:]:
				occurance_source =+  int(lineTokens[0])
				flag = True
			if destWord in lineTokens[1:]:
				occurance_dest =+  int(lineTokens[0])
				if flag:
					print(lineTokens)
					if abs(lineTokens.index(sourceWord) - lineTokens.index(destWord))<K:				
						occurance_candidate_context =+  int(lineTokens[0])
		retVals = []
		retVals.append(occurance_source)
		retVals.append(occurance_dest)
		retVals.append(occurance_candidate_context)
		return retVals

	def getRank1(self,sourceWord, contextWords, K):
		retScore = 0;
		print(sourceWord)
		print(contextWords)
		for contextWord in contextWords:
			
			score = self.getCoOccuranceCount(sourceWord,contextWord,K)
			#print(score)
			if(score[0]==0 or score[2]==0):
				tmpScore = 0
			else:
				tmpScore = score[2]*1.0/score[0]
				retScore = retScore + math.log(tmpScore)
		#print(retScore)
		return retScore
	
	def getRank(self,in_wrd, inAllWrds, k):
		#in_wrd="jury".lower()
		#inAllWrds= ['On', 'other', 'matters', 'the' , 'recommended', 'that', 'Four' , 'additional']
		#k=3

		corpus='../data/anc.txt'	
		inAllWrds=[x.upper() for x in inAllWrds] # converting all to lowercase
		THRES=1
		flagCond2=1
		A={}
		B={}
		count=0
		with open(corpus,'r') as f:
			for line in f:
				line = line.strip().upper()
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
		else:
			print (in_wrd)
			print ("count = 0 | The word is not there in corpus")
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

