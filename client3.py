__author__ = 'Itay Bergig'

from chat_client import ChatClient

# Connects to the server and starts the client thread
if __name__ == "__main__":
    client = ChatClient("Shai", host='127.0.0.1', port=5555)
    client.connect_to_server()
    client.start()
