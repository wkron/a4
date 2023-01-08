import socket
import os
import mimetypes
from email.utils import parsedate
import time

# Constants
HOST = ''
PORT = 8000
BUFFER_SIZE = 1024

# Create the server socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)

print(f'Listening for connections on port {PORT}')


while True:

    # Accept connection
    connection, address = server_socket.accept()
    print(f'New connection from {address}')
    
    # Receive and parse request
    request_data = connection.recv(BUFFER_SIZE).decode()
    
    request_lines = request_data.split('\n')
    request_line = request_lines[0]
    method, path, _ = request_line.split()
    
    # Parse headers
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
        if not file_path and os.path.exists("index.html"):
            file_path= "index.html"
        print("this is file_path:",file_path)
        # Check if the file exists
        if os.path.exists(file_path) and not os.path.isdir(file_path):
            print("file exists, being served")
            # open file and parse
            with open(file_path, 'rb') as f:
                # check if-modified since and if-unmodified since headers
                if "if-modified-since" in headers:
                    if time.gmtime(os.stat(f).st_mtime) < parsedate(headers["if-modified-since"]):
                        response_status = 'HTTP/1.1 304 Not Modified\n'
                        response_headers = '\n'
                        connection.send(response_status.encode())
                        connection.send(response_headers.encode())
                        continue
                if "if-unmodified-since" in headers:
                    if time.gmtime(os.stat(f).st_mtime) > parsedate(headers["if-unmodified-since"]):
                        response_status = 'HTTP/1.1 412 Precondition Failed\n'
                        response_headers = '\n'
                        connection.send(response_status.encode())
                        connection.send(response_headers.encode())
                        continue

                # Get MIME type, construct and send response
                mimetype, _ = mimetypes.guess_type(file_path)
                
                response_status = 'HTTP/1.1 200 OK\n'

                response_headers = f'Content-Type: {mimetype}\n'
                response_headers += f'Content-Length: {os.path.getsize(file_path)}\n'
                response_headers += '\n'

                connection.send(response_status.encode())
                connection.send(response_headers.encode())
                connection.sendfile(f)

        elif not file_path or os.path.isdir(file_path):
            # Generate a list of the files and directories in the directory
            if not os.path.isdir(file_path):
                file_path += "."
            file_list = os.listdir(file_path)
            
            response_status = 'HTTP/1.1 200 OK\n'
            response_headers = 'Content-Type: text/html\n'
            # Build the HTML for the file list
            file_list_html = '<html><body><ul>'
            for file in file_list:
                file_list_html += f'<li><a href="{ "/" + file_path + "/" + file}">{file}</a></li>'
            file_list_html += '</ul></body></html>'
            
            response_headers += f'Content-Length: {len(file_list_html.encode())}\n'
            response_headers += '\n'
            
            connection.send(response_status.encode())
            connection.send(response_headers.encode())
            connection.send(file_list_html.encode())

        else:
            print("file not found, 404 returned")
            response_status = 'HTTP/1.1 404 Not Found\n'
            response_headers = '\n'
            
            connection.send(response_status.encode())
            connection.send(response_headers.encode())
            if os.path.exists("404.html"):
                connection.sendfile(open("404.html", "rb"))
    
    # Close the connection
    connection.close()
