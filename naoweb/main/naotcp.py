import socket

TCP_IP = '169.254.89.225'
TCP_PORT = 8080

def nao_connect():
    connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connection.connect((TCP_IP, TCP_PORT))

    return connection

def nao_action_udp(connection, action):
    connection.send('1#%s$' % action)

def nao_action_tcp(connection, action):
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

    result = result[:-6]

    return result

def nao_disconnect(connection):
    connection.close()
