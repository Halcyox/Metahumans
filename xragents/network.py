import os
import socket

def ping(host):
    response = os.system("ping -n 1 " + host)
    if response == 0:
        return True
    else:
        return False

def send_message(message, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.sendall(message.encode("utf-8"))
        print("Message sent successfully.")

if __name__ == "__main__":
    host = "172.20.128.1"
    port = 12345

    if ping(host):
        send_message("Ping test successful!", host, port)
    else:
        print(f"{host} is not reachable.")
