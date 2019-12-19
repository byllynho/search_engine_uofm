#!/usr/local/bin/python3

# Author - Felipe de Oliveira

# Subject - HW 7, Information Retrieval

# Date - Nov. 19, 2019

###################################
# Description
###################################
'''
Develop a retrieval program that takes as input an user query in the form of
a set of keywords, uses the inverted index to retrieve documents containing
at least one of the keywords, and then ranks these documents based on
cosine values between query vector and document vectors. The output should be
a ranked list of documents with links to the original documents, i.e. URLs to
the original documents on the web. Include web interface.
'''

###################################
# Imports
###################################
import sys
import os
import operator
from math import log, sqrt
import cgi
from time import time
import json

import cgitb
cgitb.enable()

import nltk
import string
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize


###################################
# Constants
###################################
INDEX_FILE = 'invertedIndex.txt'
BASE_DIR = os.getcwd()
TOTAL_DOCS = 10001

###################################
# Functions
###################################

# code to show html start page
def Start():
    # precondition: None
    # postcondition: start page on the browser

    print ("Content-type:text/html\n\n")
    print ("<html>")
    print ("<head>")
    print ("<title>Memphis Search</title>")
    print("<div><h1 align='center' style='padding-top:5%'>Memphis Search</h1></div>")
    print ("</head>")
    print ("<body>")
    print("<form action='#' method='post'>")
    print("<div style='text-align:center'><input type='text' style ='corner-radius:5px;height:50px' name='searchQuery' size='100' placeholder='What would you like to search?'></div>")
    print("<div style='text-align:center'><input type='submit' style ='height:36px;color:blue;background-color:lightgrey;font-size:16px' name='search' value='Search'/></div>")
    print("</form>")

# read index file
def readIndex(fileName):
    # precondition: text file with inverted index of documents
    # postcondition: python dictionary

    # change directory to find file
    os.chdir(BASE_DIR)

    # open and read as dictionary
    with open(fileName, 'r') as txtFile:
        indexedDocs = json.load(txtFile)

    os.chdir(BASE_DIR)

    return(indexedDocs)

# read dictionary
def getWordData(word, index):

    # try reading word information from dictionary
    # if error, word not included and return zero
    
    try:
        total = 0
        for doc, doc_word_frequency in index[word].items():
            
            total += int(doc_word_frequency)

        docFreq = total
        docList = index[word]

    except:
        docFreq = 0
        docList = 0

    data = [docFreq, docList]

    return(data)

# calculate tfIdf weight
def get_TfIdf(doc, docList, docFreq):
    # precondition: document, the doc list (with term frequency), and docFreq
    # postcondition: tfidf weight

    # if the word is in the index...
    if docFreq > 0:

        # get term frequency in the document
        termFreq = docList[doc]

        # calculate the tfidf weight
        tfIdf = termFreq * log(TOTAL_DOCS/docFreq)

    # if the word isn't in the index.
    else:
        tfIdf = 0

    return(tfIdf)

# stem the query to match the index
def stemQuery(text):

	text = text.lower()

	punctuation = "[]!@#$%^&*()_+<>?:.,;}{'\"/\-0123456789="

	for c in text:
	    if c in punctuation:
	        text = text.replace(c, "")

	# Now we have a text variable which contains all the text derived #from our file.
	# Now, we will clean our text variable, and create a list of keywords.
	#The word_tokenize() function will break our text phrases into #individual words
	
  
	word_tokens = word_tokenize(text) 

	#We initialize the stopwords variable which is a list of words like #"The", "I", "and", etc. that don't hold much value as keywords
	#We create a list comprehension which only returns a list of words #that are NOT IN stop_words and NOT IN punctuations.
	stop_words = set(stopwords.words('english'))
	keywords = [w for w in word_tokens if not w in stop_words] 

	#We use this function to work with the morphological variations of the words
	keywords_final = []
	lemmatizer = WordNetLemmatizer()
	for word in keywords:
		keywords_final.append(lemmatizer.lemmatize(word))
		
	#return a list of words
	return keywords_final  

# retrieve final ranks
def getRanks(relevantLinks, queryWeight_sq):
    # precondition: dicitonary of relevant links and the sum of queryWeight^2 (to normalize)
    #               relevantLinks = {
    #                   'dotProd': dot product of doc and query
    #                   'length': the sum of the squares of tfidf
    #               }
    # postcondition: final ranks

    finalRank = {}

    # loop through each document
    for link in relevantLinks:

        # numerator --> Di * Q
        top = relevantLinks[link]['dotProd']

        # denominator --> |Di|*|Q|
        bottom = sqrt(relevantLinks[link]['length']) * sqrt(queryWeight_sq)

        try:
            # final rank
            finalRank[link] = top/bottom

        except:
            finalRank[link] = 0

    return(finalRank)

# get relevant links based on the query
def getRelevantLinks(query, index):
    # precondition: a list of query words
    # postcondition: a dictionary of links and (unnormalized) consine similarity values

    relevantLinks = {}

    # initialize query weight
    queryWeight_sq = 0

    # for word in query
    for word in query:

        # find word in index and get data
        data = getWordData(word, index)
        # separate data
        docFreq = data[0]
        docList = data[1]

        # get tfidf weight for query term
        # sum the squares for normalization
        if docFreq > 0:
            queryWeight = log(TOTAL_DOCS/docFreq)

        else:
            queryWeight = 0

        # sum the squre of the query weights
        queryWeight_sq += queryWeight**2

        # if the word appears in some documents...
        if docList != 0:
            for doc in docList:

                # find tfidf and calculate the dot product with the query term
                tfIdf = get_TfIdf(doc, docList, docFreq)
                tfIdf_dotProd = tfIdf * queryWeight

                # add to previous weight total if document already exists in list
                if doc in relevantLinks:
                    relevantLinks[doc]['dotProd'] += tfIdf_dotProd
                    relevantLinks[doc]['length'] += tfIdf**2

                # if new document initialize
                else:
                    relevantLinks[doc] = {}
                    relevantLinks[doc]['dotProd'] = tfIdf_dotProd
                    relevantLinks[doc]['length'] = tfIdf**2

        else:
            continue

    # return relevantLinks
    # and sum of queryWeight_sq to normalize in the next step
    data = [relevantLinks, queryWeight_sq]

    return(data)

# display hyperlinks of ranked pages
def displayLinks(query, rankedLinks, searchTime):
    # precondition: the original query, the ranked links, and the total search time.
    # postcondition: nicely displayed form of all the inputs

    linkNum = 1
    print('<div style="text-align:center">Showing '+ str(len(rankedLinks)) +' results for "' + query + '"</div>')
    print('<div style="text-align:center;margin-bottom:10px">('+ str(searchTime) + ' s)' +'</div>')

    for link in rankedLinks:
        file = open(BASE_DIR + '/documents/' + str(link[0]), 'r').read()
        url = file.split('||')
        print('<div style="text-align:center;margin-bottom:5px">')
        #print(str(linkNum) + " (" + str(round(link[1],5)) + str(link[0]))
        print(str(linkNum) + ': <a href="'+ url[0] +'" target="_blank">'+ url[0] +'</a></div><br/>')
        linkNum += 1
    print ("</body></html>")

# search
def Search(query, index):
    # precondition: list of query words and the index
    # postcondition: links to view displayed on webpage
    i = time()

    # stem query to match indexed words
    stemmedQuery = stemQuery(query)
    
    # get relevant links and the magnitude of query weights for normalization
    data = getRelevantLinks(stemmedQuery, index)
    relevantLinks = data[0]
    queryWeight_sq = data[1]

    # get sorted ranked list from relevantLinks
    # remove cosine score from tuple
    rankedLinks = getRanks(relevantLinks, queryWeight_sq)
    rankedLinks = sorted(rankedLinks.items(), key = operator.itemgetter(1),reverse=True)

    f = time()
    searchTime = round(f-i,6)

    # if no results
    if len(rankedLinks) == 0:
            print('No results found!')
            print('<div style="text-align:center; margin-top:50px">')
            print('No results found for "' + query + '". Please try a new query.')
            print('</div></body></html>')

    else:
        displayLinks(query, rankedLinks, searchTime)

    return

# run program
def Run():
    # precondition: None
    # postcondition: beautiful search engine

    Start()

    index = readIndex(INDEX_FILE)
    form = cgi.FieldStorage()

    query = form.getvalue('searchQuery')
    #query = "Computer Science"
    if query:
        Search(query, index)

###################################
# Run
###################################

Run()