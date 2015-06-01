import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005

def nao_connect():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((TCP_IP, TCP_PORT))

    return connection

def nao_action(connection, action):
    connection.send('1#%s$' % action)

    result = ''
    i = 0

    while 1:
        data = connection.recv(1024)
        result += data

        # i is data in Ko: max 600 Ko to avoid problems if end signal not sent
        i += 1

        if '1#end$' in result or i >= 600:
            break

    return result

def nao_disconnect(connection):
    connection.close()
