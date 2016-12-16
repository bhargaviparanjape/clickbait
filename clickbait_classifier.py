from sklearn import preprocessing,svm
from sklearn.pipeline import Pipeline
import nltk
import numpy
import subprocess
import time
import utility

###############  Classifier  ############################
print "creating classifier..."
no_samples = 10000
positive = numpy.loadtxt("vectors/positive.csv",  delimiter=',')
negetive = numpy.loadtxt("vectors/negative.csv", delimiter=',')
X = numpy.concatenate((positive, negetive), axis=0)
p = numpy.ones((no_samples, 1))
n = numpy.full((no_samples, 1), -1, dtype=numpy.int64)
Y = numpy.concatenate((p,n), axis=0)
y = Y.ravel()
#scale
scaler = preprocessing.StandardScaler().fit(X)
#classifying
svm_module = svm.SVC()
classifier = Pipeline(steps= [('svm', svm_module)]) #[('scale', scaler), ('svm', svm_module)])
classifier.fit(X, y)
print "Classifer created"
##############################################################

##################### Clickbait Classifier Service ###########################
def isclickbait(document):
	try:
		title_vector = numpy.array(utility.create_vector(document)).reshape(1,-1)
		# t = scaler.transform(title_vector)
		prediction = classifier.predict(title_vector)
		if prediction[0] == 1:
			print "The headline is a Clickbait!"
		else:
			print "The headline is not a Clickbait!"
	except Exception,e:
		print "except:", e

if __name__ == '__main__':
	input_text = "W"
	while input_text != "Q":
		input_text = raw_input("Enter a news headline or 'Q/q' to exit: ")
		if input_text == "Q" or input_text == 'q':
			break
		isclickbait(input_text)
	print "Exited Succesfully"
