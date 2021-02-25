from functions import *
from pyfiglet import figlet_format
from random import choice
import atexit
init()

word = choice(["Argov", "Itamar", "ITSAFE", "PYTHON", "v2.0"])
print(figlet_format(word))

print("Welcome! Choose an option:\n=====================\n1) Server\n2) Client\n=====================\n")
role = input("Select a role > ")

if role == "1":
    print(f"\n[*] Your IP Address is {get_ip()}")
    port = input("[*] Please enter a free port on your system > ")

    server = NetworkManagerServer(port)
    server()

    server_menu()
    server.select_option(input("Select an Option > "))

elif role == "2":
    ip = input("Enter an IP Address to connect to > ")
    port = input("Enter a port to connect to > ")
    audio = input("Enter 0 to turn notifications off > ")

    if audio == "0":
        audio = False
    else:
        audio = True

    NetworkManagerClient().main(ip, port, audio)

else:
    print(f"{Fore.RED}[-] Error: Please enter 1 for Server, 2 for Client.")
    input("Quitting...")
