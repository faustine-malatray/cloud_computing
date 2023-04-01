'''
server.py

Implementation of the chat room server application.
'''

import socket
import threading
import utils
import argparse

# We keep track of the client connections.
connections = {}
# Used to assign an internal identifier to the client.
total_connections = 0


class Client(threading.Thread):
    '''
        This class collects all the information on a connected client.
        For each client, the server starts a new thread that is dedicated to serve
        that client. For each client we keep:

        - The socket used by the server.
        - The IP address of the client.
        - The internal identifier used by the server to identify a client.
        - A boolean flag (signal) that is set to False when the client disconnects.
    '''

    def __init__(self, socket, address, id, signal):
        '''
        Constructor of the class. Initialization of the attributes.
        '''

        threading.Thread.__init__(self)
        self.socket = socket
        self.address = address
        self.id = id
        self.signal = signal
        self.username = None

    def __str__(self):
        '''
        Textual representation some of the client information.
        '''
        return str(self.id) + " " + str(self.address)

    def run(self):
        '''
        This function is executed when this thread is started.
        '''
        while self.signal:
            # Waits for a message from a client.
            message = utils.recv_msg(self.socket)
            if message:
                # Responds to the hello message
                if message["type"] == "HELLO":
                    self.username = message["name"]
                    print(f"Received HELLO from {self.username}")
                    # Send hello to the new user
                    welcome_message = utils.\
                        prepare_welcome_message(
                            f"Welcome {self.username}! You can now start to chat!")
                    utils.send_msg(welcome_message, self.socket)
                    # Tell him who's connected
                    connected_users_msg = \
                        utils.prepare_chat_message("CONNECTED USERS: {}".format(
                            ", ".join([x.username for x in connections.values()])))
                    utils.send_msg(connected_users_msg, self.socket)
                    # Tell the others that the user went online.
                    online_msg = utils.prepare_chat_message(
                        f"SERVER: {self.username} is now online")
                    for client_id, client in connections.items():
                        if client_id != self.id:
                            utils.send_msg(online_msg, client.socket)
                # Handles a chat message received from a client.
                elif message["type"] == "CHAT":
                    print(f"{self.username} wrote {message['content']}")
                    ''' 
                        A message of type MESSAGE contains something to send to all the other clients.
                        The server prefixes the message with the name of the user who sent the message.
                    '''
                    msg = utils.prepare_chat_message(
                        self.username + ": " + message["content"])
                    for client_id, client in connections.items():
                        if client_id != self.id:
                            utils.send_msg(msg, client.socket)
                elif message["type"] == "QUIT":
                    print(f"{self.username} wants to quit")
                    # A client asks to disconnect. We kiss the user goodbye and
                    # notify the other clients.
                    bye_message = utils.prepare_bye_message(
                        f"You now left the chat. See you soon {self.username}!")
                    utils.send_msg(bye_message, self.socket)
                    self.handle_disconnection()
            else:  # Handles the disconnection of a client.
                print("Client " + str(self.username) + " has disconnected")
                self.handle_disconnection()
                break

    def handle_disconnection(self):
        '''
        Handles the disconnection of a client.
        '''
        self.signal = False
        del connections[self.id]
        # Inform all the other client that the current client is disconnected from the chat.
        for client_id, client in connections.items():
            if client_id != self.id:
                msg = utils.prepare_chat_message(
                    f"SERVER: {self.username} left the chat")
                utils.send_msg(msg, client.socket)


def newConnections(socket):
    '''
    Wait for new connections.

    Parameters
    ----------
    - socket : The server socket
    '''

    while True:
        # Accept a new incoming connection from a client.
        # sock = client socket; address = IP address of the client.
        sock, address = socket.accept()
        global total_connections
        new_client_id = total_connections
        total_connections += 1
        connections[new_client_id] = Client(sock, address, new_client_id, True)
        connections[new_client_id].start()
        print("New connection at ID " + str(connections[new_client_id]))


'''
Entry point. Instructions executed when the server is executed.
'''


if __name__ == '__main__':

    # Get the host name of the server.
    host = socket.gethostbyname(socket.gethostname())
    # The port number must be specified when executing the server.
    parser = argparse.ArgumentParser()
    parser.add_argument("server_port", help="port number of the server",
                        type=int)
    args = parser.parse_args()
    port = args.server_port

    # Create new server socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((host, port))
    sock.listen(5)

    print(f"The server is listening at {host}, port {port}")

    # Create new thread to wait for connections.
    newConnectionsThread = threading.Thread(
        target=newConnections, args=(sock,))
    newConnectionsThread.start()
