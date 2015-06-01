#!/usr/bin/env python

import socket

TCP_IP = '127.0.0.1'
TCP_PORT = 5005
BUFFER_SIZE = 150  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))

while True:
    s.listen(1)
    conn, addr = s.accept()

    print 'Connection address:', addr
    data = conn.recv(BUFFER_SIZE)

    if data == '1#camera$':
        raw_image = open('/home/tgalopin/Projets/Python/startnao/naoweb/main/image.base64', 'rb').read()
        conn.send(raw_image + '1#end$')
    else:
        conn.send('1#end$')

    conn.close()
