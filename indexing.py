"""
Felipe de Oliveira
Assignment #5

Due Date: Oct 29, 2019

Problem 1 [40 points]. Write a (Perl) program that generates the inverted 
index of a set of already preprocessed files. The files are stored in a 
directory which is given as an input parameter to the program. Use the files
preprocessed in the previous assignment(s) as test data. Use raw term 
frequency (tf) in the document without normalizing it.

"""

import unicodedata
import os
import json
"""
You will have to install the next 3 dependencies using:
pip install PyPDF2
pip install textract
pip install nltk

"""
import PyPDF2 
import textract
import nltk
import string
from nltk.stem import WordNetLemmatizer

from nltk.corpus import stopwords 
from nltk.tokenize import word_tokenize

from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize


# Uncomment the next lines to install the needed dependencies
#nltk.download('punkt')
#nltk.download('stopwords')
#nltk.download('wordnet')


def preprocess(file, inverted, dic_inverted_with_df): 
	##open file
	text_from_file = ''
	words = []

	open_file1 = open(file, 'r', encoding="latin-1").read()

	text_url_keywords = open_file1.split('||')
	text_url = text_url_keywords[0]
	text_keyworkds = text_url_keywords[1]

	# Now we have a text variable which contains all the text derived #from our file.
	# Now, we will clean our text variable, and create a list of keywords.
	#The word_tokenize() function will break our text phrases into #individual words
	doc_index = inverted_index(text_keyworkds)
	inverted = inverted_index_add(inverted, file, doc_index)
	
	#return a list of words
	return inverted


def inverted_index(text):
	"""
	Create an Inverted-Index of the specified text document.
	{word:[locations]}
	"""
	inverted = {}
	document_words = text.split(" ")
	#document_words = word_split(text)
	
	for word in document_words:
		if word in inverted:
			inverted[word] += 1
		else:
			inverted[word] = 1

	return inverted

def inverted_index_add(inverted, doc_id, doc_index):
	"""
	Add Invertd-Index doc_index of the document doc_id to the 
	Multi-Document Inverted-Index (inverted), 
	using doc_id as document identifier.
        {word:{doc_id:[locations]}}
	"""
	for word, locations in doc_index.items():
		indices = inverted.setdefault(word, {})
		indices[doc_id] = locations
	return inverted


if __name__ == '__main__':

	#Variable used to keep track of all words in all documents
	inverted = {}

	#Variable used to keep track of Term frequency
	dict_file_tf = {}

	#List all the documents in the folder
	for filename in os.listdir(os.getcwd()):
		#It is a file that is generated randomly in the folder. No need to check
		if filename != '.DS_Store' and filename != 'assignment7_indexing.py' and filename != 'result.txt':
			preprocess(filename, inverted, dict_file_tf)	

	# Write Inverted-Index

	result_file = open("result.txt",mode="w")

	words_string = json.dumps(inverted) 
	result_file.write(words_string)	
	

