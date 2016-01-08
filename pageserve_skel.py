"""
Socket programming in Python
  as an illustration of the basic mechanisms of a web server.

  Based largely on https://docs.python.org/3.4/howto/sockets.html
  This trivial implementation is not robust:  We have omitted decent
  error handling and many other things to keep the illustration as simple
  as possible. 

  This pageserver serves web pages (text files with names that end with .html) 
  and style sheets (text files that end with .css) from the directory in which the server 
  is run. It rejects URLs that contain '~' or '..' or '//', and therefore cannot be 
  used to read files outside of that directory.
  
  This file is the server and the web browser is the client. This server is run, and then
  is listening on a randomly chosen port, and then a URL is given through the web browser. 
  At that point, if the URL satisfies the above criteria then it will be fetched from the 
  current directory and served. Else, an error message will appear in the web browser. 
  
"""

import socket	 # Basic TCP/IP communication on the internet
import random	 # To pick a port at random, giving us some chance to pick a port not in use
import _thread	 # Response computation runs concurrently with main program 


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
	while True:
		print("Attempting to accept a connection on {}".format(sock))
		(clientsocket, address) = sock.accept()
		_thread.start_new_thread(func, (clientsocket,)) #call the function respond 


CAT = """
	 ^ ^
   =(	)=
   """


def respond(sock):
	"""
	Respond (only) to GET. If the requested URL is a ".html" or a ".css" AND it does not 
	contain "~" or ".." or "//" AND it is in the current directory, then it will be served.
	Else, an error message will appear in the browser. 
	Args:
	    sock: A server socket, already listening on some port.
	Returns: None
	Effects: If the requested URL is a ".html" or a ".css" AND it does not 
	contain "~" or ".." or "//" AND it is in the current directory, then it will be served.
	Else, an error message will appear in the browser. 
	"""
	sent = 0
	request = sock.recv(1024)  #this is the requested URL  
	request = str(request, encoding='utf-8', errors='strict') 
	print("\nRequest was {}\n".format(request))

	parts = request.split()
	if len(parts) > 1 and parts[0] == "GET":
		web_part = parts[1]
		if (".." in web_part) or ("//" in web_part) or ("~" in web_part):
		    transmit("HTTP/1.0 403 Forbidden\n\n", sock)
		    transmit("403 Forbidden\n\n", sock)
		elif web_part.endswith(".html") or web_part.endswith(".css"):
			try:
				file_url = web_part[1:]
				file = open(file_url, "r")
				#if here means file is in current directory
				list = []
				for line in file:
				    list.append(line)
				web_string = " ".join(list)
				transmit("HTTP/1.0 200 OK\n\n", sock) #telling web browser that the request was successful. must do this
				transmit(web_string, sock)
			except IOError:
			    #if here means file is not in current directory. 
				transmit("HTTP/1.0 404 Not Found\n\n", sock)
				transmit("404 Not Found\n\n", sock)
		else:
		    transmit("HTTP/1.0 403 Forbidden\n\n", sock)
		    transmit("403 Forbidden\n\n", sock)
			 
	
	else:
		transmit("HTTP/1.0 400 Bad Request\n\n", sock)
		transmit("400 Bad Request\n\n", sock)

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
    
