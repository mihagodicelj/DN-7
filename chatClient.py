import socket
import struct
import sys
import threading
from message import Message
import ssl

PORT = 12346
HEADER_LENGTH = 2

context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
context.load_cert_chain(certfile="client1-cert.pem", keyfile="client1-key.pem")
context.load_verify_locations(cafile="server-cert.pem")
context.set_ciphers("ECDHE-RSA-AES128-GCM-SHA256")

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

def message_receiver():
    while True:
        msg_received = receive_message(sock)
        if len(msg_received) > 0:
            msg = Message()
            msg.fromJson(msg_received)
            print("[RKchat] " + msg.message)

ime = input("prosim vnesite svoje ime: ")

print("[system] connecting to chat server ...")
raw_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock = context.wrap_socket(raw_sock, server_hostname="localhost")
sock.connect(("localhost", PORT))
print("[system] connected!")

msg = Message()
msg.username = ime
msg.setTimeNow()
msg.isPrivate = False
msg.message = "uporabnik " + ime + " se je pridruzil pogovoru"
send_message(sock, str(msg))

thread = threading.Thread(target=message_receiver)
thread.daemon = True
thread.start()

while True:
    try:
        msg_send = input("")
        msg = Message()
        if msg_send[0] == "/":
            msg.isPrivate = True
        else:
            msg.isPrivate = False
        msg.username = ime
        msg.message = msg_send
        msg.setTimeNow()
        send_message(sock, str(msg))
    except KeyboardInterrupt:
        sys.exit()