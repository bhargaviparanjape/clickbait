# SVM clickbait classifier
Code and Dataset used in the paper titled,
**[Stop Clickbait: Detecting and Preventing Clickbaits in Online News Media](http://cse.iitkgp.ac.in/~abhijnan/papers/chakraborty_clickbait_asonam16.pdf)**
at *2016 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM)*

If you are using this code or dataset for any research publication, or for preparing a technical report, you must cite the following paper as the source of the code and dataset.

Abhijnan Chakraborty, Bhargavi Paranjape, Sourya Kakarla, and Niloy Ganguly. "Stop Clickbait: Detecting and Preventing Clickbaits in Online News Media”. In Proceedings of the 2016 IEEE/ACM International Conference on Advances in Social Networks Analysis and Mining (ASONAM), San Fransisco, US, August 2016.

BibTex:

@inproceedings{chakraborty2016stop,   
  title={Stop Clickbait: Detecting and preventing clickbaits in online news media},   
  author={Chakraborty, Abhijnan and Paranjape, Bhargavi and Kakarla, Sourya and Ganguly, Niloy},   
  booktitle={Advances in Social Networks Analysis and Mining (ASONAM), 2016 IEEE/ACM International Conference on},    
  pages={9--16},    
  year={2016},   
  organization={IEEE}   
}

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
* dataset: This directory contains both clickbait and non-clickbait headlines used to train the classifier
* dependencies : Includes the corpus of hyperbolic words, common ngrams etc.
* vectors: Includes pretrained vectors used for classification
* experiment.py: code used to run certain experiments for the paper (can be ignored)
* stanford_server.py : Exposes Stanford CoreNLP as a service on localhost
* clickbait_classifier.py : The clickbait classifier
* utility.py : Helper functions
