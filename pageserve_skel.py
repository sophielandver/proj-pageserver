"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible. 

  FIXME:
  Currently this program always serves an ascii graphic of a cat.
  Change it to serve files if they end with .html and are in the current directory
"""

import socket	 # Basic TCP/IP communication on the internet
import random	 # To pick a port at random, giving us some chance to pick a port not in use
import _thread	 # Response computation runs concurrently with main program 


#fix listen function


def listen(portnum):
	"""
	Create and listen to a server socket.
	Args:
	   portnum: Integer in range 1024-65535; temporary use ports
		   should be in range 49152-65535.
	Returns:
	   A server socket, unless connection fails (e.g., because
	   the port is already in use).
	"""
	# Internet, streaming socket
	serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# Bind to port and make accessible from anywhere that has our IP address
	serversocket.bind(('', portnum))
	serversocket.listen(1)	  # A real server would have multiple listeners
	return serversocket

def serve(sock, func):
	"""
	Respond to connections on sock.
	Args:
	   sock:  A server socket, already listening on some port.
	   func:  a function that takes a client socket and does something with it
	Returns: nothing
	Effects:
		For each connection, func is called on a client socket connected
		to the connected client, running concurrently in its own thread.
	"""
	#when a request comes in it accepts the connection and it creates this socket. The address we just lose. the socket
	#is like a connection. a request comes in we create a connection and we pass the connection into the function 
	#we need to read in the text by using "request = sock.recv(1024)" which takes in the first charcters of the request 
	#so we arent always sending a cat
	#if someone asked for trivial.html then you would send them back to it 
	#where does the user ask for something 
	#user asks for something 
	#try to open the file using try/accept block. You try opening the file and if you succeeded then you send the contetnts of the file
	#if you didnt find it then it doesnt exits in current directory 
	#where do they ask for the URL. they give me a URL. and where will it be 
	while True:
		print("Attempting to accept a connection on {}".format(sock))
		(clientsocket, address) = sock.accept()
		_thread.start_new_thread(func, (clientsocket,)) #make window pop up with cat in it


CAT = """
	 ^ ^
   =(	)=
   """


def respond(sock):
	"""
	Respond (only) to GET

	"""
	sent = 0
	request = sock.recv(1024)  # We accept only short requests. This is where you get the request  
	request = str(request, encoding='utf-8', errors='strict')
	#THIS IS WHERE YOU FIX THINGS WITH THE request
	#you want to ask questions about request AND you dont always wanna transmit a cat but instead transmit 
	#whatever URL the request is 
	print("\nRequest was {}\n".format(request))

	parts = request.split()
	if len(parts) > 1 and parts[0] == "GET":
		web_part = parts[1]
		if (".." in web_part) or ("//" in web_part) or ("~" in web_part):
		    transmit("HTTP/1.0 403 Forbidden\n\n", sock)
		    transmit("403 Forbidden\n\n", sock)
		elif web_part.endswith(".html") or web_part.endswith(".css"):
		#try to open it in order to see if it is current directory
			try:
				file_url = web_part[1:]
				file = open(file_url, "r")
				list = []
				for line in file:
				    list.append(line)
				web_string = " ".join(list)
				#send content with the proper http type use transmit
				#http_url = "https://" + file_url
				#sock.send(http_url)
				transmit("HTTP/1.0 200 OK\n\n", sock)
				transmit(web_string, sock)
			except IOError:
				#send 404 not found using transmit 
				transmit("HTTP/1.0 404 Not Found\n\n", sock)
				transmit("404 Not Found\n\n", sock)
		else:
		    transmit("HTTP/1.0 403 Forbidden\n\n", sock)
		    transmit("403 Forbidden\n\n", sock)
			 
	
		#transmit(CAT, sock)
	else:
		transmit("HTTP/1.0 400 bad request\n\n", sock)
		transmit("400 bad request\n\n", sock)

	sock.close()

	return

def transmit(msg, sock):
	"""It might take several sends to get the whole buffer out"""
	sent = 0
	while sent < len(msg):
		buff = bytes( msg[sent: ], encoding="utf-8")
		sent += sock.send( buff )
	

def main():
	port = random.randint(5000,8000)
	sock = listen(port)
	print("Listening on port {}".format(port))
	print("Socket is {}".format(sock))
	serve(sock, respond)

main()
    
