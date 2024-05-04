import socket


def main():
    print("Logs will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()

    #this returns a tuple (conn, address) where conn is a new socket object, representing the connection to a client after 3-way handshake
    #and address is the clients address.
    conn, addr = server_socket.accept()
    client_req = ""

    #This loop ensures that the complete http header is received even if it contains more than 1024 byte.
    #The http-header always ends with \r\n\r\n before the body starts
    while True:
        client_req += conn.recv(1024).decode("utf-8")
        
        if "\r\n\r\n" in client_req:
            break

    http_header = client_req

    def get_http_path(http_header):
        lines = http_header.split("\r\n")
        first_line = lines[0]
        words = first_line.split()
        if len(words) >= 2:
            return words[1]
        else:
            return None
        
    def get_message(path):
        parts = path.split("/")
        return parts[2]
    
    def build_http_response(status_code, content_type, body):
        response="HTTP/1.1 "
        if status_code == "200":
            response += "200 OK\r\n"
        elif status_code == "404":
            response += "404 Not Found\r\n"
        if content_type:
            response += f"Content-Type: {content_type}\r\n"
        if body:
            body_length = len(body)
            response += f"Content-Length: {body_length}\r\n"
        #Linebreak to separate header and body
        response += "\r\n"
        if body:
            response += body
        return response
        
    path = get_http_path(http_header)
    if path == "/":
        #sendall has to be used here instead of send because send only sends as much data as possible within the sockets send buffer and then
        #returns the number of bytes that were sent. So send needs to be called multiple times if it's buffer doesn't fit into the sockets send buffer.
        #sendall on the other hand keeps sending data until all data from its buffer has been sent.

        #the b-prefix has to be used because the send methods expects bytes instead of strings.
        conn.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
    elif path.startswith("/echo/"):
        message = get_message(path)
        response = build_http_response("200", "text/plain", f"{message}")
        response_bytes = response.encode("utf-8")
        conn.sendall(response_bytes)
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        
    
   


if __name__ == "__main__":
    main()
