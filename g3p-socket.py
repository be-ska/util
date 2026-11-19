'''
Control G3P TCP protocol. Not sure why, but on Mac it needs to be run with sudo
'''
import socket
import json

HOST = "192.168.144.135"
PORT = 7878

def send(sock, msg):
    sock.sendall((json.dumps(msg) + "\n").encode())
    return json.loads(sock.recv(4096).decode())

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(5)
        s.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")

        # Start session
        resp = send(s, {"msg_id": 257, "token": 0})
        print("Session:", resp)
        token = resp.get("param", 1)

        while True:
            cmd = input("\nZoom level (100-1200), quit (q)").strip()
            if cmd.lower() == "q":
                break
            elif cmd.isdecimal() and 100 <= int(cmd) <= 1200:
                resp = send(s, {"msg_id": 2, "token": token, "type": "DZoom", "param": cmd.upper()})
                print("Response:", resp)
            else:
                print("Unknown command.")

        # End session
        send(s, {"msg_id": 258, "token": token})
        print("Session ended.")

if __name__ == "__main__":
    main()
