import socket
import threading
import os
close_flag = False
PORT = 50500
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
FILES_PATH = os.getcwd() + "\Files\\"  # Thư mục chứa file trên server
def send_list_file(client_socket):
    try:
        with open("server_files.txt", 'r') as file:
            file_list = file.read()
        client_socket.sendall(file_list.encode())
        print("Send list file successfully")
    except Exception as e:
        print(f"Error: {e}")

def send_file_chunk_socket(filename, start, end, conn):
    try:
        filepath = os.path.join(FILES_PATH, filename)

        #gui dung luong cua chunk
        conn.send((str(end - start + 1) + " " + str(start)).encode())
        print("send chunk size successfully")
        with open(filepath, 'rb') as file:
            file.seek(start)
            remaining_bytes = end - start + 1
            while remaining_bytes > 0:
                chunk_size = min(1024, remaining_bytes)
                data = file.read(chunk_size)
                if not data:
                    break
                conn.send(data)
                remaining_bytes -= len(data)
        print(f"Sent chunk {start}-{end} of file {filename}.")
    except Exception as e:
        print(f"Error when sending file chunk: {e}")

def handle_client(conn, addr):
    try:
        print(f"Connected by {addr}")

        # Gửi danh sách file tới client
        send_list_file(conn)

        while True:
            # Nhận yêu cầu từ client
            request = conn.recv(1024).decode(FORMAT)
            if not request:
                continue

            parts = request.split()
            command = parts[0]

            if command == "DOWNLOAD":
                filename = parts[1]
                chunk = int(parts[2])
                filepath = os.path.join(FILES_PATH, filename)

                if not os.path.exists(filepath):
                    conn.sendall(b"ERROR")
                    print(f"File {filename} does not exist.")
                    continue

                file_size = os.path.getsize(filepath)
                chunk_size = file_size // 4
                start = chunk * chunk_size
                end = start + chunk_size - 1 if chunk < 3 else file_size - 1
                send_file_chunk_socket(filename,start,end,conn)
            else:
                conn.sendall(b"INVALID COMMAND")
                print(f"Invalid command received: {request}")
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    #finally:
     #   conn.close()
      #  print(f"Connection with {addr} closed.")

def start_server():
    os.makedirs(FILES_PATH, exist_ok=True)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(10)
    print(f"Server started on {SERVER}:{PORT}")

    while True:
        try:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
            print(f"Active connections: {threading.active_count() - 1}")
        except Exception as e:
            print(f"Error accepting connections: {e}")
        

if __name__ == "__main__":
    start_server()
