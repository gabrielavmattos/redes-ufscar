# -*- coding: utf-8 -*-
# Referencias: http://www.cs.sfu.ca/CourseCentral/371/oba2/Sep19.pdf
#http://www.binarytides.com/programming-udp-sockets-in-python/
from socket import *
import sys
import math
import numpy


# A mensagem será dividida no tamanho da janela e salva em um vetor de string, o indice do vetor vai representar

def dividirMensagem(tamanhoPacote, mensagem):

	pacotes = []
	tamanho = int(math.ceil(len(mensagem) / (tamanhoPacote * 1.0)))

	for i in range (0, tamanho):
		inicio = i * tamanhoPacote
		fim = inicio + tamanhoPacote
		pacotes.append(mensagem[inicio:fim])

	return pacotes

def main():
	tamanhoJanela = 2
	numSeqMax = tamanhoJanela - 1
	tamanhoPacote = 5
	ack = 0

	if(len(sys.argv)>1):
		numPort = int(sys.argv[1])
		print numPort
		servidorSocket = socket(AF_INET, SOCK_DGRAM)
		servidorSocket.bind(('', numPort))
	
		while 1:
			print "O servidor está pronto para receber."

	
			mensagem, enderecoReceptor = servidorSocket.recvfrom(2048)
		
			if (len(mensagem) != 0):
				
				numSeqBase = 0
				numSeq = 0
				ultimoAck = 0
				pacotes = dividirMensagem(tamanhoPacote, mensagem)
				numSeqMax = tamanhoJanela - 1

				#pacote é transmitido em ordem
				for i in range (0, len(pacotes)):
		
					if (numSeq <= numSeqMax):
					
						res = str(numSeq) + ";" + pacotes[i] + ";"
						# [melhorar depois] mensagem avisando que foi enviado o pacote
						print "Enviando pacote de dados com cabecalho: " + res + "/" + str(len(pacotes))				    
				        	servidorSocket.sendto(res, enderecoReceptor)

						numSeq += 1
					#quando atinge o tamanho da janela ele deve reenviar os pacotes
					else:
						print "Tamanho da janela atingido " + str(i)
						i = ack + 1
						numSeq = i
	
					mensagem = servidorSocket.recvfrom(2048)[0]

					if (len(mensagem) != 0):
						parts  = mensagem.split(";")
						ack = int(parts[0])
						print ack
						print numSeq
						#tratar o ack aqui
						if (ack > numSeqBase):
							numSeqMax = numSeqMax + (ack+1 - numSeqBase)
							numSeqBase = ack
							ultimoAck = ack
						#duvida: aqui é um tempo ou posso verificar o ultimo?
						#elif (ack == ultimoAck): #é nesse momento que vamos saber se houve perca, pq o mesmo ack tá sendo enviado mais de uma vez
						
		else:
			print "Espera-se o seguinte parametro: numero de porta do serviço"

main()