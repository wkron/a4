import socket
import os
import re

# Create a socket and bind it to the specified port
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8000))

# Set the root folder for the server
root_folder = ''

# Listen for incoming connections
sock.listen(1)

while True:
    # Accept a connection
    conn, addr = sock.accept()
    print('Connected by', addr)
    # Receive the request
    request = conn.recv(1024).decode()
    # Split the request into individual lines
    lines = request.split('\n')
    # Extract the request method, URL, and headers
    if len(lines) >= 3:
     method, url, headers = lines[0], lines[1], lines[2:]
    else:
     method = ''
     url = ''
     headers = []

    # Extract the root and file path from the URL
    if '/' in url:
     root, file_path = url.split('/', 1)
    else:
     root = ''
     file_path = url

    # Concatenate the root folder and file path
    file_path = os.path.join(root_folder, file_path)
    # Check if the file exists
    if os.path.exists(file_path):
        # If the file exists, send a 200 status code and the contents of the file
        conn.send('HTTP/1.1 200 OK\n'.encode())
        with open(file_path, 'r') as f:
            contents = f.read()
        conn.send(contents.encode())
    else:
        # If the file does not exist, send a 404 status code and an error message
        conn.send('HTTP/1.1 404 Not Found\n'.encode())
        conn.send('File not found'.encode())
    # Close the connection
    conn.close()
