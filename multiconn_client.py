import socket
import json
import types
import selectors


HOST = '192.168.0.11'
PORT = 65432
NUM_CONNS = 1

sel = selectors.DefaultSelector()

input_data = {'number_1': 3.5, 'number_2': 1, 'number_3': 0.2}
# List Of Messages
messages = [(json.dumps(input_data)).encode()]


# Functions
def start_conncetions(HOST, PORT, NUM_CONNS):
    server_addr = (HOST, PORT)

    for i in range(NUM_CONNS):
        connid = i+1
        print('starting connection', connid, 'to', server_addr)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setblocking(False)
        sock.connect_ex(server_addr)
        events = selectors.EVENT_READ | selectors.EVENT_WRITE
        # Define Data Type
        # msg_total: number of messages
        # recv_total: number of expected messages (break condition)
        data = types.SimpleNamespace(connid=connid,
                                     msg_total=sum(len(m) for m in messages),
                                     recv_total=0,
                                     messages=list(messages),
                                     outb=b'')
        sel.register(sock, events, data=data)


def service_connection(key, mask):
    sock = key.fileobj
    data = key.data
    # Receive Data
    if mask & selectors.EVENT_READ:
        recv_data = sock.recv(1024)
        if recv_data:
            print('received', repr(recv_data), 'from', data.connid)
            data_recv = json.loads(recv_data.decode())
            assert(data_recv['result'] == 0.9)
            # Set Condition Close Connection
            # Instead of data.recv_total += len(recv_data)
            data.recv_total = data.msg_total
        if not recv_data or data.recv_total == data.msg_total:
            print('closing connection', data.connid)
            sel.unregister(sock)
            sock.close()
    # Send Data
    if mask & selectors.EVENT_WRITE:
        if not data.outb and data.messages:
            data.outb = data.messages.pop(0)
        if data.outb:
            print('sending', repr(data.outb), 'to connection', data.connid)
            sent = sock.send(data.outb)
            data.outb = data.outb[sent:]


start_conncetions(HOST, PORT, NUM_CONNS)

while True:
    events = sel.select(timeout=1)
    if events:
        for key, mask in events:
            service_connection(key, mask)
    if not sel.get_map():
        break
