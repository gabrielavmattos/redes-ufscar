#!/Python27/python
# -*- coding: utf-8 -*-
#################################################################################################################
# 	Nome: receptor.py									    		#									
# 	Objetivo:  Simular o comportamento do lado receptor com a utilização do go-back-n.			#
# 	Referencias:												#
# - http://www.diveintopython.net/scripts_and_streams/command_line_arguments.html				#
# - http://stackoverflow.com/questions/1767910/checksum-udp-calculation-python					#
#################################################################################################################
from socket import *
import sys
import random



#Definição da operação de checksum, com base no link especificado
def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)

def checksum(msg, opcao):
   	s = 0
	if len(msg) % 2 == 1:
            msg += "\0"
   	for i in range(0, len(msg), 2):
       		w = ord(msg[i]) + (ord(msg[i+1]) << 8)
       		s = carry_around_add(s, w)
   	if(opcao == 0):
   		return ~s & 0xffff
	else:
		return s & 0xffff
   
#Função para criação do pacote do ack, que recebe como parâmetro o número do ack, que é correspondente ao número de 
#sequência que foi recebido por último sem perda nem corrupção e na ordem. O pacote é simplesmente formado por um campo
#de checksum e um campo com o número do ack.
def makeAck(numAck):
	ack = str(numAck)
	checkSum = checksum(ack, 0)
	ack =  str(checkSum) + ";" + ack
	return ack

def mySendTo(numAck, ack, receptorSocket, nomeHost, numPort, probPerda, probCorrupcao):
	if(probPerda < 1):
		probPerda = probPerda * 10
	if(probCorrupcao < 1):
		probCorrupcao = probCorrupcao * 10
	#Para decidir se havera perda ou corrupcao
	x = random.randint(1,10)
	y = random.randint(1,10)

	if(x < probPerda):
		print "Perda do Ack " + str(numAck)
	elif (y < probCorrupcao):
		ack = "1234;90"
		receptorSocket.sendto(ack, (nomeHost, numPort))
	else:
		receptorSocket.sendto(ack, (nomeHost, numPort))

#Função principal, para tratamento dos pacotes recebidos
def main():
	
	#No nosso projeto, obrigatoriamente os argumentos devem seguir o seguinte padrão:
	#receptor <sender hostname> <sender-porta> <filename> Pl PC
	if (len(sys.argv) > 5):
		nomeHost = sys.argv[1]
		numPort = int(sys.argv[2])
		nomeArq = sys.argv[3]
		PL = float(sys.argv[4])
		if(PL > 0.4 or PL < 0.0):
			PL = 0.4
		PC = float(sys.argv[5])
		if(PC > 0.4 or PC < 0.0):
			PC = 0.4
		msgInicial = nomeArq
		#estabelecendo uma espécie de "conexão" antes de inicializar a transmissao dos dados, representada pela 
		#requisição do arquivo
		#criando um socket UDP
		receptorSocket = socket(AF_INET, SOCK_DGRAM)
		receptorSocket.sendto(msgInicial, (nomeHost, numPort))
		print "Requisitando arquivo " + msgInicial + " para o servidor " + nomeHost + " na porta " + str(numPort)
		#inicializando as variáveis que serão usadas para controle da comunicação
		#nroSeqEsperado representa o número de sequência que o receptor está esperando. Inicialmente, ele é 0, pois
		# é o primeiro número que se espera. A medida que forem sendo recebidos outros pacotes, com os números de 
		#sequência na ordem correta, o nroSeqEsperado é atualizado com o próximo valor de número de sequência que
		#se espera
		nroSeqEsperado = 0
		ultimoAck = -1
		arquivo = open('ArquivoRecebido.out', 'w')
		while 1:
			resMessage = receptorSocket.recvfrom(8192)[0]
			parts  = resMessage.split(";")

			#primeira verificacao para evitar problemas no acesso ao vetor
			#se nao for maior ou igual a 3, ja subentende-se que houve corrupcao no pacote, mais especificamente
			#no delimitador ;
			if(len(parts) >= 3):
				nroSeqRecebido = int(parts[1])
				#considerando que o checksum vem logo apos o numero de sequencia no cabecalho, no teste para verificacao ele sera desconsiderado
				verificacao = resMessage.split(";", 1)
				checkSum = int(verificacao[0])
				mensagemSemChecksum = verificacao[1]
				#realizando a soma dos dados do pacote, desconsiderando o campo de checksum
				somaDoPacote = checksum(mensagemSemChecksum, 1)

				#considerando o valor de checksum recebido no pacote, e a soma dos dados do pacote é feita a soma desses valores
				#essa soma deve resultar em FFFF, que equivale a 65535 em decimal
				soma = checkSum + somaDoPacote
				print "A soma do checksum é: " + str(soma)
			
				if(soma == 65535):
					print "Numero de sequencia recebido: " + str(nroSeqRecebido) + ". Esperava-se o numero de sequencia: " + str(nroSeqEsperado)
					#segundo nossa implementacao, quando o nro de seq for -1 (considerando um pacote nao corrompido)
					#existem duas possibilidades: ou essa eh a ultima parte do arquivo, ou o arquivo nao foi encontrado
					if(nroSeqRecebido == -1):
						if(parts[2] == 'Arquivo nao encontrado'):
							print "Arquivo nao encontrado"
						arquivo.close()
						break
						
					#se o número de sequência recebido é aquele que é esperado, então um ack é enviado confirmando o pacote recebido e o número esperado é incrementado
					if(nroSeqRecebido == nroSeqEsperado):
						arquivo.write(parts[2])
						#o ultimoAck enviado é atualizado com o último nro de sequência recebido. Essa atualização serve para os casos em que
						# der erro, e deve ser reenviado o último ack
						ultimoAck = nroSeqRecebido
						ack = makeAck(ultimoAck)
						print "Enviando Ack " + str(nroSeqRecebido)
						mySendTo(ultimoAck, ack, receptorSocket, nomeHost, numPort, PL, PC)
						#atualizando o próximo número de sequência esperado
						nroSeqEsperado = nroSeqEsperado + 1
					else:
						#Se não for o número de sequência esperado, esse pacote é descartado, pois deve ser recebido em ordem
						ack = makeAck(ultimoAck)
						#o ultimo ack confirmado é reenviado, para indicar o erro	
						print "Reenviando Ack " + str(ultimoAck)
						mySendTo(ultimoAck, ack, receptorSocket,nomeHost, numPort, PL, PC)
					
				else:	
					#Se a soma não está correta, corrupção foi detectada no pacote, e o ack deve ser reenviado para indicar erro
					print "Corrupcao detectada no pacote!"
					ack = makeAck(ultimoAck)
					print "Reenviando Ack " + str(ultimoAck)
					mySendTo(ultimoAck, ack, receptorSocket,nomeHost, numPort, PL, PC)

			else:
				print "Corrupcao detectada no pacote!"
				ack = makeAck(ultimoAck)
				print "Reenviando Ack " + str(ultimoAck)
				mySendTo(ultimoAck, ack, receptorSocket,nomeHost, numPort, PL, PC)	
		receptorSocket.close()	
	else:
		print "Espera-se os argumentos: hostname do rementente, numero de porta do rementente, nome do arquivo, probabilidade de perda (um numero entre 0.0 e 0.4, com uma casa decimal), e probabilidade de corrupcao (um numero entre 0.0 e 0.4, com uma casa decimal)"




main()
