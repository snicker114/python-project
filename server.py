import os
import socket
import threading


class FileServer:
    def __init__(self, host='localhost', port=5555, root_folder="C:\\"):
        self.host = host
        self.port = port
        self.root_folder = root_folder
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_directories(self, root_dir):
        return [item for item in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, item))]

    def send_file(self, client_socket, file_path):
        try:
            with open(file_path, 'rb') as file:
                while chunk := file.read(1024):
                    client_socket.sendall(chunk)
            client_socket.sendall(b"DONE")  # Signal end of file
            print(f"File sent: {file_path}")
        except Exception as e:
            error_message = f"Error reading the file: {str(e)}"
            client_socket.sendall(error_message.encode('utf-8'))
            print(error_message)

    def handle_client(self, client_socket):
        current_folder = self.root_folder

        directories = self.get_directories(self.root_folder)
        client_socket.send("\n".join(directories).encode('utf-8'))

        while True:
            request = client_socket.recv(1024).decode('utf-8').strip()
            if not request:
                break

            print(f"Client requested: {request}")

            if not request.startswith('get ') and not request.startswith('search '):
                full_folder_path = os.path.join(current_folder, request)
                if os.path.exists(full_folder_path) and os.path.isdir(full_folder_path):
                    current_folder = full_folder_path
                    files = os.listdir(current_folder)
                    client_socket.send("\n".join(files).encode('utf-8')) if files else client_socket.send(
                        "The folder is empty.".encode('utf-8'))
                else:
                    client_socket.send("The folder does not exist.".encode('utf-8'))

            elif request.startswith('get '):
                file_path = os.path.abspath(request[4:].strip())
                if os.path.exists(file_path) and os.path.isfile(file_path):
                    client_socket.send("Sending file...".encode('utf-8'))
                    self.send_file(client_socket, file_path)
                else:
                    client_socket.send("The file does not exist.".encode('utf-8'))

            elif request.startswith('search '):
                query = request[7:].strip().lower()
                matches = []

                # Search files and folders in the current directory
                for item in os.listdir(current_folder):
                    if query in item.lower():
                        matches.append(item)

                if matches:
                    client_socket.send("\n".join(matches).encode('utf-8'))
                else:
                    client_socket.send("No matches found.".encode('utf-8'))

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server started, listening on {self.host}:{self.port}...")

        while True:
            client_socket, addr = self.server_socket.accept()
            print(f"Accepted connection from {addr}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()


if __name__ == "__main__":
    server = FileServer()
    server.start()





