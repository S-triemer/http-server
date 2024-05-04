import socket


def main():
    print("Logs will appear here!")

    server_socket = socket.create_server(("localhost", 4221), reuse_port=True)
    server_socket.listen()
    conn = server_socket.accept() #this returns a new socket object, representing the connection to a client after 3-way handshake
    print(conn)
    conn.send("HTTP/1.1 200 OK\r\n\r\n")


if __name__ == "__main__":
    main()
