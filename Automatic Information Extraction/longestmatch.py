# To change this template, choose Tools | Templates
# and open the template in the editor.
import re
import string
import urllib
import urllib2


#Case 1.1: domain fixed (multiple words) and range sub str (multiple words) left or right side
def DomMWFRangeMW(domSubStr, rangeSubStr, line):
	#print rangeSubStr
    d = ""
    r = ""
    domWord = " ".join(domSubStr)
#        print domWord
    if domWord.strip() in line:
                #print domWord.strip()
        for rword in rangeSubStr:
	    if rword.strip() in line:
	        d = domWord.strip()
		r = rword.strip()
		return d, r
    return d, r
    
#Case 1.2: domain fixed (multiple words) range single word left or right side
def DomMWFRangeSW(domSubStr, rangeWord, line):
   
    l2 = ""
    dword = domWord.strip()
    rword = rangeSubStr.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = longestMatchRange(rword, l1)		
	return l2

    elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = longestMatchRange(rword, l1)		
	return l2

    elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = longestMatchRange(rword, l1)		
	return l2
	    	#print dword, line
    return l2


#Case 1.3: domain fixed (single word) range multiple words left or right side
def DomSWFRangeMW(domWord, rangeSubStr, line):
#        print domWord
   
    if domWord.strip() in line:
	for rword in rangeSubStr:
	    if rword.strip() in line:
		d = domWord.strip()
		r = rword.strip()
		return d, r
    return d, r

#Case 1.4: domain fixed (single word) range single word left or right side
def DomSWFRangeSW(domWord, rangeWord, line):
#        print domWord
   
    l2 = ""
    dword = domWord.strip()
    rword = rangeWord.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = RangeSW(rword, l1)		
	return l2

    elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = RangeSW(rword, l1)		
	return l2

    elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = RangeSW(rword, l1)		
	return l2
	    	#print dword, line
    return l2

#Case 2.1: domain substr (multiple words) left or right side and range multiple words fixed
def DomMWRangeMWF(domSubStr, rangeSubStr, line):
#        print domWord
    d = ""
    r = ""
    rangeWord = " ".join(rangeSubStr)
    if rangeWord.strip() in line:
        for domWord in domSubStr:
            if domWord.strip() in line:
                d = domWord.strip()
                r = rangeWord.strip()
                return d, r
    return d, r

#Case 2.2: domain single word left or right side and range multiple words fixed
def DomSWRangeMWF(domWord, rangeSubStr, line):
#        print domWord
   
   
    l2 = ""
    dword = domWord.strip()
    rword = rangeSubStr.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = longestMatchRange(rword, l1)		
	return l2

    elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = longestMatchRange(rword, l1)		
	return l2

    elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = longestMatchRange(rword, l1)		
	return l2
	    	#print dword, line
    return l2

#Case 2.3: domain multiple words left or right side and range single word fixed
def DomMWRangeSWF(domSubStr, rangeWord, line):
#        print domWord
  
    l2 =""
    rword = rangeWord.strip()
    #print domSubStr
        #print rangeSubStr
    for dword in domSubStr:	
        #if dword.strip() in line:
	dword = dword.strip()
	#x = re.search(r'(?i)(\s+)(%s)(\s+)|(?i)^(%s)(\s+)|(?i)(\s+)(%s)$'%(dword,dword,dword), line)
	if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
		l2 = RangeSW(rword, l1)		
		return l2

	elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
		l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
		l2 = RangeSW(rword, l1)		
		return l2

	elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
		l2 = RangeSW(rword, l1)		
		return l2
	    	#print dword, line
    return l2

#Case 2.4: domain single word left or right side and range single word fixed
def DomSWRangeSWF(domWord, rangeWord, line):
#        print domWord
  
    l2 = ""
    dword = domWord.strip()
    rword = rangeWord.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = RangeSW(rword, l1)		
	return l2

    elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = RangeSW(rword, l1)		
	return l2

    elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = RangeSW(rword, l1)		
	return l2
	    	#print dword, line
    return l2



def RangeSW(rangeWord, line):
    l1 =""
    rword = rangeWord.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(rword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(rword), '\\1<e2>\\2</e2>\\3', line)	
	return l1
			#print dword, rword
			#d = dword
			#r = rword
    elif(re.search(r'(?i)^(%s)(\s+)'%(rword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(rword), '<e2>\\1</e2>\\2', line)	
	return l1
    elif(re.search(r'(?i)(\s+)(%s)$'%(rword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(rword), '\\1<e2>\\2</e2>', line)	
	return l1
	
    return l1    
  

    

def longestMatchMe(domSubStr, rangeSubStr, line):
    d = ""
    r = ""
        #print domSubStr
        #print rangeSubStr
    for dword in domSubStr:            
        if dword.strip() in line:
            for rword in rangeSubStr:
                if rword.strip() in line:
		
                    d =dword.strip()
                    r = rword.strip()
                    return d, r
    return d, r	


def lMDomWordRangeSubstr(domWord, rangeSubStr, line):
	#print rangeSubStr
    d = ""
    r = ""
    l2= ""    
    dword = domWord.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = longestMatchRange(rangeSubStr, l1)		
	return l2

    elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = longestMatchRange(rangeSubStr, l1)		
	return l2

    elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = longestMatchRange(rangeSubStr, l1)		
	return l2
	    	#print dword, line
    return l2



def longestMatch(domSubStr, rangeSubStr, line):
  
    l2 =""
        #print domSubStr
        #print rangeSubStr
    for dword in domSubStr:	
        #if dword.strip() in line:
	dword = dword.strip()
	#x = re.search(r'(?i)(\s+)(%s)(\s+)|(?i)^(%s)(\s+)|(?i)(\s+)(%s)$'%(dword,dword,dword), line)
	if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
		l2 = longestMatchRange(rangeSubStr, l1)		
		return l2

	elif(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
		l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
		l2 = longestMatchRange(rangeSubStr, l1)		
		return l2

	elif(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
		l2 = longestMatchRange(rangeSubStr, l1)		
		return l2
	    	#print dword, line
    return l2

def longestMatchRange(rangeSubStr, line):
	l1 =""
	for rword in rangeSubStr:
		rword = rword.strip()			
		#y = re.search(r'(?i)(\s+)(%s)(\s+)|(?i)^(%s)(\s+)|(?i)(\s+)(%s)$'%(rword,rword,rword), line)
		if(re.search(r'(?i)(\s+)(%s)(\s+)'%(rword), line)):
			l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(rword), '\\1<e2>\\2</e2>\\3', line)	
			return l1
			#print dword, rword
			#d = dword
			#r = rword
		elif(re.search(r'(?i)^(%s)(\s+)'%(rword), line)):
			l1 = re.sub(r'(?i)^(%s)(\s+)'%(rword), '<e2>\\1</e2>\\2', line)	
			return l1
		elif(re.search(r'(?i)(\s+)(%s)$'%(rword), line)):
			l1 = re.sub(r'(?i)(\s+)(%s)$'%(rword), '\\1<e2>\\2</e2>', line)	
			return l1
	
	return l1

def exactMatchDomainWRangeW(domainW, rangeW, line):
#        print domWord
  
    l2 = ""
    dword = domainW.strip()
    rword = rangeW.strip()
#                print domWord.strip()
    if(re.search(r'(?i)(\s+)(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(dword), '\\1<e1>\\2</e1>\\3', line)
	l2 = exactMatchRangeW(rword, l1)		
	return l2

    if(re.search(r'(?i)^(%s)(\s+)'%(dword), line)):
	l1 = re.sub(r'(?i)^(%s)(\s+)'%(dword), '<e1>\\1</e1>\\2', line)
	l2 = exactMatchRangeW(rword, l1)		
	return l2

    if(re.search(r'(?i)(\s+)(%s)$'%(dword), line)):
	l1 = re.sub(r'(?i)(\s+)(%s)$'%(dword), '\\1<e1>\\2</e1>', line)
	l2 = exactMatchRangeW(rword, l1)		
	return l2
	    	#print dword, line
    return l2


def exactMatchRangeW(rangeW, line):
	l1 =""
    	rword = rangeW.strip()

    	if(re.search(r'(?i)(\s+)(%s)(\s+)'%(rword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)(\s+)'%(rword), '\\1<e2>\\2</e2>\\3', line)	
		return l1			
    	elif(re.search(r'(?i)^(%s)(\s+)'%(rword), line)):
		l1 = re.sub(r'(?i)^(%s)(\s+)'%(rword), '<e2>\\1</e2>\\2', line)	
		return l1
    	elif(re.search(r'(?i)(\s+)(%s)$'%(rword), line)):
		l1 = re.sub(r'(?i)(\s+)(%s)$'%(rword), '\\1<e2>\\2</e2>', line)	
		return l1
	
    	return l1   


def test():
	line= "nucleus The name refers collectively to the and gracile , which are present at the junction between the spinal cord and the medulla oblongata cuneate"
	domSubStr="cuneate"
	rangeSubStr = "oblongata"
	rangeSubStr = rangeSubStr.strip()
	x = re.search(r'(?i)(\s+)(%s)(\s+)|(?i)^(%s)(\s+)|(?i)(\s+)(%s)$'%(rangeSubStr,rangeSubStr,rangeSubStr), line)

	#x = re.search(r'(?i)(\s+)(%s)$'%(rangeSubStr), line)
	#x = re.search(r'(?i)^(%s)(\s*)'%(domSubStr), line)

	if(x!='None'):
		d =domSubStr.strip()
		r = rangeSubStr.strip()
		print d, r	
	                    

#longestMatchMe(domSubStr, rangeSubStr, line)

