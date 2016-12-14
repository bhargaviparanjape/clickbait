# SVM clickbait classifier
Code and Dataset used in the paper titled,
**[Stop Clickbait: Detecting and Preventing Clickbaits in Online News Media](www.facweb.iitkgp.ernet.in/~niloy/PAPER/P-ASONAM-2016_paper_64.pdf)**
at *2016 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining(ASONAM)*

### Requirements
1. JDK 1.7 or greater
2. Python modules
  * numpy
  * scipy
  * SocketServer
  * Scikit Learn
  * networkx

### Usage
* Download [Stanford CoreNLP suite](http://stanfordnlp.github.io/CoreNLP/) (ensure Java version compatibility) and extract
* Download python module [stanford_corenlp_pywrapper](https://github.com/brendano/stanford_corenlp_pywrapper)
* Install python module stanford_corenlp_pywrapper following instructions in thier README.md
* In file stanford_server.py, change path to the Stanford CoreNLP suite to where the suite was extracted
* Run Command : python stanford_server.py
* On a *separate Terminal*, run command: python server.py
* At the prompt, enter the title to be classified, or enter q/Q to exit

### Code
* clickbait_data: contains the headlines used to train the classifier
* dependencies : corpus of hyperbolic words, common ngrams etc.
* vectors: pretrained vectors used for classification
* experiment.py: has code used to run certain experiments for the paper (can be ignored)
* stanford_server.py : Exposes Stanford CoreNLP as a service on localhost
* server.py : classifier
* utility.py : helper functions
