__author__ = 'Itay Bergig'

import socket
import threading

# Global list of connected clients in server
clients = []
server_socket = None
server_running = True
amountClients = 0
current_client_name = ""


# Handles in coming messages
def handle_client(client_socket):
    global current_client_name
    while True:
        try:
            message_with_name = ""
            while True:
                part = client_socket.recv(1024).decode('utf-8')
                message_with_name += part
                if len(part) < 1024:
                    break

            current_client_name = message_with_name.split('NAME:')[1].split('MESSAGE:')[0].strip()
            message = message_with_name.split('MESSAGE:')[1].strip()

            if message.lower() == 'quit':
                print(f"\n{current_client_name} requested disconnection.")
                remove_client(client_socket)
                break
            elif message:
                print(f"\nReceived message from {current_client_name}: {message}")
                broadcast(message_with_name, client_socket, True)
            else:
                remove_client(client_socket)

        except Exception as e:
            print(f"Error handling client: {e}")
            continue


# Sends out message to all clients except the one who sent the message
def broadcast(message_with_name, client_socket, flag):
    count = 0
    for client in clients:
        if client != client_socket:
            try:
                client.send(message_with_name.encode('utf-8'))
                count += 1

            except (BrokenPipeError, ConnectionResetError) as e:
                print(f"Error sending message to clients: {e}")
                remove_client(client)
            except Exception as e:
                print(f"Unexpected error while broadcasting: {e}")
                remove_client(client)
    if flag:
        print(f"Broadcasted message to {count} clients.")


# Removes a client from the server client list
def remove_client(client_socket):
    global amountClients
    try:
        if client_socket in clients:
            clients.remove(client_socket)
            amountClients -= 1
    except Exception as e:
        print(f"Error removing {current_client_name} from client list: {e}")
    finally:
        client_socket.close()  # Close the socket to release resources
        print(f"{current_client_name} disconnected - socket closed.")

        message_with_name = f"NAME:{current_client_name}MESSAGE:Has disconnected"
        broadcast(message_with_name, client_socket, False)

        monitor_clients()


# Creates a server socket
def setup_tcp_server(host='127.0.0.1', port=5555):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen()
    print("Server is listening on", host, ":", port)


def setup_udp_server(host='127.0.0.1', port=5555):
    global server_socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port))
    print("Server is listening on", host, "port", port)


# Shuts down the server
def shutdown_server():
    if server_socket:
        try:
            server_socket.close()
            print("\nServer shut down.")
        except socket.error as e:
            print(f"Socket error while shutting down the server: {e}")
        except Exception as e:
            print(f"Unexpected error while shutting down the server: {e}")


# Checks if there are clients connected to server
def monitor_clients():
    global server_running
    if amountClients == 0:
        server_running = False


def main():
    global amountClients
    setup_tcp_server()

    try:
        while server_running:
            try:
                # Accept a client connection
                server_socket.settimeout(1.0)
                client_socket, client_address = server_socket.accept()
                print(f"Connection established with client address: {client_socket} ")

                clients.append(client_socket)
                amountClients += 1

                # Creates a new thread to handle the client
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()

                monitor_clients()

            except socket.timeout:
                # Continue the loop to check server_running
                continue
            except (ConnectionAbortedError, OSError) as e:
                print(f"Error accepting client connection: {e}")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")

    finally:
        shutdown_server()


if __name__ == "__main__":
    main()
