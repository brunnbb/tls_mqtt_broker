import socket
import json
import threading

class Client:
    def __init__(self, client_id, host='127.0.0.1', port=5000):
        self.client_id = client_id
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def connect(self):
        self.socket.connect((self.host, self.port))
        self.__identify()
        threading.Thread(target=self.__listen_to_broker, daemon=True).start()

    def __identify(self):
        data = {
            'command': 'indentify',
            'client_id': self.client_id
        }
        self.__send(data)

    def __listen_to_broker(self):
        while self.running:
            try:
                data = self.socket.recv(1024)
                if data:
                    message = json.loads(data.decode('utf-8'))
                    print(f"[SERVER] {message}")
            except Exception as e:
                print(f'[ERROR] Receiving message: {e}')
                self.running = False

    def __send(self, data):
        try:
            message = json.dumps(data)
            self.socket.sendall(message.encode('utf-8'))
        except Exception as e:
            print(f'[ERROR] Sending message: {e}')

    def subscribe(self, topic):
        data = {
            'command': 'subscribe',
            'client_id': self.client_id,
            'topic': topic
        }
        self.__send(data)

    def unsubscribe(self, topic):
        data = {
            'command': 'unsubscribe',
            'client_id': self.client_id,
            'topic': topic
        }
        self.__send(data)

    def publish(self, topic, message):
        data = {
            'command': 'publish',
            'client_id': self.client_id,
            'topic': topic,
            'message': message
        }
        self.__send(data)

    def close(self):
        self.running = False
        self.socket.close()

    def main_loop(self):
        self.connect()
        print("\nComandos disponíveis:")
        print("- subscribe <topico>")
        print("- unsubscribe <topico>")
        print("- publish <topico> <mensagem>")
        print("- exit")

        while True:
            try:
                comando = input("> ").strip()
                if comando == "exit":
                    self.close()
                    break
                elif comando.startswith("subscribe "):
                    _, topico = comando.split(maxsplit=1)
                    self.subscribe(topico)
                elif comando.startswith("unsubscribe "):
                    _, topico = comando.split(maxsplit=1)
                    self.unsubscribe(topico)
                elif comando.startswith("publish "):
                    try:
                        _, topico, mensagem = comando.split(maxsplit=2)
                        self.publish(topico, mensagem)
                    except ValueError:
                        print("Uso: publish <topico> <mensagem>")
                else:
                    print("Comando não reconhecido.")
            except KeyboardInterrupt:
                self.close()
                break

if __name__ == '__main__':
    client_id = input("Digite o ID do cliente: ")
    client = Client(client_id)
    client.main_loop()
