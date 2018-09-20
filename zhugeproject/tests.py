from django.test import TestCase

# Create your tests here.



import socket
s= socket.socket()
host = 'DESKTOP-ANIHA2P'
port = 8000
s.connect((host,port))
print('Linked')
while True:
    send_mes=input()
    s.send(send_mes.encode())
    if send_mes =='exit':
        break

info = ''

while info != 'exit':
    info = s.recv(1024).decode()
    print('张三:'+info)


s.close()


