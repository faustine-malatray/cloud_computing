'''
client.py

Implementation of the chat room client application.
'''

import argparse
import socket
import threading
import sys
import utils

def send(socket, signal):
    '''
    Function that the client uses to send a message out.

    Parameters
    ----------
    socket : The socket used by the client.
    signal : Initially set to true. It'll be set to False to stop 
    the execution of the sending loop.

    '''
    while signal:
        # Get the message typed by the user from the standard input (keyboard)
        next_message = input(">> ")
        # If the message if #quit, then stop the sending loop (the user wants to leave the chat room).
        if next_message == "#quit":
            # Prepares and sends the quit message.
            msg = utils.prepare_quit_message()
            utils.send_msg(msg, socket)
            # Stop the sending loop.
            signal = False
        else:   
            # The user wants to send a message in the chat room. 
            msg = utils.prepare_chat_message(next_message)
            utils.send_msg(msg, socket)

def receive(socket, signal):

    '''
    Function that the client uses to receive messages, either from the server or 
    another client through the server.

    Parameters
    ----------

    socket : The socket used by the client.
    signal : Initially set to true. It'll be set to False to stop 
    the execution of the receive loop.
    '''
    while signal:
        # Get a message.
        message = utils.recv_msg(socket)
        # If the message has some content.
        if message:
            # Welcome message received from the server.
            if message["type"] == "WELCOME":
                print(message["content"])
                # Starts a new thread, that starts the sending loop.
                # The new thread waits for a message from the user and 
                # sends it to the server.
                sendThread = threading.Thread(target = send, args = (socket, True))
                sendThread.start()
            # A new message is received in the chat.       
            elif message["type"] == "CHAT":
                # Prints the message ....
                print(message["content"])
                # ....and wait for the input from the user.
                print(">> ", end='', flush=True)
            # The server sends a BYE message. The receive loop is interrupted.
            elif message["type"] == "BYE":
                print(message["content"])
                signal = False
                break
        else: # The received message is empty. We've been disconnected.
            print("You have been disconnected from the server")
            signal = False
            break

'''
Entry point. Instructions executed when the client is executed.
'''
if __name__ == '__main__':

    '''
    Get the input arguments:
    - The hostname (or its IP address) of the server.
    - The port where the server listens to.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("server_host", help="The host where the server is running")
    parser.add_argument("server_port", \
        help="The port on which the server is listening", type=int)
    args = parser.parse_args()
    server_host = args.server_host
    server_port = args.server_port

    print(f"Attempting to connect to {server_host} at {server_port}")
    #Attempt connection to server.
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((server_host, server_port))
    except Exception as e:
        print("Could not connect to the chat")
        print(e)
        sys.exit(0)

    # We're connected, the user is prompted to write his/her username.
    print("Write your name and start to chat: ", end='')
    username = input()
    # Send hello to the server.
    hello_message = utils.prepare_hello_message(username)
    utils.send_msg(hello_message, sock)

    #Create new thread to wait for data
    receiveThread = threading.Thread(target = receive, args = (sock, True))
    receiveThread.start()
    