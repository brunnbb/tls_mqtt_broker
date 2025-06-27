import json
import socket
from security.auth import *
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.fernet import Fernet
import os

PUBLIC_KEY_PATH = r"src\security\server_keys\broker_public_key.pem"
PRIVATE_KEY_PATH = r"src\security\server_keys\broker_priv_key.pem"
BROKER_CERT_PATH = r"src\security\certificates\bruno.crt"

class ClientHandler:
    def __init__(self, socket: socket.socket, address, broker):
        self.socket = socket
        self.address = address
        self.broker = broker
        self.public_key = load_public_key(PUBLIC_KEY_PATH)
        self.private_key = load_private_key(PRIVATE_KEY_PATH)
        self.running = True
        self.session_key = None
        self.clientId = ""

    def _finish(self, msg):
        print(msg)
        self.running = False
        self.socket.close()

    def _send_file(self, filePath):
        with open(filePath, "rb") as f:
            file_data = f.read()
            cert_size = len(file_data)
            self.socket.sendall(cert_size.to_bytes(4, byteorder="big"))
            self.socket.sendall(file_data)
        print("✅ The broker certification was sent to the client")

    def _receive_data(self):
        size_bytes = self.socket.recv(4)
        if not size_bytes:
            raise Exception("[ERROR] receiving size")

        size = int.from_bytes(size_bytes, byteorder="big")
        data = b""
        while len(data) < size:
            chunk = self.socket.recv(min(2048, size - len(data)))
            if not chunk:
                raise Exception("[ERROR] receiving data")
            data += chunk
        return data

    def _send_data(self, data, socket=None):
        socket = socket if socket else self.socket
        socket.sendall(len(data).to_bytes(4, byteorder="big"))
        socket.sendall(data)

    def _auth_handshake(self):
        try:
            # The broker sends its certificate and a proof
            self._send_file(BROKER_CERT_PATH)
            msg = os.urandom(32)
            signature = signing(self.private_key, msg)
            self._send_data(msg)
            self._send_data(signature)

            # The broker receives the client certificate and its proof
            client_cert_bytes = self._receive_data()
            msg_bytes = self._receive_data()
            signature_bytes = self._receive_data()

            if client_cert_bytes:
                client_cert = x509.load_pem_x509_certificate(client_cert_bytes)
                broker_cert = load_certificate(BROKER_CERT_PATH)
            else:
                raise Exception("[ERROR] reading client crt")

            if verify_certificate_signature(broker_cert, client_cert):
                print("✅ The client certification was signed by the broker.")
            else:
                raise Exception("❌ The client certification was not signed by the broker")

            client_public_key = client_cert.public_key()
            if verification_of_signature(client_public_key, msg_bytes, signature_bytes):
                print("✅ The client proved that it has the corresponting private key.")
            else:
                raise Exception("❌ The client failed to prove that it has the corresponting private key.")

            # The broker generates its symetric session key and sends it to the client
            key = Fernet.generate_key()
            self.session_key = Fernet(key)
            cipher_session_key = asymmetric_encrypt(key, client_public_key)
            self._send_data(cipher_session_key)

            # Stores client info
            self.clientId = client_cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
            if self.clientId not in self.broker.clients:
                self.broker.clients[self.clientId] = []
            self.broker.clients_conn[self.clientId] = {
                'socket': self.socket,
                'key': self.session_key }
            print(f"✅ Digital Envelope with {self.clientId} confirmed.\n")

        except Exception as e:
            self._finish(e)

    def _receive_msg(self):
        cipher_data = self._receive_data()
        if cipher_data:
            data = self.session_key.decrypt(cipher_data) # type: ignore
            message = json.loads(data.decode())
            return message

    def _format_and_send_msg(self, cmd, topic, content=None, session_key=None, socket=None):
        key = session_key if session_key else self.session_key
        data = {"cmd": cmd, "topic": topic}
        if content:
            data["content"] = content
        raw = json.dumps(data).encode() 
        encrypted = key.encrypt(raw) # type: ignore
        self._send_data(encrypted, socket) if socket else self._send_data(encrypted)

    # Must sync all old messages sent to the topic and the possible ones after a subscribe
    def _syncronize_msgs(self, topics_subs=None):
        topics_subs = [topics_subs] if topics_subs else self.broker.clients[self.clientId] 
        for topic in topics_subs:
            for msg in self.broker.topics[topic]:
                self._format_and_send_msg('msg', topic, msg)
       
    # Create must send all locally saved public keys to the client, so the client can encrypt the session key of the topic it generated
    # The Topic Key is encrypted and saved as a b64 str  
    def _create(self, msg):
        topic = msg.get("topic")
        content = "failure"
        with self.broker.lock:
            if topic not in self.broker.topics:
                self.broker.topics[topic] = []
                self.broker.topics_keys[topic] = {}
                self.broker.clients[self.clientId].append(topic)
                self._format_and_send_msg("create", topic, "success")
                
                for cli, pub_key in self.broker.clients_pub_keys.items():
                    self._format_and_send_msg('keys', topic, pub_key)
                    data = self._receive_msg()
                    if data:    
                        self.broker.topics_keys[topic][cli] = data['content']
                content = 'all_clear'
        self._format_and_send_msg("create", topic, content)

    # It searches for a topic key and sends it to the client, 
    # and them syncs all the msgs sent to the topic
    def _subscribe(self, msg):
        topic = msg.get("topic")
        content = "failure"
        with self.broker.lock:
            if topic in self.broker.topics:
                b64_key = self.broker.topics_keys[topic][self.clientId]
                self._format_and_send_msg('topic_key', topic, b64_key)
                self._syncronize_msgs(topics_subs=topic)
                self.broker.clients[self.clientId].append(topic)
                content = "success"
        self._format_and_send_msg("subscribe", topic, content)

    def _unsubscribe(self, msg):
        topic = msg.get("topic")
        content = "failure"
        with self.broker.lock:
            if topic in self.broker.clients[self.clientId]:
                self.broker.clients[self.clientId].remove(topic)
                content = "success"
        self._format_and_send_msg("unsubscribe", topic, content)

    def _publish(self, msg):
        topic = msg.get("topic")
        cipher_msg = msg.get('content')
        content = "failure"
        with self.broker.lock:
            if topic in self.broker.topics:
                self.broker.topics[topic].append(cipher_msg)
                for cli in self.broker.clients_conn:
                    cli_topics = self.broker.clients[cli]
                    if topic in cli_topics:
                        sck = self.broker.clients_conn[cli]['socket']
                        key = self.broker.clients_conn[cli]['key']
                        self._format_and_send_msg("msg", topic, cipher_msg, key, sck)
                content = "success"
        self._format_and_send_msg("publish", topic, content)

    def handle(self):
        try:
            self._auth_handshake()
            self._syncronize_msgs()
            while self.running:
                print("-"*90)
                print(f"Topics with msgs: {self.broker.topics}")
                print(f'\nClient and topics: {self.broker.clients}')
                msg = self._receive_msg()
                if msg:
                    cmd = msg["cmd"]
                    if cmd == "exit":
                        self._finish(f"Client {self.clientId} disconnected")
                    elif cmd == "create":
                        self._create(msg)
                    elif cmd == "subscribe":
                        self._subscribe(msg)
                    elif cmd == "unsubscribe":
                        self._unsubscribe(msg)
                    elif cmd == "publish":
                        self._publish(msg)
                    else:
                        print(f"Stop sending gibberish")
        except Exception as e:
            print(f"[ERROR] Exception with client at {self.address[0]}:{self.address[1]}: {e}")
            self.socket.close()
        finally:
            with self.broker.lock:
                self.broker.clients_conn.pop(self.clientId, None)
            print(f"Connection terminated with client at {self.address[0]}:{self.address[1]}")
