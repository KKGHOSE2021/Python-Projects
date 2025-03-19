## Project Introduction:
This is a natural language processing project, where efficient string-matching algorithms were developed to extract relevant information from Wikipedia. Extraction  of  Relational  Patterns  is  particularly  useful  for various  Natural  Language  Processing  tasks  including information  extraction  from  text,  question  answering, and paraphrasing, as they allow to retrieve relevant information for a particular relation. In this work, String matching algorithms have been developed for  different  relational  types  in  different  cases, such that we  can  retrieve  related  sentences  for  each particular relation from a corpus extracted from Wikipedia (eka. WikiCorpus).  In string  matching processes,  we  will  extract  only  those  sentences  from WikiCorpus  that  match  the searched  string  from  a  pair  of predefined  relation-patterns  (domain  and  range)  to  our candidate sentences in WikiCorpus, so that we can collect a set of sentences for each particular relation. 

## Framework:
Wikipedia is a free online encyclopedia. Wikipedia articles consist mostly of free text, but also contains various types of structured information of wiki markup. Such information includes infobox templates, categorization information, images, geo-coordinates, links to external web pages, disambiguation pages, redirects between pages and link across different language editions of Wikipedia. The characteristics of Wikipedia make it as a rich lexical semantic resources. The DBpedia  project is also a community effort to extract structured information from Wikipedia. In this project, data are from two parts: relation instance from DBpedia (extracted from Wikipedia infobox), and sentences describing the relations from the corresponding Wikipedia pages. The basic idea is to maximize the power of both Wikipedia and DBpedia as seeds to harvest a set of such relational patterns. 

"<img src=\"./framework.png\">"

Figure-1 gives an overview of the  Wiki relation pattern extraction framework.

## Task Definition:
Finding all occurrences of a pattern in a text is a problem that arises frequently in text-editing programs. Typically, the text is a document being edited, and the pattern searched for is a particular word supplied by the user. For this problem, efficient algorithms can greatly aid the responsiveness of the text-editing program. 

The problem will be formalized as follow: A  pattern P is define as a string of characters from a finite alphabet  Σ which need to be identified within the input text. And we can define  sub-pattern  Ps as a sub-string of a pattern P. 
We assume that  given input text of length n as an array T[1...n]  and the pattern of length m as an array P[1...m], and considering that both the elements of pattern P and text T are characters drawn from a finite alphabet  Σ.

The goal of  pattern matching in a given text is to output the position of all occurrences of the patterns in the text, such that given input text, T = t[1...n]  and a set of r patterns P, where Pj   P (i ≤ j ≤r).

In this project, Wikipedia and DBpedia were processed in a parallel way. First. text corpus from Wikipedia was extracted and a short list of DBpedia relations was selected as a sample for this project. After that, sentences within text corpora were collected to match with the relation. Finally, some patterns were inferred from a set of sentences.
                                  
