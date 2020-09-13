import socket
import json
import types
import selectors

from multiconn_server_helper import calc_result

HOST = '192.168.0.11'
PORT = 65432

sel = selectors.DefaultSelector()


# Functions
def accept_wrapper(sock):
    # Wrapper Function To Get The New Socket Object And Register
    conn, addr = sock.accept()
    print('accepted connection from', addr)
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    # Receive Data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            data.outb += recv_data
        else:
            print('closing connection to', data.addr)
            sel.unregister(sock)
            sock.close()
    # Send Data
    if mask & selectors.EVENT_WRITE:
        if data.outb:
            # Decode Data
            data_recv = json.loads(data.outb.decode())
            # Call Calulation Function
            result = calc_result(data_recv['number_1'],
                                 data_recv['number_2'],
                                 data_recv['number_3'])
            # Write Answer
            answer = {'result': result}
            print(answer)
            answer = json.dumps(answer).encode()
            data.outb = answer
            print('echoing', repr(data.outb), 'to', data.addr)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
lsock.bind((HOST, PORT))
lsock.listen()

print('listening on', (HOST, PORT))
# Configure Socket In Non-Blocking Mode
lsock.setblocking(False)
# Register The Socket To Be Monitored
sel.register(lsock, selectors.EVENT_READ, data=None)

# Event Loop
while True:
    # Blocks Until There Are Sockets Ready For I/O
    events = sel.select(timeout=None)
    for key, mask in events:
        # From A Listening Socket
        if key.data is None:
            accept_wrapper(key.fileobj)
        # From A Client Socket
        else:
            service_connection(key, mask)
