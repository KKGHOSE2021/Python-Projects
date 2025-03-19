# -*- coding: utf-8 -*-

##Unicode handling
import codecs
from substring import filterList
import re
#import nltk
import os
import string
import urllib
import urllib2
import sys
from substring import *
from longestmatch import *



fileoutpath = "/home/ghose/relationOutput/"

relationDictionary = {}
#To take relation input in array
def create2DTable(fileList):
	for relFile in fileList:
		table2D = []
		for line in open(relFile, 'r').readlines():
			ll=line.strip()
			#compairing with 1 is a kind of ugly but required if there is empty line
			if(len(ll)>1):
				table2D.append(re.split("\t",ll))
			#print relation[0]
		relationDictionary[relFile] = table2D

stopWordList = []
def readStopWord(fileStopWord):
	for line in open(fileStopWord, 'r').readlines():
		#print line,"HELLO"
		ll=line.strip()
		if(len(ll)>=1):
			stopWordList.append(ll)

def removeStopWord(wordList):
	newList = []
	for word in wordList:
		if word not in stopWordList:
			newList.append(word)
	return newList

def removeBracket(txt):
	words = re.sub(r"\(.*?\)", "", txt)
	words = words.replace("  ", " ")
	#print txt, " REMOVE ", words
	return words

#subString(ABC AB BC A B) algorithm-3/4

def findAndWrite(domainW, rangeW):
	text = ""
	domListLeft = []
	rangeListLeft = []
	domListRight = []
	rangeListRight = []
	domRemParenList = []
	rangeRemParenList = []
	domSingleWordR = ''
	rangeSingleWordR = ''
	domSingleWordL = ''
	rangeSingleWordL = ''
	rangeSingleWord = ''
	domSingleWord = ''
	"""name string matching without parenthesis string for domain and range"""
	domRemParen = removeBracket(domainW)
	rangeRemParen = removeBracket(rangeW)
	dRemPList = domRemParen.split()
	rRemPList = rangeRemParen.split()
#        print domRemParen, rangeRemParen
#        print dRemPList, rRemPList

	c1_flag = False
	c2_flag = False
	c3_flag = False
	c4_flag = False

	domList = []
	rangeList = []


	#4.1 domain multiple strings and range multiple strings:

	if (type(dRemPList) == type(list()) and len(dRemPList)>1) and (type(rRemPList) == type(list()) and len(rRemPList)>1):
		c1_flag = True
				#print c1_flag
		domRemParenList = dRemPList
		rangeRemParenList = rRemPList
		domSubStrL = subStringLeft(domRemParen)
		rangeSubStrL = subStringLeft(rangeRemParen)
		domSubStrR = subStringRight(domRemParen)
		rangeSubStrR = subStringRight(rangeRemParen)

				#print domRemParenList, rangRemParenList
				#print domSubStrL, rangeSubStrL
				#print domSubStrR, rangeSubStrR
		tmp=" ".join(domRemParenList)

		domList.append(tmp)
		domList.extend(domSubStrL)
		domList.extend(domSubStrR)
		domList.extend(domRemParenList)
		domList = removeStopWord(domList)
		domList = filterList(domList)


		tmp = " ".join(rangeRemParenList)
				#print tmp
		rangeList.append(tmp)
		rangeList.extend(rangeSubStrL)
		rangeList.extend(rangeSubStrR)
		rangeList.extend(rangeRemParenList)
		rangeList = removeStopWord(rangeList)
		rangeList = filterList(rangeList)


	##4.2 domain single string and range multiple strings:

	elif (type(domRemParen) == type(str())) and (type(rRemPList) == type(list()) and len(rRemPList)>1):

		c2_flag = True
		rangRemParenList = rRemPList
		domSingleWord = "".join(domRemParen)
		rangeSubStrL = subStringLeft(rangeRemParen)
		rangeSubStrR = subStringRight(rangeRemParen)

				#domSingleWord = " ".join(domRemParen)

		tmp = " ".join(rangeRemParenList)
				#print tmp
		rangeList.append(tmp)
		rangeList.extend(rangeSubStrL)
		rangeList.extend(rangeSubStrR)
		rangeList.extend(rangeRemParenList)
		rangeList = removeStopWord(rangeList)
		rangeList = filterList(rangeList)
				#print c2_flag
#                print domSingleWord
#                print rangeSubStrL, rangeSubStrR


	#4.3 domain multiple strings and range single string :

	elif (type(dRemPList) == type(list()) and len(dRemPList)>1) and (type(rangeRemParen) == type(str())):

		c3_flag = True
		domRemParenList = dRemPList
		rangeSingleWord = "".join(rangeRemParen)
		domSubStrL = subStringLeft(domRemParen)
		domSubStrR = subStringRight(domRemParen)
		
		tmp = " ".join(domRemParenList)
		domList.append(tmp)
		domList.extend(domSubStrL)
		domList.extend(domSubStrR)
		domList.extend(domRemParenList)
		domList = removeStopWord(domList)
		domList = filterList(domList)


	#4.4 domain single word & range single word:

	elif (type(domRemParen) == type(str())) and (type(rangeRemParen) == type(str())):

		c4_flag = True
		domSingleWord = "".join(domRemParen)
		rangeSingleWord = "".join(rangeRemParen)

	for wikiFile in fileListWiki:
		filetext = open(wikiFile, "r").read()
		sentlist = re.split(u'[\n|\r\n]+',filetext)
		for i in sentlist:
						#print len(domRemParenList), domRemParenList, len(rangRemParenList), rangRemParenList
#                        print len(domRemParenList), domRemParenList, rangeListRight
#                        print domRemParen.strip(), rangeRemParen.strip()
			rangeW = rangeW.strip()
			domainW = domainW.strip()
			rangeRemParen = rangeRemParen.strip()
			domRemParen = domRemParen.strip()

						#case 1: exact matching domain and range fixed
			if domainW in i and rangeW in i:
				#i1 = re.sub('(?i)\\b(%s)\\b'%domainW, '<w1>\\1</w1>', i)
				#i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rangeW, '<w2>\\1</w2>', i1)	
				#text = text + i2 + "\n"	
				#continue		
				#s_tag = re.compile(r"(<s[^>]+>)(.*?)(</s>)")
				#line_parts = re.search(s_tag, i)
    				#start = line_parts.group(1)
    				#content = line_parts.group(2)
    				#end = line_parts.group(3)

    				#left_match = "(?i)\\b(%s)\\b" % domainW
    				#right_match = "(?i)\\b(%s)\\b" % rangeW
   				#if re.search(left_match, content) and re.search(right_match, content):
        				#line1 = re.sub(left_match, '<w1>\\1</w1>', content)
        				#line2 = re.sub(right_match, '<w2>\\1</w2>', line1)
        				#print(line_parts.group(1) + line2 + line_parts.group(3))
					#text = (line_parts.group(1) + line2 + line_parts.group(3))
					#text = text + "\n"
				#print domainW, rangeW
							
				#l1 = exactMatchDomainWRangeW(domainW, rangeW, i)
				#if(l1!=''):
					#text = text + l1 + "\n"
					#print text
				line = i.replace(domainW, '<e1>' + domainW + '</e1>')
			    	lineR = line.replace(rangeW, '<e2>' + rangeW + '</e2>')
				#print lineR
				text = text + lineR + "\n"				
				#i1 = re.sub('(?i)(\s+)(%s)(\s+)'%domainW, '\\1<e1>\\2</e1>\\3', i)
				#i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rangeW, '\\1<e2>\\2</e2>\\3', i1)
				#text = text + i2 + "\n"
				continue
						#case 2.1: domain fixed and range bracket removed
			elif domainW in i and rangeRemParen in i:
								#print domRemParen.strip(), rangeRemParen.strip()
				#l2 = exactMatchDomainWRangeW(domainW, rangeRemParen, i)
				#if(l2!=''):
				#	text = text + l2 + "\n"				
				line = i.replace(domainW, '<e1>' + domainW + '</e1>')
			    	lineR = line.replace(rangeRemParen, '<e2>' + rangeRemParen + '</e2>')
				#print lineR
				text = text + lineR + "\n"				
				#i1 = re.sub('(?i)(\s+)(%s)(\s+)'%domainW, '\\1<e1>\\2</e1>\\3', i)
				#i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rangeRemParen, '\\1<e2>\\2</e2>\\3', i1)
				#text = text + i2 + "\n"
				continue
						#case 2.2: domain bracket removed and range fixed
			elif domRemParen in i and rangeW in i:
				#l3 = exactMatchDomainWRangeW(domRemParen, rangeW, i)
				#if(l3!=''):
				#	text = text + l3 + "\n"					
				#print domRemParen.strip(), rangeRemParen.strip()
				line = i.replace(domRemParen, '<e1>' + domRemParen + '</e1>')
			    	lineR = line.replace(rangeW, '<e2>' + rangeW + '</e2>')
				#print lineR
				text = text + lineR + "\n"				
				#i1 = re.sub('(?i)(\s+)(%s)(\s+)'%domRemParen, '\\1<e1>\\2</e1>\\3', i)
				#i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rangeW, '\\1<e2>\\2</e2>\\3', i1)
				#text = text + i2 + "\n"
				continue
						#case 2.3: domain bracket removed and range bracket removed
			elif domRemParen in i and rangeRemParen in i:
				#l4 = exactMatchDomainWRangeW(domRemParen, rangeRemParen, i)
				#if(l4!=''):
				#	text = text + l4 + "\n"	
#                                print domRemParen.strip(), rangeRemParen.strip()
				line = i.replace(domRemParen, '<e1>' + domRemParen + '</e1>')
			    	lineR = line.replace(rangeRemParen, '<e2>' + rangeRemParen + '</e2>')
				#print lineR
				text = text + lineR + "\n"					
				#i1 = re.sub('(?i)(\s+)(%s)(\s+)'%domRemParen, '\\1<e1>\\2</e1>\\3', i)
				#i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rangeRemParen, '\\1<e2>\\2</e2>\\3', i1)
				#text = text + i2 + "\n"
				continue

			###########################CASE 1##########################
			elif(c1_flag):
				#print "c1_flag"
							#4.1 domain multiple words fixed and range multiple words
				#dom, rang = longestMatch(domList, rangeList, i)
				#dom = ''
				#rang = ''
				l5 = longestMatch(domList, rangeList, i)
				if(l5!=''):
					text = text + l5 + "\n"				

				#print "YES ", d
				
				#if(dom !='' and rang !=''):
					#print "DOM: ", dom, "RANGE: ",rang
					#print i
					#i1 = re.sub(r'(?i)\b(\s+)(%s)(\s+)\b'%dom, '\\1<e1>\\2</e1>\\3', i)
					#i2 = re.sub(r'(?i)\b(\s+)(%s)(\s+)\b'%rang, '\\1<e2>\\2</e2>\\3', i1)
					
					#line = i.replace(dom, '<e1>' + dom + '</e1>')
			    		#lineR = line.replace(rang, '<e2>' + rang + '</e2>')
					#print lineR
					#text = text + lineR + "\n"
	
#					text = text + i2 + "\n"
					#print "C1: ",text
					continue
			elif(c2_flag):
						###################CASE 2############################
				#print "c2_flag"
				#4.2 domain single words fixed and range multiple words
				#dom = ''
				#rang = ''
				l6 = DomSWRangeMWF(domSingleWord, rangeList, i)
				if(l6!=''):
					text = text + l6 + "\n"				
				#dom, rang = DomSWFRangeMW(domSingleWord, rangeList, i)
				#if(dom !='' and rang !=''):
				#	i1 = re.sub('(?i)(\s+)(%s)(\s+)'%dom, '\\1<e1>\\2</e1>\\3', i)
				#	i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rang, '\\1<e2>\\2</e2>\\3', i1)
				#	text = text + i2 + "\n"
				#	print "C2: ",text
					continue
			elif(c3_flag):
						########################CASE 3#######################################
				#print "c3_flag"
				#4.3 domain multiple words fixed and range single word
				#dom = ''
				#rang = ''
				l7 = DomMWRangeSWF(domList, rangeSingleWord, i)
				if(l7!=''):
					text = text + l7 + "\n"	
				#dom, rang = DomMWRangeSWF(domList, rangeSingleWord, i)
				#if(dom !='' and rang !=''):
				#	i1 = re.sub('(?i)(\s+)(%s)(\s+)'%dom, '\\1<e1>\\2</e1>\\3', i)
				#	i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rang, '\\1<e2>\\2</e2>\\3', i1)
				#	text = text + i2 + "\n"
				#	print "C3: ",text
					continue
			elif(c4_flag):
						######################CASE 4####################
				#print "C4_flag"
							#4.4 domain single word fixed and range single word
				if (domSingleWord != '' and rangeSingleWord != ''):
					l8 = DomSWFRangeSW(domSingleWord, rangeSingleWord, i)
					#dom = ''
					#rang = ''
					if(l8!=''):
						text = text + l8 + "\n"	
					#dom, rang = DomSWFRangeSW(domSingleWord, rangeSingleWord, i)
					#if(dom !='' and rang !=''):
					#	i1 = re.sub('(?i)(\s+)(%s)(\s+)'%dom, '\\1<e1>\\2</e1>\\3', i)
					#	i2 = re.sub('(?i)(\s+)(%s)(\s+)'%rang, '\\1<e2>\\2</e2>\\3', i1)
					#	text = text + i2 + "\n"
						#print text
						continue


	return text

def findRelationInWiki():
	for rel, relTable in relationDictionary.iteritems():
		text = ""
		fName = os.path.basename(rel)
		out = file( fileoutpath+fName+".xml", "w" )
		#out.write( codecs.BOM_UTF8 )
		#print rel, len(relTable)# relTable
		for row in relTable:
			#print row
			array = row
			if(len(array)==2):
				#print array[0], array[1]
				text = findAndWrite(array[0].strip(), array[1].strip())
				if(len(text)>0):
					out.write(text)

			#print col1, col2
		out.close()

#To list relation input
def listFilesRelation(dirpath): 
	#print dirpath
	for dirname, dirnames, filenames in os.walk(dirpath):
#	    for subdirname in dirnames:
#		os.path.join(dirname, subdirname)
		for filename in filenames:
			fPath = os.path.join(dirname, filename)
		#print os.path.basename(filename)
		        fileListRelation.append(fPath)
#To list wikifile
def listFilesWiki(dirpath):
	#print dirpath
#	out = file("wiki.files", "w" )
	for dirname, dirnames, filenames in os.walk(dirpath):
		for subdirname in dirnames:
			os.path.join(dirname, subdirname)
		for filename in filenames:
			fPath = os.path.join(dirname, filename)
			fileListWiki.append(fPath)
#			out.write(fPath+"\n");
#	out.close()

#for fileN in fileList:
fileListRelation = []
fileListWiki = []
listFilesRelation(sys.argv[1])
listFilesWiki(sys.argv[2])
readStopWord("/home/ghose/codeCollection/fileStopWord.txt")
create2DTable(fileListRelation)

findRelationInWiki()

#out.close()

print "DONE!!"
