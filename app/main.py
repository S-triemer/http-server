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
        chunck = conn.recv(1024).decode("utf-8")
        if not chunck:
            break
        else:
            client_req += chunck

    http_header = client_req
        
    def get_message(path):
        parts = path.split("/")
        return parts[2]
    
    def get_http_request(request):
        http_request = {"start-line": {}, "headers": {}, "body": {}}
        #using 1 here just in case if the body also includes "\r\n\r\n"
        header, body = request.split("\r\n\r\n", 1)
        
        ############################
        #parsing the header
        ############################
        lines = header.split("\r\n")

        #read the start line
        start_line = lines.pop(0)
        start_line_words = start_line.split()
        http_request["start-line"]["method"] = start_line_words[0]
        http_request["start-line"]["path"] = start_line_words[1]
        http_request["start-line"]["version"] = start_line_words[2]
        
        for line in lines:
            line_words = line.split()
            #need to check this because by spliting lines with (\r\n) the last line will be ("")
            if len(line_words)>=2:
                headers_key = line_words[0].rstrip(":")
                http_request["headers"][headers_key] = line_words[1]

        ############################
        #parsing the body
        ############################
        http_request["body"] = body
    
        return http_request

    
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
    
    http_request = get_http_request(http_header)
    path = http_request["start-line"]["path"]
 
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
    elif path == "/user-agent":
        print(http_request)
        message = http_request["headers"]["User-Agent"]
        response = build_http_response("200", "text/plain", f"{message}")
        print(response)
        response_bytes = response.encode("utf-8")
        conn.sendall(response_bytes)
    else:
        conn.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")
        
    
   


if __name__ == "__main__":
    main()
