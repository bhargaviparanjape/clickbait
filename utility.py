# -*- coding: utf-8 -*-
import json
# from alchemyapi import AlchemyAPI
import nltk
import networkx as nx
import nltk.data
import re
from nltk.corpus import stopwords
import socket
from sklearn.externals import joblib
import numpy


HOST = '127.0.0.1'
PORT = 9998
# alchemyapi = AlchemyAPI()
stops = stopwords.words("english")
clf1 = joblib.load("dependencies/nb_small/nb_normal.pkl")
clf2 = joblib.load("dependencies/nb_small/nb_pos.pkl")
clf3 = joblib.load("dependencies/nb_small/nb_syn.pkl")
common_pos_grams = open("dependencies/pos_ngrams1", "r+").read().splitlines()
common_grams = open("dependencies/normal_ngrams1", "r+").read().splitlines()
common_sn_grams = open("dependencies/sn_ngrams1", "r+").read().splitlines()
common_words = open("dependencies/common", "r+").read().splitlines()



##################################
####	      HELPERS       ######
##################################

def convert_to_pattern(title):
	lct = title.lower()
	analysis = get_stanford_analysis(lct)
	tags = []
	words = []
	deps_cc = []
	for sen in analysis["sentences"]:
		tags += sen['pos']
		words += sen['tokens']
		deps_cc += sen["deps_cc"]
	norm = []
	i = 0
	while i < len(tags):
		if tags[i] == '``':
			while i < len(tags) and tags[i] != "''":
				i += 1
			if i < len(tags):
				norm.append("<QUOTE>")
			i += 1
		elif tags[i] == "CD":
			norm.append("<D>")
			i += 1
		elif words[i] in common_words: 
			norm.append(words[i])
			i += 1
		elif tags[i] in ['CC', 'CD', 'DT', 'EX', 'IN', 'LS', 'MD', 'PDT', 'POS', 'PRP', 'PRP$', 'SYM', 'TO', 'UH', 'WDT', 'WP', 'WP$', 'WRB']:
			norm.append(words[i])
		else:
			norm.append(tags[i])
			i += 1
	return ' '.join(norm)

def get_stanford_analysis(document):
	try:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.connect((HOST, PORT))
		if not isinstance(document, unicode):
			document = unicode(document, 'utf-8')
		sock.sendall(document + "\n")
		received = sock.recv(10000)
		return json.loads(received)
	finally:
		sock.close()

def normalize_title(tags, words):
	norm = []
	i = 0
	while i < len(tags):
		if tags[i] == '``':
			while i < len(tags) and tags[i] != "''":
				i += 1
			if i < len(tags):
				norm.append("<QUOTE>")
			i += 1
		elif tags[i] == "CD":
			norm.append("<D>")
			i += 1
		else:
			norm.append(words[i])
			i += 1
	return ' '.join(norm)

def syntactic_n_gram(dependency, n):
	G = nx.DiGraph()
	dict = {}
	i = 0
	for d in dependency:
		if d[0] == 'root':
			root = d[2]
		else:
			G.add_edge(d[1], d[2])
			dict[d[1], d[2]] = d[0]
	allpaths = []
	for node in G:
		allpaths.extend(findPaths(G,node,n))
	# print allpaths
	sngrams = []
	for path in allpaths:
		if n==1:
			sngrams.append([dict[(path[0], path[1])]])
		elif n==2:
			sngrams.append([dict[(path[0], path[1])] , dict[(path[1], path[2])]])
		else:
			sngrams.append([dict[(path[0], path[1])] , dict[(path[1], path[2])], dict[(path[2], path[3])]])
	return sngrams

def findPaths(G, u, n, excludeSet = None):
	if excludeSet == None:
		excludeSet = set([u])
	else:
		excludeSet.add(u)
	if n==0:
		return [[u]]
	paths = [[u]+path for neighbor in G.neighbors(u) if neighbor not in excludeSet for path in findPaths(G,neighbor,n-1,excludeSet)]
	excludeSet.remove(u)
	return paths

def longest_dependency(deps_cc):
	max = 0
	for dep in deps_cc:
		if dep[0] != 'root':
			diff = abs(dep[1] - dep[2])
			if max < diff:
				max = diff
	return max

def naive_bayes(analysis):	
	tags = []
	words = []
	deps_cc = []
	for sen in analysis["sentences"]:
		tags += sen['pos']
		words += sen['tokens']
		deps_cc += sen["deps_cc"]
	norm = normalize_title(tags, words)

	f1 = []	
	current = list(nltk.ngrams(norm.split(), 1)) + list(nltk.ngrams(norm.split(), 2)) + list(nltk.ngrams(norm.split(),3))
	ngram_list = [' '.join(list(g)) for g in current]
	for pos in common_grams:
		if pos in ngram_list:
			f1.append(1)
		else:
			f1.append(0)
	f1 = numpy.array(f1).reshape(1, len(f1))

	#pos ngrams
	f2 = []
	current_pos = list(nltk.ngrams(tags, 1)) + list(nltk.ngrams(tags, 2)) + list(nltk.ngrams(tags,3))
	ngram_list = [' '.join(list(g)) for g in current_pos]
	for pos in common_pos_grams:
		if pos in ngram_list:
			f2.append(1)
		else:
			f2.append(0)
	f2 = numpy.array(f2).reshape(1, len(f2))
	# print f2.shape


	# syntactic ngrams
	f3 = []
	current_sngrams = list(syntactic_n_gram(deps_cc, 1)) + list(syntactic_n_gram(deps_cc, 2)) + list(syntactic_n_gram(deps_cc, 3))
	ngram_list = [' '.join(list(g)) for g in current_sngrams]
	for pos in common_sn_grams:
		if pos in ngram_list:
			f3.append(1)
		else:
			f3.append(0)
	f3 = numpy.array(f3).reshape(1, len(f3))

	return [clf1.predict(f1)[0], clf2.predict(f2)[0], clf3.predict(f3)[0]]

def create_vector(title):
	#clean title
	# title = unidecode.unidecode(title.encode('utf-8'))
	lct = title.lower()
	# response = alchemyapi.entities('text', lct, {'sentiment': 1, 'disambiguate' : 1})
	# if response['status'] == 'OK':
	# 	for entity in response['entities']:
	# 		if entity['type'] in ['Country', 'Holiday', 'Movie', 'MusicGroup', 'Organization', 'Person', 'PrintMedia', 'Region', 'StateOrCountry', 'TelevisionShow', 'TelevisionStation', 'Money', 'Company', 'GeographicFeature']:
	# 			if title.find(entity['text'].upper()) >= 0:
	# 				lct = lct.replace(entity['text'], entity['text'].upper())
	# 			else:
	# 				lct = lct.replace(entity['text'], entity['text'].title())
	analysis = get_stanford_analysis(lct)
	tags = []
	words = []
	deps_cc = []
	for sen in analysis["sentences"]:
		tags += sen['pos']
		words += sen['tokens']
		deps_cc += sen["deps_cc"]
	for i in range(0, len(words)):
		if not isinstance(words[i], unicode):
				words[i] = unicode(words[i], 'utf-8')
	#title starts with number
	f1 = 0
	if(tags[0] == 'CD'):
		f1 = 1

	#length of title
	f2 = len(title.split())

	#average length of each word
	f3 = float(len(title))/ float(f2)

	#number of hyperbolic terms/common phrases
	hyperbolics = open("dependencies/hyperbolic").read().splitlines()
	f4 = len([word for word in words if word in hyperbolics])

	#number of common words
	norm = normalize_title(tags, words)
  	common_phrases = open("dependencies/common_phrases").read().splitlines()
  	f5 = len([p for p in common_phrases if p.decode('utf-8') in norm])

	#subject of title
	common_subjects = ['dog', 'everyone', 'girl', 'girls', 'guy', 'guys', 'he', 'here', 'i', 'it', 'kid', 'kids', 'man', 'men', 'mom', 'one', 'parent', 'people', 'photos', 'reasons', 'she', 'signs', 'something', 'that', 'they', 'thing', 'things', 'this', 'thoughts', 'times', 'video', 'ways', 'we', 'what', 'who', 'woman', 'women', 'you']
	subs = set([words[dep[2]] for dep in deps_cc if dep[0] == 'nsubj'])
	f6 = len([s for s in subs if s.lower() in common_subjects])

	#presence of word contractions
	contractions = open("dependencies/contractions").read().splitlines()
	f7 = len([c for c in lct.split() if c in contractions])

	# presence of determiners and pronouns
	determiners = ['i', 'you', 'he', 'she', 'it', 'they', 'we', 'me', 'you', 'him', 'her', 'it', 'us', 'them', 'every', 'that', 'his', 'these', 'its', 'this', 'those', 'our', 'mine', 'ours', 'what', 'which', 'whose', 'your', 'his']
	f8 = len([c for c in lct.split() if c in determiners])

	#presence of punctuations
	f9 = 0
	regex = re.compile('[?]|["]|[!]|[.]+|[*]')
	if regex.search(lct):
		f9 = 1

	#ratio of stops to other words in the description
	f10 = float(len([s for s in lct.split() if s in stops]))/float(len(lct.split()))

	f11 = longest_dependency(deps_cc)

	#normal_ngrams bayes
	nb_features = naive_bayes(analysis)

	return ([f1, f2, f3, f4, f5, f6, f7, f8, f9, f10, f11] + nb_features)
