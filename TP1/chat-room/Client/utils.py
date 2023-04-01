import json
import struct

'''
Utility functions
'''


def send_msg(message, sock):
    '''
        Send a message over the given socket.

        Parameters
        ----------
        message : The message to send.
        sock : The socket used to send the message.

    '''
    # Serialize the message as a json and encodes it.
    message = json.dumps(message).encode('utf-8')
    # Prefix the message with 4 bytes indicating the length.
    message = struct.pack('>L', len(message)) + message
    # Finally send the message
    sock.sendall(message)


def recv_msg(sock):
    '''
    Receives a message over a socket.

    Parameters
    ----------
    sock : The socket used to receive the message.

    Return
    ------
    Returns the received message.

    Source: https://stackoverflow.com/questions/17667903/python-socket-receive-large-amount-of-data
    '''
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    msg = recvall(sock, msglen)
    return json.loads(msg.decode('utf-8'))


def recvall(sock, n):
    '''
    Receives n bytes from the given socket.

    Parameters
    ----------
    sock : The socket used to receive the data.
    n : The number of bytes to receive.

    Return
    ------
    The received data.

    '''
    data = bytearray()
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data.extend(packet)
    return data


def prepare_hello_message(name):
    '''
    Prepares a message of type HELLO

    Parameters
    ---------
    name : The name of the client to welcome.

    Returns
    -------
    The prepared HELLO message.
    '''

    return {"type": "HELLO", "name": name}


def prepare_welcome_message(message):
    '''
    Prepares a message of type WELCOME

    Parameters
    ---------
    message : The content of the message.

    Returns
    -------
    The prepared WELCOME message.
    '''

    return {"type": "WELCOME", "content": message}


def prepare_bye_message(message):
    '''
    Prepares a message of type BYE

    Parameters
    ---------
    message : The content of the message.

    Returns
    -------
    The prepared BYE message.
    '''

    return {"type": "BYE", "content": message}


def prepare_chat_message(message):
    '''
    Prepares a message of type CHAT

    Parameters
    ---------
    message : The content of the message.

    Returns
    -------
    The prepared CHAT message.
    '''

    return {"type": "CHAT", "content": message}


def prepare_quit_message():
    '''
    Prepares a message of type QUIT

    Parameters
    ---------
    message : The content of the message.

    Returns
    -------
    The prepared QUIT message.
    '''

    return {"type": "QUIT"}
