import socket 
import threading
import json

class Broker:
    # dictionary of topics and the messages at that topic
    topics: dict[str, list] = {}
    # dictionary of clients and the topics each chose to subscribe
    clients: dict[str, list] = {}
    
    def __init__(self, host='127.0.0.1', port=5000) -> None:
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
    def run(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f'[SERVER] listening at {self.host}:{self.port}...')
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
            client_id = ''
            while True:
                client_data = self.__receive_request(client_socket, client_address)
                cmd = client_data['command']
                match cmd:
                    case 'indentify':
                        self.__identify_client(client_socket, client_address, client_data)
                    case 'subscribe':
                        self.__subscribe(client_socket, client_address, client_data)
                        return ''
                    case 'publish':
                        self.__publish(client_socket, client_address, client_data)
                        return ''
                    case 'unsubscribe':
                        self.__leave_topic(client_socket, client_address, client_data)
                        return ''
        except Exception as e:
            print(f'Error with client {client_address}: {e}')
    
    def __receive_request(self, client_socket, client_address) -> dict:
        data = client_socket.recv(1024)
        if data:
            try: 
                return json.loads(data.decode('utf-8'))
            except json.JSONDecodeError as e:
                print(f'Error decoding message: {e}')
                return {}
        return {}
              
    def __identify_client(self, client_socket, client_address, client_data):
        client_id = client_data['client_id']
        if client_id not in self.clients:
            self.clients[client_id] = []
            print(f'[SERVER] New client {client_id} identified at {client_address}')
        else:
            print(f'[SERVER] Client {client_id} reconnected at {client_address}')
    
    def __publish(self, client_socket, client_address, client_data):
        pass
    
    def __subscribe(self, client_socket, client_address, client_data):
        pass
        
    def __leave_topic(self, client_socket, client_address, client_data):
        pass

if __name__ == '__main__':
    broker = Broker()
    broker.run()