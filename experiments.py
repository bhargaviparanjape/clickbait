import codecs
import re
import imp
from alchemyapi import AlchemyAPI
import json
import xml.sax
import nltk
import ast
from nltk.corpus import stopwords
from collections import Counter
import nltk.data
from nltk.tokenize import word_tokenize
import math


stops = stopwords.words("english")
sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')

############################################
#   Add Full Stops if not?,!,',"           #
############################################
def add_full_stops_to_the_end(infile, outfile):
	#clean data of small titles nad add full stops for NLTK to work
	output_format = '{}.\n'.format
	with open(infile) as fin, codecs.open(outfile, 'w+', 'utf-8') as fout:
		for line in fin:
			if line[0] == ' ':
				pass
			#ignore headlines with less than three words
			elif len(line.split()) <= 3:
				pass
			elif line.endswith('.\n') or line.endswith('!\n') or line.endswith('?\n') or line.endswith('!\n') or line.endswith('\'\n') or line.endswith('"\n'):
				print >> fout, line.decode('utf-8'),
			else:
				print >> fout, output_format(line.strip()).decode('utf-8'),



############################################
#   Convert All except first word and quotes
# 	to lower case 				           #
############################################
def convert_to_lower_case(infile, outfile):
	f = open(infile)
	f2 = codecs.open(outfile, "w+", "utf-8")
	for l in f:
		#In quotes text are Ok
		if len(re.findall('\"(.+?)\"', l)):
			start = l.find('"') + 1
			end = l.find('"', start)
			temp = len(l.split(' ', 1)[0]) + 1
			if start == 1:
				k = '"' + l[start:end].decode('utf-8') + l[end:].decode('utf-8').lower()
			else:
				k = l.split(' ', 1)[0].decode('utf-8') + " " + (l.split(' ', 1)[1]).decode('utf-8')[:start-temp].lower() + l[start:end].decode('utf-8') + l[end:].decode('utf-8').lower()
			print >> f2, k,
		else:
			print >> f2, l.split(' ', 1)[0].decode('utf-8') + " " +  l.split(' ', 1)[1].decode('utf-8').lower(),


############################################
#	Perform entity recognition to re-cap 
# 	proper nouns for better POS tagging
############################################
def convert_to_clean_titles(infile, outfile):
	alchemyapi = AlchemyAPI()
	f = open(infile, "r")
	f2 = codecs.open(outfile, "w+", "utf-8")
	f3 = codecs.open("Entities.txt", "w+", "utf-8")
	count = 1
	for line in f:
		line = line.decode("utf-8")
		response = alchemyapi.entities('text', line, {'sentiment': 1, 'disambiguate' : 1})
		if response['status'] == 'OK':
			for entity in response['entities']:
				if "type" in entity.keys:
					if entity['type'] in ['Country', 'Holiday', 'Movie', 'MusicGroup', 'Organization', 'Person', 'PrintMedia', 'Region', 'StateOrCountry', 'TelevisionShow', 'TelevisionStation', 'Money', 'Company', 'GeographicFeature']:
						line = line.replace(entity['text'], entity['text'].title())
					print >> f3, entity['text'], entity['type'], entity['sentiment']
			print >> f2, line,
		else:
			print >> f2, line,
		print count, line
		count += 1

def handle_indian_actors(infile, outfile):
	f = open(infile, "r")
	f2 = codecs.open(outfile, "w+", "utf-8")
	f3 = open("actors_final.txt", "r")
	actors = f3.readline().split(',')
	for line in f:
		line = line.decode("utf-8")
		words = line.split()
		for w in words:
			if w.title() in actors:
				line = line.replace(w, w.title())
		print >> f2, line, 

def handle_multiple_sentences(infile, outfile):
	titles = []
	f = open(infile, "r")
	f2 = codecs.open(outfile, "w+", "utf-8")
	for line in f:
		line = line.decode("utf-8")
		sentences = sent_detector.tokenize(line.strip())
		for i in range(len(sentences)):
			if i == 0:
				sentences[i] = sentences[i].replace(sentences[i].split()[0],sentences[i].split()[0].title())
			else:
				sentences[i] = sentences[i].replace(sentences[i].split()[0],sentences[i].split()[0].title())
				sentences[i-1] = sentences[i-1].replace(sentences[i-1].split()[-1][-1], " ::::")

	 	titles.append(" ".join(sentences))
	title_set = set(titles)
	for l in title_set:
		print >> f2, l

def normalise_numbers_quotes(infile, outfile):
	pass
	#done in file

class HeadlineContentHandler(xml.sax.ContentHandler):
	def __init__(self, outfile):
		xml.sax.ContentHandler.__init__(self)
		self.outfile = outfile
		self.currentData = ""
		self.parse = ""
		self.trip = 0
		self.type = ""
		self._charBuffer = []
		self.dict = {}
		self.dict_token = {}
		self.depidx = -1
		self.govidx = -1
		self.governor = ()
		self.dependent = ()

	def _flushCharBuffer(self):
		s = ''.join(self._charBuffer)
		self._charBuffer = []
		return s


	def startElement(self, tag, attrs):
		self.currentData = tag
		if tag == "sentence":
			self.dict["tokens"] = []
			self.dict["id"] = int(attrs.getValue("id"))
			self.basic = []
			self.cc_processed = []
			self.collapsed = []
		elif tag == "token":
			print attrs.getValue("id")
			self.dict_token["id"] = int(attrs.getValue("id"))
		elif tag == "dependencies" and attrs.getValue("type") ==  "basic-dependencies":
			self.trip = 1
		elif tag == "dependencies" and attrs.getValue("type") ==  "collapsed-dependencies":
			self.trip = 2
		elif tag == "dependencies" and attrs.getValue("type") ==  "collapsed-ccprocessed-dependencies":
			self.trip = 3
		elif tag == "dep":
			self.type = attrs.getValue("type")
		elif tag == "dependent":
			self.depidx = attrs.getValue("idx")
		elif tag == "governor":
			self.govidx = attrs.getValue("idx")


	def endElement(self, tag):
		if tag == "sentence":
			self.dict["basic-dependencies"] = self.basic
			self.dict["collapsed-dependencies"] = self.collapsed
			self.dict["collapsed-ccprocessed-dependencies"] = self.cc_processed
			print >> self.outfile, self.dict
			self.dict = {}
		elif tag == "token":
			self.dict["tokens"].append(self.dict_token)
			self.dict_token = {}
			self.dict["subject"] = []
		elif tag == "parse":
			self.dict["parse"] = self._flushCharBuffer().strip()
		elif tag == "word":
			self.dict_token["word"] = self._flushCharBuffer().strip()
		elif tag == "lemma":
			self.dict_token["lemma"] = self._flushCharBuffer().strip()
		elif tag == "POS":
			self.dict_token["pos"] = self._flushCharBuffer().strip()
		elif tag == "NER":
			self.dict_token["ser"] = self._flushCharBuffer().strip()
		elif tag == "sentiment":
			self.dict_token["sentiment"] = self._flushCharBuffer().strip()
		elif tag == "governor":
			self.governor = (self.govidx, self._flushCharBuffer().strip())
		elif tag == "dependent":
			self.dependent = (self.depidx, self._flushCharBuffer().strip())
		elif tag == "dep":
			#create type and gov, dep tuple list
			list = [self.type, self.governor, self.dependent]
			if self.trip == 1:
				self.basic.append(list)
			elif self.trip == 2:
				self.collapsed.append(list)
			elif self.trip == 3:
				self.cc_processed.append(list)

	def characters(self, content):
		if self.currentData == "parse":
			self._charBuffer.append(content)
		elif self.currentData == "word":
			self._charBuffer.append(content)
		elif self.currentData == "lemma":
			self._charBuffer.append(content)
		elif self.currentData == "POS":
			self._charBuffer.append(content)
		elif self.currentData == "NER":
			self._charBuffer.append(content)
		elif self.currentData == "sentiment":
			self._charBuffer.append(content)
		elif self.currentData == "dependent":
			self._charBuffer.append(content)
		elif self.currentData == "governor":
			self._charBuffer.append(content)



def stanford_nlp_processor(infile, outfile):
	f2 = codecs.open(outfile, "a+", "utf-8")
	parser = xml.sax.make_parser()
	parser.setFeature(xml.sax.handler.feature_namespaces, 0)
	Handler = HeadlineContentHandler(f2)
	parser.setContentHandler(Handler)
	parser.parse(infile)

def join_multiple_sentences(infile, outfile):
	f = open(infile, "r")
	f2 = codecs.open(outfile, "w+", "utf-8")
	lines = f.readlines()
	i = 0
	while i < len(lines):
		d = dict()
		pos = []
		sen = []
		sentence = ast.literal_eval(lines[i])
		if (i < len(lines)-1 ):
			next_sentence = ast.literal_eval(lines[i+1])
		words_ = next_sentence["tokens"]
		if words_[0]['pos'] == ':':
			#combine the dictionaries of sentence and next_sentence
			d['tokens'] = sentence['tokens'] + next_sentence['tokens']
			d['subject'] = sentence['subject'] + next_sentence['subject']
			d['parse'] = sentence['parse'] + next_sentence['parse']
			d["basic-dependencies"] = sentence['basic-dependencies'] + next_sentence['basic-dependencies']
			d["collapsed-dependencies"] = sentence['collapsed-dependencies'] + next_sentence['collapsed-dependencies']
			d["collapsed-ccprocessed-dependencies"] = sentence['collapsed-ccprocessed-dependencies'] + next_sentence['collapsed-ccprocessed-dependencies']
			print >> f2, d
			i += 1
		else:
			#print the dictionaries as it is
			print >> f2, sentence
		i += 1



def n_gram_analysis_simple(infile, gram, stop):
	ngram = dict()
	f = open(infile, "r" )
	#f2 = codecs.open(outfile, "w+", "utf-8")
	for l in f:
	    x = nltk.ngrams(l.split(),gram)
	    for w in x:
	    	# if stop:
	    	# 	if w not in stops:
			   #      if w in ngram:
			   #          ngram[w]+=1
			   #      else:
			   #      	ngram[w]=1
			if w in ngram:
				ngram[w] += 1
			else:
				ngram[w] = 1
	p = list(ngram.items())
	p.sort(key = lambda x: -x[1])
	print len(p)
	for x in p[:10]:
		sen = ' '.join(x[0])
		cnt = int(x[1])
		if cnt == 0:
			cnt = 1
		print sen, cnt


def create_tag_sentence_dictionary(infile, outfile):
	tagged_data = open(infile, "r+")
	f2 = codecs.open(outfile, "a+", "utf-8")
	for line in tagged_data:
		sentence = ast.literal_eval(line)
		d = dict()
		pos = []
		sen= []
		for word in sentence["tokens"]:
			pos.append(word['pos'])
		for word in sentence["tokens"]:
			sen.append(word['word'])
		if len(sen) >= 4:
			d['sentence'] = " ".join(sen)
			d['pos_sentence'] = " ".join(pos)
			print >> f2, d

def pos_with_common_words(infile, outfile):
	f = open("common.txt", "r")
	f1 = open(infile, "r+")
	f2 = codecs.open(outfile, "w+", "utf-8")
	common_words = set(f.readline().split())
	for line in f1:
		sentence = ast.literal_eval(line)
		for word in sentence["tokens"]:
			#list of common words needs to be filtered for better clustering results
			if word['word'].lower() in common_words:
				print >> f2, word['word'], 
			elif word['pos'] == 'CD':
				print >> f2, "<D>",
			else:
				print >>f2, word['pos'],
		print >> f2,'\n'



def obtain_hyperbolic_terms(infile, outfile):
	tagged_data = open( infile, "r+")
	f2 = codecs.open(outfile, "a+" ,"utf-8")
	words = []
	for line in tagged_data:
		sentence = ast.literal_eval(line)
		for word in sentence["tokens"]:
			#list of common words needs to be filtered for better clustering results
			try:
				if word['sentiment'] == u'Very negetive': # Positive and word['pos'] in ['JJ', 'JJS', 'JJR', 'RB', 'RBS', 'RBR']:
					words.append(word['word'])
			except:
				pass
	print "Very Positive Words\n"
	print >> f2, set(words)
	print "\n\n"


def pos_with_entity_replaced_common_words(infile, outfile):
	alchemyapi = AlchemyAPI()
	common_word_pos = open("common_word_pos.txt", "r")
	title_data = open(infile, "r+")
	f2 = codecs.open(outfile, "w+", "utf-8")
	for line1, line2 in title_data, common_word_pos:
		response = alchemyapi.entities('text', line1, {'sentiment': 1, 'disambiguate' : 1})
		if response['status'] == 'OK':
			for entity in response['entities']:
				line2.replace(entity['text'], entity['type'])
			print >> f2, line2,

def subjects(infile, outfile):
	f1 = open(infile, "r+")
	f2 = codecs.open(outfile, "w+", "utf-8")
	subjects = dict()
	for l in f1:
		sentence = ast.literal_eval(l)
		dependency = sentence['collapsed-ccprocessed-dependencies']
		for d in dependency:
			if d[0] == 'nsubj':
				sub = d[2][1]
				if sub in subjects:
					subjects[sub] += 1
				else:
					subjects[sub] = 1
	p = list(subjects.items())
	p.sort(key = lambda x: -x[1])
	for x in p[:50]:
	    print >> f2, x



def dependency_bigram_analysis(infile, outfile):
	f1 = open(infile, "r+")
	f2 = codecs.open(outfile, "w+", "utf-8")
	# f3 = open()
	relation = dict()
	example = dict()
	example_sentence = dict()
	cnt = 0
	for l in f1:
		sentence = ast.literal_eval(l)
		words = sentence['tokens']
		s = ' '.join([w['word'] for w in words])
		pos_dict = dict()
		for w in words:
			pos_dict[w['id']] = w['pos']
		dependency = sentence['basic-dependencies']
		for d in dependency:
			dep_dict = dict()
			if math.fabs(int(d[1][0]) - int(d[2][0])) >= 3:
				r = dep_dict['relation'] = d[0]
				if r in relation:
					relation[r] += 1
				else:
					relation[r] = 1
					example[r] = [d[1][1], d[2][1]]
					example_sentence[r] = s
				cnt += 1
	print cnt
	p = list(relation.items())
	p.sort(key = lambda x: -x[1])
	for x in p:
	    print >> f2, x, example[x[0]], example_sentence[x[0]]

def average_length_sentences(infile):
	f1 = open(infile, "r+")
	# f2 = codecs.open(outfile, "w+", "utf-8")
	cnt = 0
	lines = f1.readlines()
	for line in lines:
		cnt += len(word_tokenize(line.decode("utf-8")))
	avg = float(cnt/len(lines))
	print cnt, len(lines), avg




def create_histrogram_given_dictionary(d, wonky, title):
	fig = plt.figure() 
	if wonky:
		d_ = dict()
		for key , value in d.iteritems():
			d_[key[0]] = value
		f = {x:70*i for i,x in enumerate(set(d_.keys()))}
		new_d = dict()
		for key, value in d_.iteritems():
			new_d[f[key]] = value
	else:
		f = {x:70*i for i,x in enumerate(set(d.keys()))}
		new_d = dict()
		for key, value in d.iteritems():
			new_d[f[key]] = value
	c = list(new_d.items())
	X,Y = zip(*c)
	plt.barh(X,Y,align='center')
	c = list(f.items())
	ticks,pos = zip(*c)
	pylab.yticks(pos,ticks)
	matplotlib.rc('ytick', labelsize=8)
	fig.suptitle(title)
	plt.show()

def analyse_clickbait():
	#preprocessing
	# add_full_stops_to_the_end("titles.txt", "full_stop_titles.txt")	
	# convert_to_lower_case("full_stop_titles.txt", "lower_case_titles.txt")
	# convert_to_clean_titles("lower_case_titles.txt", "clickbaittitles.txt")
	# handle_indian_actors("clickbaittitles.txt", "clickbaittitles_indian.txt")
	# handle_multiple_sentences("clickbaittitles_indian.txt", "final_clickbait.txt")
	# stanford_nlp_processor("processing/cb7.txt.xml", "cb.out")
	# join_multiple_sentences("cb.out", "cb_final.out")
	# create_tag_sentence_dictionary("cb_final.out", "tag_word_dictionary.txt")
	# pos_with_common_words("/home/bhargavi/Desktop/BTP/news/news.out", "/home/bhargavi/Desktop/BTP/click_bait/classifiers/normalised_titles_.txt")
	# n_gram_analysis_simple("final_clickbait.txt", 4 , 0)
	# subjects("cb.out", "subjects.txt")
	# obtain_hyperbolic_terms("cb.out", "hyperbolic.txt")
	average_length_sentences("/home/bhargavi/Desktop/BTP/news/final_news.txt")
	# dependency_bigram_analysis("/home/bhargavi/Desktop/BTP/news/news.out", "/home/bhargavi/Desktop/BTP/news/dependency_news.txt")

if __name__ == '__main__':
	analyse_clickbait()