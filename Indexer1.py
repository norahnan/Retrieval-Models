#!/usr/bin/env python
# coding: utf-8

# In[156]:


### imports and read json file ###

################################################################################

import numpy as np
import random
import json
from pprint import pprint
import time
import sys
from queue import PriorityQueue


#open file
with open('shakespeare-scenes.json') as f:
    data = json.load(f)
    

#pprint(data['corpus'][93])
#'playId': 'merry_wives_of_windsor',
#'sceneId': 'merry_wives_of_windsor:3.4',
#'sceneNum': 93,
#'text': 'scene v a room in the garter inn enter host and simple host what '


# In[160]:


### checks/ print ###

################################################################################

#print(invertls['fear'])
#print( metadata['playLen'])


# In[62]:


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
            
            
        


# In[157]:


### global variables ###

################################################################################

#data about the collection as a whole
metadata = {}
metadata['collectionLen'] = 0 # number of doc in the collection
metadata['playLen'] = [] #list of pairs[play length, play name]
metadata['docLen'] = [] #list of pairs[doc length, doc name] 
metadata['docid'] = [] #list of doc names like play:2.2
metadata['terms'] = [] #list of strings of all the terms
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
            #metadata['termINall'][text[i]] += 1
            
        #else create the term and add
        else:
            #when this is a new word
            metadata['terms'].append(text[i])
            #create a term
            newterm = termList(text[i])
            newterm.addWord(text[i], i, x)
            #metadata['termINall'][text[i]] += 1
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
        


# In[158]:


### find the avg scene len, long/short play/scene ###

################################################################################

#play length
metadata['playLen'].sort()
print('Shortest play: ', metadata['playLen'][0])

print('longest play: ', metadata['playLen'][-1])

#scene length
metadata['docLen'].sort()
print('Shortest scene: ', metadata['docLen'][0])
print('longest scene: ', metadata['docLen'][-1])

#ave scene
print('Ave scene length: ', metadata['totalWords']/metadata['collectionLen'])
#print(metadata['totalWords'])


# In[116]:


### vbyte compress and delta compress ###

################################################################################
#decimal - binary - add one(last byte)/zero before every 7 bit - 16 

        
def vbyte_encode(data):
    ls = []
    
    for x in range (0,len(data)):
        value = data[x]
        ls.append(0)
        if(value <= 128):
            ls[x] = value +128
            
        else:
            count = 0
            while(value >= 128):
                temp = value
                value = value>>7
            
                rest = temp - (value<<7)
                #print(bin(rest))
                if(count == 0):
                    #do notadd
                    count+=1
                    ls[x] += rest+128
                    #print(bin((rest<<(8*count))))
                    #ls[x] += (rest<<(8*count))
                
                else:
                    #add the value with zero before it
                    #print('else  ', (rest<<(8*count)))
                    ls[x] += (rest<<(8*count))
            
            #add 128 to the last 7 bits
            ls[x] += (value<<(8*count))
        
    return ls

def vbyte_decode(byte_input):
    intls = []
    for x in range(0, len(byte_input)):
        intls.append(0)
        #myint = int(byte_input[x], 2)
        myint = byte_input[x]
        
        #while we do not reach the last eight digits where the first is a one
        count = 0
        shift = 0
        #print(rest)
        while (myint >= 128):
            temp = myint
            myint = myint>>(7+shift)
            #print('myintfirst: ', myint)
            rest = temp - (myint<<(7+shift))
            shift = 1
            
            if(count == 0):
                #print(bin(rest))
                intls[x] += rest
                count += 1
                
            else:
                #add the rest 
                intls[x] += (rest<<(7*count))
                count += 1
            
        myint = myint>>1
        #print(myint)
        intls[x] += (myint<<(7*count))
        
    return intls
    
    
    
    
    
def delta_encode(ints):
    encoded = []
    encoded.append(ints[0])
    for x in range (1, len(ints)):
        encoded.append(ints[x] - ints[x-1])
        
    return encoded
    
    
    
def delta_decode(ints):
    decoded = []
    decoded.append(ints[0])
    for x in range (1, len(ints)):
        decoded.append(decoded[x-1] + ints[x]) 
        
    return decoded
     

#do the two encoding above given a term list
def compressTerm(term):
    for key in term:
        #compresss each pos list 
        term[key] = vbyte_encode(delta_encode(term[key]))
        #print(term[key])
        
    return term 


#given the bytes array
def decompress(mybytes):
    
    return delta_decode(vbyte_decode(mybytes))
    
#a = compressTerm({1:[2,4,5]})
#decompress(a)
    


# In[161]:


### WRITE to disk and update the look up table ###

################################################################################

filename = 'invli.bin'
comp_filename = 'comp_invli.bin'
filepos = 0
with open(filename, 'w') as f:
    #for each of the term
    for key in invertls:
        f.write(str(invertls[key]))
        #print(str(invertls[key]))
        lookup_table[key] = [f.tell(), f.tell()-filepos]
        filepos = f.tell()
         
        
        
filepos_c = 0
with open(comp_filename, 'w') as f:
    #for each of the term
    for key in invertls: 
        #original term's doc-position dictionary
        term_original = invertls[key]
        #compressed version
        comp = compressTerm(term_original)
        #print(comp)
        f.write(str(comp))
        lookup_table[key] = [f.tell(), f.tell()-filepos_c]
        filepos_c = f.tell()
        
        

        
#read from the disk by term name
#return the inverted list for that term 
def readTerm(termname, filename):
    #get where and what to read
    start, size = lookup_table[termname]
    with open(filename, 'r') as f:
        f.seek(start)
        term_jstr = f.read(size)
        
    return term_jstr


# In[88]:


### dice's coefficient ###

################################################################################

#get the best dice score term for the input term
def best_dice(term):
    #if our term only appear at the end of the test
    
    best_score = -100
    best_term = None
    #for each of the terms in the list
    for key in invertls:
        term_compare = invertls[key]
        d_ef = getD_coef(term, term_compare)
        #when we find a higher score
        if(d_ef>best_score):
            best_score = d_ef
            best_term = term_compare
        
    #print(best_score)
    return best_term
            
        


#get the coef for phrase12 and phrase21
def getD_coef(term1, term2):
    n1 = term1.collection_f
    n2 = term2.collection_f
    n12 = conFrequency(term1, term2)
    
    
    
    return n12 / (n1+n2)

#get the phrase frequency, input terms have the same current doc
def phraseInDoc(term1, term2):
    cur_docID = term1.currentDoc
    t1_pos = getDocPos(term1)
    t2_pos = getDocPos(term2)
    
    count = 0
    for x in range (0, len(t1_pos)):
        
        if(t1_pos[x]+1 in t2_pos or t1_pos[x]-1 in t2_pos):
            count += 1
            
    return count
        
    
    

#takes two term objects and find frequency they show up together
#we only care about when term1 comes in the front
def conFrequency(term1, term2):
    #get the two doc-position dictionaries
    t1_docs = term1
    t2_docs = term2
    
    #get the docid list for terms
    t1_docid1 = list(t1_docs.keys())
    t2_docid2 = list(t2_docs.keys())
    
    #find the intersection of the two
    common_doc = list(set(t1_docid1).intersection(t2_docid2))

    count = 0
    #print(common_doc)
    #in each doc where two terms both appear
    for docnum in common_doc:
        t1_pos = t1_docs[docnum]
        t2_pos = t2_docs[docnum]
        
        #increment positions by one
        t1_posIN = np.array(t1_pos) + 1
        t2_posIN = np.array(t2_pos) + 1
        
        #add t1t2 and t2t1
        #len(list(set(t1_pos).intersection(t2_posIN))) + 
        count += len(list(set(t2_pos).intersection(t1_posIN)))
        
    return count

        
    
testterm = best_dice(invertls['little'])    


# In[89]:


print(testterm.name)


# In[138]:


### randomly select 7 words from the vocabulary read from file and search ###

################################################################################

#given a list of words, return the docID with the highest score
def searchwords(words, meta, filename):
    #a list to remember the best 10 docs
    good_docs = []
    
    doclist = meta['docid']
    #go through each document 
    for x in range (0, len(doclist)):
        score = 0
        for oneword in words:
            word_invls = readTerm(oneword, filename)
            pos_word = word_invls[x]
            #get the score
            #add to the total score
            score += len(pos_word)
            
        #add the score and the doc
        good_docs.append([score, doclist[x]])
        #sort the list
        good_docs.sort()
        #if the qsize is 10, remove the least element    
        if(good_docs.qsize() == 11):
            good_docs.pop(0)
            
    return good_docs
            
        
#return a list of term names        
def getRanTerm(n, meta):
    #get the list of term names from metadata
    termNs = meta['terms']
    #randomly select 7 of the names
    sele_termN = random.sample(termNs, n)
    
    return sele_termN
    
    

#get 7*100 rand term names and store in file
#Query les:
#these should contain the 100 sets of 7 terms, one set per line, in a plain text le
#and the 100 sets of 7
#two term phrases, one set per line
with open('single_wordQ.txt', 'a') as f:
    
    for x in range(0, 100):
        st= ''
        terms7 = getRanTerm(7, metadata)
        #for each of the 7 terms
        for term in terms7:
            st = str(term)+' '+st 
        f.write(st + '\n' )


print('Done')


# In[ ]:


def read7():
    a = []
    with open('single_wordQ.txt', 'r') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for line in content:
        line = line.split()
        
        a.append(line)
    return a

singlewords = read7()
with open('two_wordQ.txt', 'a') as f:
    for x in range(0, 100):
        st= ''
        terms7 = singlewords[x]
        #for each of the 7 terms
        for term in terms7:
            st = str(term)+' '+ best_dice(invertls[term]).name + ' '+st 
            
        print(x)
        f.write(st + '\n' )


print('Done')


# In[148]:


def read14():
    a = []
    with open('two_wordQ.txt', 'r') as f:
        content = f.readlines()
    content = [x.strip() for x in content]
    for line in content:
        line = line.split()
        
        a.append(line)
    return a


twowords = read14()
lstime_comp = [] #[[7,14], [7,14]......]
lstime_uncomp = []
docls7c = []
docls14c = []
docls7uc = []
docls14uc = []
if(print(sys.argv)[1] == 'comp'):
    #run the compressed search on 7 and 14
    for x in range (0, 100):
        starttime7 = time.time()
        #get the largest score
        doc7 = searchwords(singlewords[x], metadata, comp_filename)[-1]
        endtime7 = time.time()
        docls7c.append(doc7)
        
        starttime14 = time.time()
        #get the largest score
        doc14 = searchwords(twowords[x], metadata, comp_filename)[-1]
        endtime14 = time.time()
        docls14c.append(doc14)
        #time difference
        lstime_comp.append([endtime7-starttime7, endtime14-starttime14])
#when not compressed
else:
    #run the compressed search on 7 and 14
    for x in range (0, 100):
        starttime7u = time.time()
        #get the largest score
        doc7u = searchwords(singlewords[x], metadata, filename)[-1]
        endtime7u = time.time()
        docls7uc.append(doc7u)
        
        starttime14u = time.time()
        #get the largest score
        doc14u = searchwords(twowords[x], metadata, filename)[-1]
        endtime14u = time.time()
        docls14uc.append(doc14u)
        #time difference
        lstime.append([endtime7u-starttime7u, endtime14u-starttime14u])


# In[ ]:





# In[ ]:




