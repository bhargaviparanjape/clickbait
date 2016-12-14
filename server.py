from sklearn import preprocessing,svm
from sklearn.pipeline import Pipeline
import nltk
import numpy
import subprocess
import time
import utility



###############Classifier############################
no_samples = 10000
positive = numpy.loadtxt("vectors/positive.csv",  delimiter=',')
negetive = numpy.loadtxt("vectors/negetive.csv", delimiter=',')
X = numpy.concatenate((positive, negetive), axis=0)
p = numpy.ones((no_samples, 1))
n = numpy.full((no_samples, 1), -1)
Y = numpy.concatenate((p,n), axis=0)
y = Y.ravel()
#scale
scaler = preprocessing.StandardScaler().fit(X)
#classifying
svm_module = svm.SVC()
classifier = Pipeline(steps= [('svm', svm_module)]) #[('scale', scaler), ('svm', svm_module)])
classifier.fit(X, y)
##############################################################

######################bhargavi part###########################
def isclickbait(document):
	try:
		title_vector = utility.create_vector(document)
		# t = scaler.transform(title_vector)
		prediction = classifier.predict(title_vector)
		if prediction[0] == 1:
			print "That's Clickbait!"
		else:
			print "That's not Clickbait!"
	except Exception,e:
		print "except:"
		print e



if __name__ == '__main__':
	input_text = "W"
	while input_text != "Q":
		input_text = input("Enter a clickbait title")
		isclickbait(input_text)
	print "Exited Succesfully"