# -*- coding: utf-8 -*-

from stanford_corenlp_pywrapper import CoreNLP
import SocketServer

class MyTCPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print self.data
        if not isinstance(self.data, unicode):
            document = unicode(self.data, 'utf-8')
        jdoc = ss.parse_doc(document, raw = True)
        self.request.sendall(jdoc)

if __name__ == "__main__":
    HOST, PORT = "localhost", 9998
    ss = CoreNLP(configdict={'annotators':'tokenize, ssplit, pos, parse'}, corenlp_jars=["/home/t-bhpara/clickbait/corenlp/*"]) #Enter FULL path to folder containing extracted Stanford Core NLP
    print "model loaded"
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)
    server.serve_forever()
