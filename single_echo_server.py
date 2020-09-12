import socket
import json

from single_echo_server_helper import calc_result

HOST = '192.168.0.13'
PORT = 65431

# socket.socket() creates a socket object
# AF_INET is the internet adress family for IPv4
# SOCK_STREAM is the socket type for TCP (used protocol)
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    # Associate Socket With A Specified Network Interface And Port Number
    s.bind((HOST, PORT))
    # Listen For Connection From Client
    s.listen()
    # accept() blocks and waits for incoming connections
    conn, addr = s.accept()
    with conn:
        print('Connected by', addr)
        while True:
            # recv(1024) will return 1024 bytes
            data = conn.recv(1024)
            if not data:
                break

            else:
                data_recv = json.loads(data.decode())
                result = calc_result(data_recv['number_1'],
                                     data_recv['number_2'],
                                     data_recv['number_3'])
                answer = {'result': result}
                print(data_recv)
                answer = json.dumps(answer).encode()

                # Send Data To Client
                conn.sendall(answer)
