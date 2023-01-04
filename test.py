import socket
import os
import mimetypes

# Constants
HOST = ''
PORT = 8000
BUFFER_SIZE = 1024

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f'Listening for connections on port {PORT}')

# Run the server indefinitely
while True:
    # Accept a new connection
    connection, address = server_socket.accept()
    print(f'New connection from {address}')
    
    # Receive the request data
    request_data = connection.recv(BUFFER_SIZE).decode()
    print(f'Received request:\n{request_data}')
    
    # Parse the request
    request_lines = request_data.split('\n')
    request_line = request_lines[0]
    method, path, _ = request_line.split()
    
    # Check if the method is GET
    if method == 'GET':
        # Get the requested file path
        file_path = path[1:]
        
        # Check if the file exists
        if os.path.exists(file_path):
            # Open the file in binary mode
            with open(file_path, 'rb') as f:
                # Get the file's mimetype
                mimetype, _ = mimetypes.guess_type(file_path)
                # Set the response status to 200 (OK)
                response_status = 'HTTP/1.1 200 OK\n'
                # Set the content type header
                response_headers = f'Content-Type: {mimetype}\n'
                # Set the content length header
                response_headers += f'Content-Length: {os.path.getsize(file_path)}\n'
                # End the headers
                response_headers += '\n'
                # Send the response
                connection.send(response_status.encode())
                connection.send(response_headers.encode())
                # Send the file contents to the client
                connection.sendfile(f)
        else:
            # Set the response status to 404 (Not Found)
            response_status = 'HTTP/1.1 404 Not Found\n'
            # End the headers
            response_headers = '\n'
            # Send the response
            connection.send(response_status.encode())
            connection.send(response_headers.encode())
    
    # Close the connection
    connection.close()
