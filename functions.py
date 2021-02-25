import subprocess as sp
import socket
import threading
from colorama import Fore, init
from os import popen, path, chdir, getcwd
import json
from playsound import playsound
import time

init()


# Server class
class NetworkManagerServer(object):
    def __init__(self, port):
        #  Setting up the server and it's settings.
        try:
            self.port = port
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind(("", int(port)))
            self.server.listen(10)
            self.audio = True

            self.clients = []

        except Exception as e:
            print(f"{Fore.RED}[-] Socket creation failed: {e}{Fore.RESET}")

    def __call__(self, *args, **kwargs):
        # Calling the function that accepts clients.
        t = threading.Thread(target=self.accepting_clients)
        t.start()

    def accepting_clients(self):
        # Accepts clients and appending them to the clients list which contains dictionaries of the clients ips and
        # sockets.
        try:
            while True:
                client, addr = self.server.accept()

                self.clients.append({"ip": list(addr)[0], "socket": client})

        except Exception as e:
            print(f"{Fore.RED}[-] Failed connecting to clients. {e}{Fore.RESET}")

    def select_option(self, option):
        # Getting the user's option from the menu and executing it.
        if option == "1":
            # Show connected clients, if there are none it will print there aren't.
            if len(self.clients) > 0:
                print("\nConnected Clients:\n==================")

                for i in range(len(self.clients)):
                    for client in self.clients:
                        print(f"{Fore.GREEN}{client['ip']}{Fore.RESET}")
                print("==================")

            else:
                print("\nThere are no connected clients.\n")

            server_menu()
            self.select_option(input("Select an Option > "))

        elif option == "2":
            # Chat with a client.
            print("\n\nChoose a client:\n==================")
            for i in range(len(self.clients)):
                for client in self.clients:
                    print(f"{Fore.GREEN}{i}) {client['ip']}{Fore.RESET}")
            try:
                print("==================")
                index = int(input("Choose a client > "))

                self.chat(index)

            except Exception as e:
                if e == ValueError:
                    print(f"{Fore.RED}[-] Error: Please enter a valid client index.{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

                elif e == IndexError:
                    print(f"{Fore.RED}[-] Error: please enter an existing client.{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

                else:
                    print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

        elif option == "3":
            # Execute commands on a client.
            print("\n\nChoose a client:\n==================")
            for i in range(len(self.clients)):
                for client in self.clients:
                    print(f"{Fore.GREEN}{i}) {client['ip']}{Fore.RESET}")
            try:
                print("==================")
                index = int(input("Choose a client > "))

                if 0 <= index <= 10:
                    print(f"{Fore.GREEN}[+] Successfully chose a client, enter exit to exit.{Fore.RESET}")
                    self.cmds(index)

            except ValueError:
                print(f"{Fore.RED}[-] Error: Please enter a valid client index.{Fore.RESET}")

            except Exception as e:
                print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")

        elif option == "4":
            # Download/ upload files with a client
            print("\n\nChoose a client:\n==================")
            for i in range(len(self.clients)):
                for client in self.clients:
                    print(f"{Fore.GREEN}{i}) {client['ip']}{Fore.RESET}")
            try:
                print("==================")
                index = int(input("Choose a client > "))

                self.files(index)

            except Exception as e:
                if e == ValueError:
                    print(f"{Fore.RED}[-] Error: Please enter a valid client index.{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

                elif e == IndexError:
                    print(f"{Fore.RED}[-] Error: please enter an existing client.{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

                else:
                    print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")
                    server_menu()
                    self.select_option(input("Select an Option > "))

        elif option == "5":
            # Change audio setting: turn off/ on the new message sound.
            audio = input("Enter 0 to turn notifications off, 1 to turn it on > ")

            if audio == "0":
                self.audio = False
                print(f"{Fore.GREEN}[+] Turned notifications off.{Fore.RESET}")
                server_menu()
                self.select_option(input("Select an option >  "))

            elif audio == "1":
                self.audio = True
                print(f"{Fore.GREEN}[+] Turned notifications on.{Fore.RESET}")
                server_menu()
                self.select_option(input("Select an option >  "))

        elif option == "E" or option == "e" or option == "6":
            print("Quitting...")

            for i in range(len(self.clients)):
                for client in self.clients:
                    client['socket'].sendall(str({"exit": "exit"}).encode())
                    client["socket"].close()

            self.server.close()
            time.sleep(1)

        else:
            print(f"{Fore.RED}[-] Error: please choose one of the following options.{Fore.RESET}")
            server_menu()
            self.select_option(input("Select an option >  "))

    def chat(self, index):
        # The function that receives and sends messages with msg type.
        try:
            client = self.clients[int(index)]['socket']
            ip = self.clients[int(index)]['ip']
            print(f"{Fore.GREEN}[+] Connected to a chat with {ip}. Enter EXIt to close the chat.{Fore.RESET}")

            while True:
                message = input("You: ")

                if message != "EXIt":
                    message = ({"msg": message})
                    client.sendall(json.dumps(message).encode())

                    data = json.loads(client.recv(2048).decode())

                    if "msg" in data:
                        if self.audio:
                            playsound("new_message.mp3")
                        print(f"{ip}: {data['msg']}")

                else:
                    break

            client.sendall(json.dumps({"exit": "close_chat"}).encode())

            print(f"{Fore.RED}[!] Closing the chat...{Fore.RESET}")
            server_menu()
            self.select_option(input("Select an option >  "))

        except Exception as e:
            print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")
            server_menu()
            self.select_option(input("Select an option >  "))

    def cmds(self, index):
        # Sends commands and receives the result of them.
        try:
            client = self.clients[int(index)]['socket']
            while True:
                cmd = input("Enter a command to execute > ")

                if cmd != "exit":
                    client.sendall(json.dumps({"cmd": cmd}).encode())
                    result = json.loads(client.recv(2048).decode())

                    if "cmd" in result:
                        print(result["cmd"] + '\n')

                else:
                    print(f"{Fore.RED}{Fore.RESET}")
                    break

            server_menu()
            self.select_option(input("Select an option >  "))

        except Exception as e:
            print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")
            server_menu()
            self.select_option(input("Select an option >  "))

    def files(self, index):
        # Sends\ receives files.
        client = self.clients[int(index)]['socket']

        while True:
            print(f"{Fore.GREEN}Choose an option or [e] to exit\n===============================\n1) Send a file\n2) "
                  f"Download a file\n==============================={Fore.RESET}")

            choice = input("Choose an option > ")
            if choice == "1":
                filename = input("Enter the path of the file and it's extension (name.txt, name.py, etc) > ")
                try:
                    with open(filename, "rb") as fd:
                        file_data = fd.read(198283722)

                    client.sendall(json.dumps({"file_name": filename}).encode())
                    time.sleep(1)
                    client.sendall(file_data)
                    data = json.loads(client.recv(2048).decode())

                    if "file" in data:
                        name = data["file"]

                        if name == filename:
                            print(f"{Fore.GREEN}[+] Successfully sent the file.{Fore.RESET}")
                        else:
                            print(f"{Fore.GREEN}[+] Successfully sent the file. Client changed it's name to {name}"
                                  f"{Fore.RESET}\n\n")

                    elif "error" in data:
                        e = data["error"]
                        print(f"{Fore.RED}[-] Error: {e}.{Fore.RESET}")

                except Exception as e:
                    print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")
                    continue

            elif choice == "2":
                print(f"{Fore.LIGHTYELLOW_EX}\n[!] Warning: In order to download a file from the client you need it's "
                      f"full path and extension. \nUse the option 'Execute Commands' to find it.{Fore.RESET}\n")
                file = input("Enter the full path of the file > ")

                try:
                    client.sendall(json.dumps({"download_file": file}).encode())
                    file_data = client.recv(198283722)
                    file_name = input("How do you want to call the file? Enter the extension too (file.txt, names.log, "
                                      "etc) > ")

                    if path.isfile(file_name):
                        print(f"{Fore.RED}[-] Error: A file with the name of the received file already exist."
                              f"{Fore.RESET}")

                        rename = input("Do you want to rename the file? [y]es or [n]o > ")

                        if rename == "y":
                            file_name = input("Choose a new name for the file > ")
                            with open(file_name, "wb") as fd:
                                fd.write(file_data)
                                print(f"{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}")

                        elif rename == "n":
                            final_rename = input("Are you sure? this will overwrite the existing file [y]es "
                                                 "or [n]o > ")

                            if final_rename == "n":
                                file_name = input("Choose a new name for the file > ")
                                with open(file_name, "wb") as fd:
                                    fd.write(file_data)

                                print(f"\n{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}\n")

                            else:
                                with open(file_name, "wb") as fd:
                                    fd.write(file_data)

                                print(f"\n{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}\n")

                    else:
                        with open(file_name, "wb") as fd:
                            fd.write(file_data)
                            print(f"\n{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}\n")

                except Exception as e:
                    print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")

            elif choice == "e":
                print(f"{Fore.RED}[!] Quitting...{Fore.RESET}")
                break

            else:
                print(f"{Fore.RED}[-] Error: please select a valid option.{Fore.RESET}")
                continue

        server_menu()
        self.select_option(input("Select an option >  "))


# Client Class
class NetworkManagerClient(object):
    def main(self, ip, port, audio):
        # Sets up the client and receives data all the time. When data is received, it checks the first item in the
        # json to get the type of the data that was sent.
        try:
            self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client.connect((ip, int(port)))
            self.audio = audio

            print(f"\n{Fore.GREEN}[+] Connected to {ip}{Fore.RESET}\n")

            while True:
                data = self.client.recv(2048).decode()

                if data is not None:
                    data = json.loads(data)

                    # Identifying the data type we are getting so we will know what to do with it.
                    if "msg" in data:
                        if self.audio:
                            playsound("new_message.mp3")

                        print(f'Server: {data["msg"]}')

                        message = input("You: ")
                        message = json.dumps({"msg": message})
                        self.client.sendall(message.encode())

                    elif "cmd" in data:
                        if data["cmd"] == "cd":
                            self.client.sendall(json.dumps({"cmd": getcwd()}).encode())

                        else:
                            check_for_cd = list(data["cmd"].split(" "))
                            if check_for_cd[0] == "cd":
                                if check_for_cd[1] == "..":
                                    chdir('..')
                                    result = getcwd()

                                else:
                                    try:
                                        chdir(check_for_cd[1])
                                        result = getcwd()

                                    except FileNotFoundError:
                                        result = "The system cannot find the path specified."

                                self.client.sendall(json.dumps({"cmd": result}).encode())

                            else:
                                command = sp.run(data["cmd"], shell=True, text=True, capture_output=True)

                                if command.stdout != "":
                                    self.client.sendall(json.dumps({"cmd": command.stdout}).encode())

                                else:
                                    if command.returncode == 1:
                                        self.client.sendall(json.dumps({"cmd": command.stderr}).encode())

                                    else:
                                        self.client.sendall(json.dumps({"cmd": data["cmd"]}).encode())

                            print(f"{Fore.GREEN}[+] Got command {data['cmd']}{Fore.RESET}")

                    elif "file_name" in data:
                        try:
                            file_name = data["file_name"]
                            file_data = self.client.recv(198283722)

                            if path.isfile(file_name):
                                print(f"{Fore.RED}[-] Error: A file with the name of the received file already exist."
                                      f"{Fore.RESET}")

                                rename = input("Do you want to rename the file? [y]es or [n]o > ")

                                if rename == "y":
                                    file_name = input("Choose a new name for the file > ")
                                    with open(file_name, "wb") as fd:
                                        fd.write(file_data)
                                        print(f"{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}")
                                        self.client.sendall(json.dumps({"file": file_name}).encode())

                                elif rename == "n":
                                    final_rename = input("Are you sure? this will overwrite the existing file [y]es "
                                                         "or [n]o > ")

                                    if final_rename == "n":
                                        file_name = input("Choose a new name for the file > ")
                                        with open(file_name, "wb") as fd:
                                            fd.write(file_data)

                                        print(f"{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}")
                                        self.client.sendall(json.dumps({"file": file_name}).encode())

                                    else:
                                        with open(file_name, "wb") as fd:
                                            fd.write(file_data)

                                        print(f"{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}")
                                        self.client.sendall(json.dumps({"file": file_name}).encode())

                            else:
                                with open(file_name, "wb") as fd:
                                    fd.write(file_data)
                                    print(f"{Fore.GREEN}[+] Successfully downloaded the file.{Fore.RESET}")
                                    self.client.sendall(json.dumps({"file": file_name}).encode())

                        except Exception as e:
                            self.client.sendall(json.dumps({"error": e}).encode())

                    elif "download_file" in data:
                        file_name = data["download_file"]
                        print(f"{Fore.GREEN}[+] Server downloaded the file {file_name}{Fore.RESET}")

                        with open(file_name, "rb") as fd:
                            file_data = fd.read()
                            self.client.sendall(file_data)

                    elif "exit" in data:
                        if data["exit"] == "exit":
                            print("[!] Server closed. Quitting...")
                            self.client.close()
                            break

                        elif data["exit"] == "close_chat":
                            print(f"{Fore.RED}[!] Server closed the chat.{Fore.RESET}")

                else:
                    continue

        except Exception as e:
            if e == ConnectionError or ConnectionResetError or ConnectionAbortedError or ConnectionRefusedError:
                print(Fore.RED)
                retry = input("[-] Error: server seems to be down.\nDo you want to try reconnecting? [y]es/ [n]o > ")
                print(Fore.RESET)

                if retry == "y":
                    self.main(ip, port, audio)

                else:
                    print("Ok. Quitting...")
                    self.client.close()
                    time.sleep(1)
            else:
                print(f"{Fore.RED}[-] Error: {e}{Fore.RESET}")


# Other Functions
def server_menu():
    # Server menu.
    print(f"""
{Fore.GREEN}\nChoose an Action\n================================\n1) Get Connected Clients\n2) Chat with a Client
3) Execute Commands on a Client\n4) Transfer Files\n5) Notifications Settings\n6) Exit\n================================
{Fore.RESET}""")


def get_ip():
    # Returns the ip of the client\ server.
    for line in popen("ipconfig").readlines():
        if "IPv4 Address" in line:
            ip = line[line.find(":") + 2:]
            return ip
