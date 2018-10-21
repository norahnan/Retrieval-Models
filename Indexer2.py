#!/usr/bin/env python
# coding: utf-8

# In[1]:


### imports and read json file ###

################################################################################

import numpy as np
import json
from pprint import pprint


#open file
with open('shakespeare-scenes.json') as f:
    data = json.load(f)
    

#pprint(data['corpus'][93])
#'playId': 'merry_wives_of_windsor',
#'sceneId': 'merry_wives_of_windsor:3.4',
#'sceneNum': 93,
#'text': 'scene v a room in the garter inn enter host and simple host what '


# In[2]:


### checks/ print ###

################################################################################

#print(invertls['fear'])
#print( metadata['playLen'])


# In[3]:


### term class ###

################################################################################

class termList(dict):
    def __init__(self, term):
        #remember the meta data
        self.currentDoc = 0 #the doc we are on 
        #self.docinv = {} #{2:[3,5,6], 5:[3,5,6] ...}
        #get incremented when building the list
        self.collection_f = 0  # total number of times a word appears in all of the docs 
        self.name = term
        
    #skip to the nth doc or beyond
    def skipTo(self, goto_doc):
        #if the wanted term is in the dictionary, dic has that key
        if(dic.get(goto_doc)!= None):
            #set current doc to that doc
            self.currentDoc = goto_doc
        #when we cannot find that doc, go to the next doc available
        else:
            #advance 1 till we get to a doc ID that is larger than goto doc
            while(self.currentDoc < goto_doc or dic.get(self.currentDoc)!= None):
                self.currentDoc += 1
            
    
    #add a word to the term list
    #when we find another of the same word for this term
    #given the term name, the position and in which doc we find it
    def addWord(self, word, wordplace, docid):
        #if we already have a doc id for it
        if(self.get(docid)!=None):
            #add to the list
            self[docid].append(wordplace)
            #increment the count
            self.collection_f += 1
            
        else:
            #create a list for that doc
            self[docid] = []
            #add word
            self[docid].append(wordplace)
            #increment the count
            self.collection_f += 1
            
            
    #get inverse doc frequency 
    def doc_term_weight(self, docid):
        return (1 + np.log10(len(self[docid]))) * np.log10(N_docs / len(self))
    
    #idf #docs/#docs with term
    def inverse_doc_f(self):
        return np.log10(N_docs / len(self))
    
    
    #tf #term in doc
    def doc_term_freq(self, docid):
        if(self.get(docid)!=None):
            return len(self[docid])
        else:
            return 0.5
        
        

        
        
    
        


# In[4]:


### global variables ###

################################################################################

#data about the collection as a whole
metadata = {}
metadata['collectionLen'] = 0 # number of doc in the collection
metadata['playLen'] = [] #list of pairs[play length, play name]
metadata['docLen'] = [] #list of pairs[doc length, doc name] 
metadata['docid'] = [] #list of doc names like play:2.2
metadata['terms'] = [] #list of strings of all the term names
metadata['totalWords'] = 0 #totally number of words in the collection
metadata['termINall'] = {} #mapping from term name to collection frequency

#look up table for reading file
#key is term, and value is where in the file to find the term
lookup_table = {}
loopup_comp = {}


### create the inverted list, update the metadata###

################################################################################

#get a new instance of the list object 
#key: term name value: a list of positions for each document
invertls = {}
#get the list of documents 
docs = data['corpus']
#to go through each doc
for x in range (0, len(docs)):
    curr_doc = docs[x]
    metadata['collectionLen'] += 1
    
    #remember the whole scnen and play name for later use
    metadata['docid'].append(curr_doc['sceneId'])
    #the play name
    playId = curr_doc['playId']
    #the whole play-scene name 
    sceneId = curr_doc['sceneId']   
    #use this as the key/ index in the list
    sceneNum = curr_doc['sceneNum']
    #split into words
    text = curr_doc['text'].split()
    metadata['docLen'].append([len(text), sceneId])
    metadata['totalWords'] += len(text)
    #loop through each word
    for i in range(0, len(text)):
        
        #get the word
        word = text[i]
        #if the term has been created
        if(invertls.get(word)!= None):
            #add the word to the term
            #object to list to term #given the term name, the position and in which doc we find it
            invertls[word].addWord(text[i], i, x)
            metadata['termINall'][text[i]] += 1
            
        #else create the term and add
        else:
            #when this is a new word
            metadata['terms'].append(text[i])
            #create a term
            newterm = termList(text[i])
            newterm.addWord(text[i], i, x)
            #add that word
            metadata['termINall'][text[i]] = 1
            invertls[text[i]] = newterm
    
currentplay = docs[0]['playId']
metadata['playLen'].append([0, currentplay])
currentplace = 0
#list of pairs[play name, play name]
#loop throught the docs to get length of each play
for doc in docs:
    #get the play this doc is in
    docplay = doc['playId']
    #get the index
    docnum = doc['sceneNum']
    #if this is a new play
    if(currentplay != docplay):
        currentplace += 1
        metadata['playLen'].append([len(doc['text'].split()), docplay])
        currentplay = docplay
        
        
    else:
        #add the doc length to the play len
        metadata['playLen'][currentplace][0] += len(doc['text'].split())
        

N_docs = len(docs)
avg_doclen = metadata['totalWords']/N_docs
print("DONE")
#print(avg_doclen)


# In[5]:


### scoring class ###

################################################################################
class scoring():
    
    def __init__(self, idf, tf, termname):
        self.idf = idf
        self.tf = tf
        #self.fi = fi
        #const
        self.k1 = 1.2
        self.k2 = 500
        self.b = 0.75
        
        self.miu = 1500
        self.lambda1 = 0.1
        self.c = metadata['totalWords']
        self.cqi = metadata['termINall'][termname]
        
        
    #bm25
    def bm25(self, doclen, ni, fi, qfi):
        k = self.k1 * (1 - self.b + (self.b * doclen)/(avg_doclen))
        temp1 = (((self.k1 + 1)*fi)/(fi+k))
        temp2 = (((self.k2+1)*qfi)/(self.k2+qfi))
        
        if((fi < 0.7)):
            return 0
        else:
            return np.log10((N_docs - ni +0.5)/(ni + 0.5)) * temp1 * temp2
    
    

    
    
    #vector space
    def vs(self, tf):
        if((tf < 0.7)):
                return 0
        else:
            return (1 + np.log10(self.tf)) * self.idf


    #JM In TREC evaluations, it has been shown that 
    #values of λ around 0.1 work well for short queries, 
    #whereas values around 0.7 are better for much longer queries.
    
    def jm(self, doclen, fi):
        
        sco = np.log10((1-self.lambda1)*(fi/doclen) + self.lambda1*(self.cqi/self.c))
        #print((1-self.lambda1)*(fi/doclen), self.lambda1*(self.cqi/self.c))
        return sco
    
    
    #DS
    #Typical values of μ that achieve the best results in 
    #TREC experiments are in the range 1,000 to 2,000 
    #(remember that col- lection probabilities are very small),
    def ds(self, doclen, fi):
        
        alpha =  self.miu/(doclen + self.miu)
        sco = np.log10((1-alpha)*(fi/doclen) + alpha*(self.cqi/self.c))
        return sco


# In[6]:


### search ###

################################################################################

def uniq(ls):
    lss = []
    for m in ls:
        if m not in lss:
            lss.append(m)
            
    return lss
#given a list of words, return the docID with the highest score
def searchwords(words):
    words = words.split()
    #a list to remember the best 10 docs
    good_docs = []
    #list for query term weights
    query_weights = []
    uniq_word = words.copy()
    uniq_word = uniq(uniq_word)
    #get Wtq
    for oneword in uniq_word:
        term = invertls[oneword]
        query_weights.append((1+np.log10(words.count(oneword)))*term.inverse_doc_f())
        

    
    #go through each document 
    for x in range (0, N_docs):
        #score 
        score = 0
        #doc vector
        doc_vector = []
        #get the doc lenth
        doclen = metadata['docLen'][x][0]
        
        #temp tpo find no word in  doc
        hasword = False
        #for each query word
        for y in range (0, len(uniq_word)):
            #print(x, uniq_word[y])
            #get the term inverted list object
            termls = invertls[uniq_word[y]]
            #inverse doc fre
            idf = termls.inverse_doc_f()
            #number of term in this doc
            tf = termls.doc_term_freq(x)
            #number of term in query
            qfi = words.count(uniq_word[y])
            #scoring object
            score_obj = scoring(idf, tf, uniq_word[y])
            
            hasword = hasword | (tf > 0.7)
            
            #for different scoring methods
            #score_part = score_obj.bm25(doclen, len(termls), tf, qfi)
            score_part = score_obj.jm(doclen, tf)
            #score_part = score_obj.ds(doclen, tf)
            #score_part = score_obj.vs(tf)
            
            #for the other three
            score += score_part
            #for vs
            #doc_vector.append(score_part)
        #score = np.dot(doc_vector, query_weights)/ doclen
        
        
        
        #if the doc has none of the query word 
        if not hasword:
            score = -100000
       
        #add the score and the doc number or doc name
        good_docs.append([score, metadata['docid'][x], x])
        #sort the list by the score
        good_docs.sort()
        #if the qsize is 10, remove the least element    
        if(len(good_docs) == 20):
            good_docs = good_docs[1:]
            
        list.reverse(good_docs)
            
    return good_docs
            
        

print('Done')


# In[7]:


Q1 = 'the king queen royalty'
Q2 = 'servant guard soldier'
Q3 = 'hope dream sleep'
Q4 = 'ghost spirit'
Q5 = 'fool jester player'
Q6 = 'to be or not to be'
Q7 = 'alas'
Q8 = 'alas poor'
Q9 = 'alas poor yorick'
Q10 = 'antony strumpet'
qs = [Q1,Q2,Q3,Q4,Q5,Q6,Q7,Q8,Q9,Q10]
#pprint(searchwords('setting the scene'))


# In[8]:


for x in range (len(qs)):
    raw_res = searchwords(qs[x])[:10]
    for y in range (len(raw_res)):
        #'nzhuang-bm25-1.2-500' 'nzhuang-ql-jm-0.1' nzhuang-ql-dir-1500
        reslt = 'Q' + str(x+1) + ' ' + 'skip' + ' ' + raw_res[y][1] + ' ' + str(y+1) + ' ' + str(float(raw_res[y][0])) + ' ' + 'nzhuang-ql-jm-0.1'
        print(reslt)


# In[9]:


ww = searchwords(Q2)
for m in ww:
    print(m[1], m[2]) 


# In[10]:


pprint(docs[213])


# In[ ]:




