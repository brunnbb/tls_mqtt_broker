import socket 
import threading
import json

class Broker:
    topics: dict[str, list] = {}
    clients: dict[str, list] = {}
    
    def __init__(self, host='127.0.0.1', port=5000) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    def inicialize(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'[SERVER] listening at {self.host}:{self.port}...')
    
    def run(self):
        try:
            while True:
                client_socket, client_address = self.server_socket.accept()
                client_thread = threading.Thread(target=self.__handle_client, args=(client_socket, client_address))
                client_thread.start()
                
        except KeyboardInterrupt:
            print("\n[SERVER] interrupted")
        finally:
            if self.server_socket:
                self.server_socket.close()
                
    def __handle_client(self, client_socket, client_address):
        try:
            self.__identify_client(client_socket, client_address)
            while True:
                pass
        except Exception as e:
            print(f'Error with client {client_address}: {e}')
              
    def __identify_client(self, client_socket, client_address):
        pass
    
    def __publish(self, client_socket, client_address):
        pass
    
    def __subscribe(self, client_socket, client_address):
        pass
        
    def __leave_topic(self, client_socket, client_address):
        pass

    
if __name__ == '__main__':
    broker = Broker()
    broker.inicialize()
    broker.run()