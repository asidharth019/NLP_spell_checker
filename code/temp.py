

# file = open('styleWords.txt','w')
# with open('count_1w100k.txt', 'r') as inputfile:
#     lines = inputfile.readlines()
#     for i in lines:
#         cols = i.split('\t')
#         # file.write(cols[0]+'\t'+str(float(int(cols[1])/99133))+'\n')
#         file.write('<item>'+cols[0] + '</item>'+'\n')
# file.close()

corpus = open('brownCleaned.txt','r')
count = 0
for w in corpus.readlines():
    count += 1
    print(w)

print(count)
corpus.close()