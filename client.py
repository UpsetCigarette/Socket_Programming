"""
Client Side
"""
import argparse, socket, sys, threading

try:
    import SocketServer as socketserver
except:
    import socketserver

from threading import Thread

try:
    input_function = raw_input
except:
    input_function = input

global open_ports
open_ports = []

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        global open_ports
        open_ports.append(self.request)
        data = self.request.recv(1024)
        while len(data):
            for port in open_ports:
                try:
                    if port == self.request:
                        pass
                    else:
                        port.send(data)
                except socket.error as e:
                    open_ports.remove(port)
            data = self.request.recv(1024)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

# main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Send and receive TCP in a chat-like manner')
    parser.add_argument('-ip_address', help='ip address', default="127.0.0.1")
    parser.add_argument('-p', metavar='PORT', type=int, default=1060,
            help='TCP port (default 1060)')
    args = parser.parse_args()
    addr = args.ip_address
    port = args.p
    """
        We will set up a simple TCP server using much of what the Python library has to offer,
        and then we will run a simple client to connect communicate with that server.

        The IP address passed in will be the IP address that the client will connect to.
        It has been set to default to the local loopback address of 127.0.0.1 for testing purposes

        The port number will be both the port that the server will listen on,
        and the port that the client will try to connect to.
    """
    # set up threads for both the server and the client
    try:
        server = ThreadedTCPServer((addr, port), ThreadedTCPRequestHandler)
        # Start a thread with the server -- that thread will then start one
        # more thread for each request
        server_thread = threading.Thread(target=server.serve_forever)
        # Exit the server thread when the main thread terminates
        server_thread.setDaemon(True)
        server_thread.start()
        print( "Server loop running in thread:"+ server_thread.getName() )
    except:
        # assume it couldn't work because we want to try this script
        # as multiple clients connecting to the same server
        # in this case, the server will have already bound to the port
        # and we can't expect to reuse the port
        print("Server is already running on this port")
        # but we keep on running so that the client can still work

    # Now we have the client connect to the server
    global sock
    #@ now make the TCP socket and assign it to sock
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global prompt_string
    prompt_string = "What data would you like to send to the server? "
    global t
    t = input_function(prompt_string)
    #@ now have sock connect to (addr,port)
    sock.connect((addr, port))
    # now that we have the client connected, we make two threads, 
    #   one for sending and 
    #   one for receiving
    def send():
        global t
        global prompt_string
        global sock
        while (len(t) > 0):
            try:
                encoded_data = t.encode()
                #@ send the encoded on the socket sock
                sock.send(encoded_data)
                t = input_function(prompt_string)
            except:
                break
        #@ close sock
        sock.close()
    def receive():
        global sock
        while (True):
            try:
                response = sock.recv(1024)
                #@ receive from sock (at most 1024) and put it into response
                if len(response):
                    print("Received: %s" % response)
            except:
                break
    sending_thread = threading.Thread(target=send)
    receiving_thread = threading.Thread(target=receive)
    sending_thread.start()
    receiving_thread.start()
    print("client threads have been created")
    sending_thread.join()
    receiving_thread.join()


    try:
        server.shutdown()
    except:
        # we get an exception if we never managed to make the server to begin with
        pass

