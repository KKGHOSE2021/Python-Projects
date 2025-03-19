# To change this template, choose Tools | Templates
# and open the template in the editor.
import re
import string
import urllib
import urllib2

def subString(searchTxt):
	searchWords = []
	words = searchTxt.split()
	"""Left most words"""
	searchWords.extend([' '.join(words[:i]) for i in range(len(words))][1:])
        #searchWords.extend([' '.join(words[:i]) for i in xrange(len(words), 0, -1)])
	"""Right most words"""
	searchWords.extend([' '.join(words[i:]) for i in range(len(words))][1:])
        #searchWords.extend([' '.join(words[i:]) for i in xrange(0, len(words),  1)])
	"""all words"""
	searchWords.extend(words)
	new_list = list(set(searchWords))
	#searchWords = removeStopWord(new_list)
	searchWords = filter(None, searchWords)
	searchWords = sorted(searchWords, key=len, reverse=True)# to look first for the longest string match
	return searchWords


def subStringList(leftList, rightList):
	#print searchTxt
	searchWords = []

	searchWords.extend(leftList).extend(rightList)
	searchWords = filter(None, searchWords)
	##searchWords.extend([' '.join(words[:i]) for i in xrange(len(words), 0, -1)])
	searchWords = sorted(searchWords, key=len, reverse=True)# to look first for the longest string match
	#print searchWords
	return searchWords

#single substring matching

def subStringWords(searchTxt):
	searchWords = []
	words = searchTxt.split()
	words = removeStopWord(words)
	searchWords.extend(words)
	searchWords = filter(None, searchWords)
	searchWords = sorted(searchWords, key=len, reverse=True)# to look first for the longest string match
	return searchWords

# subString (ABC AB A) algorithm-1/2
def subStringLeft(searchTxt):
	#print searchTxt
	searchWords = []
	words = searchTxt.split()
#        print words
#    	for i in range(len(words)):

        searchWords.extend([' '.join(words[:i]) for i in range(len(words))][1:])

	searchWords = filter(None, searchWords)
	##searchWords.extend([' '.join(words[:i]) for i in xrange(len(words), 0, -1)])
	searchWords = sorted(searchWords, key=len, reverse=True)# to look first for the longest string match
	#print searchWords
	return searchWords

#subString (ABC BC C) algorithm-1/2
def subStringRight(searchTxt):
	searchWords = []
	words = searchTxt.split()
	searchWords.extend([' '.join(words[i:]) for i in range(len(words))][1:])
	#searchWords.extend([' '.join(words[i:]) for i in xrange(0, len(words), 1)])
	searchWords = filter(None, searchWords)
	searchWords = sorted(searchWords, key=len, reverse=True)# to look first for the longest string match
	return searchWords

def filterList(listdata):
    
    listdata = filter(None, listdata)    

#    data = list(set(data))
    data = list(set(listdata))
#    data = sorted (listdata, key=len, reverse=True)
    data = sorted (data, key=len, reverse=True)
#    print data
    return data



