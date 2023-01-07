import socket
import os
import mimetypes
from email.utils import parsedate
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
    # print(f'Received request:\n{request_data}')
    
    # Parse the request
    request_lines = request_data.split('\n')
    request_line = request_lines[0]
    method, path, _ = request_line.split()
    
    # Parse the headers
    headers = {}
    for line in request_lines[1:]:
        if ":" not in line:
            continue
        header_name, header_value = line.split(":", 1)
        header_name = header_name.strip().lower()
        header_value = header_value.strip()
        headers[header_name] = header_value

    print(headers)

    # Check if the method is GET
    if method == 'GET':
        # Get the requested file path
        file_path = path[1:]
        if not file_path and os.path.exists("index2.html"):
            file_path= "index.html"
        print("this is file_path:",file_path)
        # Check if the file exists
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            print("file exists, being served")
            # Open the file in binary mode
            with open(file_path, 'rb') as f:
                if "if-modified-since" in headers:
                    print("IF MODIFIED SINCE!")
                    if time.gmtime(os.stat(f).st_mtime) < parsedate(headers["if-modified-since"]):
                        response_status = 'HTTP/1.1 304 Not Modified\n'
                        response_headers = '\n'
                        connection.send(response_status.encode())
                        connection.send(response_headers.encode())
                        continue
                if "if-unmodified-since" in headers:
                    print("IF UNMODIFIED SINCE!")
                    if time.gmtime(os.stat(f).st_mtime) > parsetime(headers["if-unmodified-since"]):
                        response_status = 'HTTP/1.1 412 Precondition Failed\n'
                        response_headers = '\n'
                        connection.send(response_status.encode())
                        connection.send(response_headers.encode())
                        continue
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
        elif not file_path or os.path.isdir(file_path):
            # Generate a list of the files and directories in the directory
            if not os.path.isdir(file_path):
                file_path += "."
            file_list = os.listdir(file_path)
                # Set the response status to 200 (OK)
            response_status = 'HTTP/1.1 200 OK\n'
            # Set the content type header
            response_headers = 'Content-Type: text/html\n'
            # Start building the HTML for the file list
            file_list_html = '<html><body><ul>'
            for file in file_list:
                file_list_html += f'<li><a href="{ "/" + file_path + "/" + file}">{file}</a></li>'
            file_list_html += '</ul></body></html>'
            # Set the content length header
            response_headers += f'Content-Length: {len(file_list_html.encode())}\n'
            # End the headers
            response_headers += '\n'
            # Send the response
            connection.send(response_status.encode())
            connection.send(response_headers.encode())
            # Send the file contents to the client
            connection.send(file_list_html.encode())
        else:
            print("file not found, 404 returned")
            # Set the response status to 404 (Not Found)
            response_status = 'HTTP/1.1 404 Not Found\n'
            # End the headers
            response_headers = '\n'
            # Send the response
            connection.send(response_status.encode())
            connection.send(response_headers.encode())
            if os.path.exists("404.html"):
                connection.sendfile(open("404.html", "rb"))
    
    # Close the connection
    connection.close()
