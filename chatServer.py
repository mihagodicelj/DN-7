import signal
import socket
import struct
import threading
from message import Message
import ssl

PORT = 12346
HEADER_LENGTH = 2

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(certfile="server-cert.pem", keyfile="server-key.pem")
context.load_verify_locations(cafile="server-cert.pem")
context.verify_mode = ssl.CERT_REQUIRED
context.set_ciphers("TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256")

def receive_fixed_length_msg(sock, msglen):
    message = b''
    while len(message) < msglen:
        chunk = sock.recv(msglen - len(message))
        if chunk == b'':
            raise RuntimeError("socket connection broken")
        message += chunk
    return message

def receive_message(sock):
    header = receive_fixed_length_msg(sock, HEADER_LENGTH)
    message_length = struct.unpack("!H", header)[0]
    message = None
    if message_length > 0:
        message = receive_fixed_length_msg(sock, message_length)
        message = message.decode("utf-8")
    return message

def send_message(sock, message):
    encoded_message = message.encode("utf-8")
    header = struct.pack("!H", len(encoded_message))
    message = header + encoded_message
    sock.sendall(message)

def client_thread(client_sock, client_addr):
    global clients
    print("[system] connected with " + client_addr[0] + ":" + str(client_addr[1]))
    print("[system] we now have " + str(len(clients)) + " clients")
    try:
        while True:
            msg_received = receive_message(client_sock)
            if not msg_received:
                break
            msg = Message()
            msg.fromJson(msg_received)
            msg.message = msg.message.upper()
            if not msg.isPrivate:
                print("[RKchat] [" + client_addr[0] + ":" + str(client_addr[1]) + "] : " + str(msg.message))
            else:
                if len(clients) == 1:
                    msg.message = "No other clients to send private message to"
            for client in clients:
                send_message(client, str(msg))
    except:
        pass
    with clients_lock:
        clients.remove(client_sock)
    print("[system] we now have " + str(len(clients)) + " clients")
    client_sock.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(("localhost", PORT))
server_socket.listen(1)
print("[system] listening ...")

clients = set()
clients_lock = threading.Lock()
while True:
    try:
        client_sock, client_addr = server_socket.accept()
        client_sock = context.wrap_socket(client_sock, server_side=True)
        with clients_lock:
            clients.add(client_sock)
        thread = threading.Thread(target=client_thread, args=(client_sock, client_addr))
        thread.daemon = True
        thread.start()
    except KeyboardInterrupt:
        break
print("[system] closing server socket ...")
server_socket.close()