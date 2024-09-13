__author__ = 'Itay Bergig'

import socket
import threading


class ChatClient:
    def __init__(self, client_name, host, port):
        self.host = host
        self.port = port
        self.client_name = client_name
        self.client_socket = None
        self.connected = False

    # Connect to the server
    def connect_to_server(self):
        # tcp
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # udp
        # self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        try:
            self.client_socket.connect((self.host, self.port))
            self.connected = True
            print(f"Connected to server at {self.host}:{self.port}")

        except Exception as e:
            print(f"Error connecting to server: {e}")
            self.client_socket.close()
            self.client_socket = None

    # Receiving messages from server
    def receive_messages(self):
        while self.connected:
            try:
                self.client_socket.settimeout(1.0)

                message_with_name = ""
                while True:
                    part = self.client_socket.recv(1024).decode('utf-8')
                    message_with_name += part
                    if len(part) < 1024:
                        break

                current_client_name = message_with_name.split('NAME:')[1].split('MESSAGE:')[0].strip()
                message = message_with_name.split('MESSAGE:')[1].strip()

                if message:
                    print(f"{current_client_name}: {message}")
                else:
                    print("Connection closed by server.")
                    self.connected = False
            except socket.timeout:
                # Continue the loop to check if socket connected
                continue
            except (socket.error, ConnectionResetError) as e:
                print(f"Socket error while receiving message: {e}")
                self.connected = False
            except Exception as e:
                print(f"Unexpected error while receiving message: {e}")
                self.connected = False

    # Sending messages to server
    def send_message(self, message):
        if not self.connected:
            print("Cannot send message, not connected to server.")
            return

        if self.client_name:
            message_with_name = f"NAME:{self.client_name}MESSAGE:{message}"
        else:
            message_with_name = message

        try:
            self.client_socket.send(message_with_name.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message: {e}")

    # Start chat
    def start(self):
        if not self.client_socket:
            print("No connection established.")
            return

        # Start a thread to receive messages
        receive_thread = threading.Thread(target=self.receive_messages)
        receive_thread.start()

        try:
            while True:
                message = input("")
                self.send_message(message)
                if message.lower() == 'quit':
                    self.connected = False
                    print("Disconnecting from server.")
                    break

        except Exception as e:
            print(f"Error in client: {e}")
        finally:
            if self.client_socket:
                self.client_socket.close()
                print("Client socket closed.")
