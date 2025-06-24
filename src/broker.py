import socket
import threading
from client_handler import ClientHandler
from security.auth import load_keys_from_dir

class Broker:
    def __init__(self, host="127.0.0.1", port=5000) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.lock = threading.Lock()
        
        # Each client and its public key
        self.clients_pub_keys: dict[str, str] = {}
        # Each topic and the keys for each client
        self.topics_keys: dict[str, dict[str, str]] = {}
        
        # Each topic and is messages
        self.topics: dict[str, list] = {}
        # Each client that connected and the topics subscribed
        self.clients: dict[str, list] = {}
        # Each client and its socket connection and session key
        self.clients_conn: dict[str, dict] = {}

    def run(self):
        try:
            self.clients_pub_keys = load_keys_from_dir("src\\security\\client_keys")
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen()
            print(f"\n[SERVER] listening at {self.host}:{self.port} ...")
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(
                    f"\nNew client connected at {client_address[0]}:{client_address[1]}"
                )
                handler = ClientHandler(client_socket, client_address, self)
                thread = threading.Thread(target=handler.handle)
                thread.start()
        except KeyboardInterrupt:
            print("\nServer interrupted")
        finally:
            self.server_socket.close()

if __name__ == "__main__":
    Broker().run()
