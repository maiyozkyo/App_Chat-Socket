import socket
from threading import Thread
import hashlib
import re
import time
import os
import os.path
import  tqdm
import pickle

PORT = 7890
BUFFER_SIZE = 4096
SEPARATOR = "<SEPARATOR>"

def encrypt_psw(str):
    hl = hashlib.md5()
    hl.update(str.encode("utf-8"))
    return hl.hexdigest()

OnlineSocketList = list()  # Connection list of online users, using for group messaging 
SocketToUser = dict()  # Store mapping between Socket connection with users

def checkUser(username, encrypted_psw):
    print("Check user information...")
    with open("./users.txt", "r") as users_file:
        users_data = users_file.read()
    users_list = users_data.split()
    for user in users_list:
        if user == username:
            # Authentication
            index = users_list.index(user) + 1
            if users_list[index] == encrypted_psw:
                return "Login successfully！"
            else:
                return "Password is incorrect, please try again！"
    else:
        return "The user does not exist, please register first！"

def addUser(new_socket, username, encrypted_psw):
    try:
        print("register: user: " + username + ", key: " + encrypted_psw)

        # Read database from file users.txt and split it into list of string 
        with open("./users.txt", "r") as users_file:
            users_data = users_file.read()
        users_list = users_data.split("\n")

        # Traverse the query list to see if the user name already exists
        for user in users_list:
            if user == username:  # Username already exists
                new_socket.sendall("Sorry, username already exists! ".encode("utf-8"))
                return
        else:
            # Add username and password(encrypted with MD5)
            with open("./users.txt", "a") as users_file:
                users_file.write(username + "\n" + encrypted_psw + "\n")
            new_socket.sendall("Register successfully! ".encode("utf-8"))
    except Exception as ret:
        print("Error when adding user data：" + str(ret))
        new_socket.sendall("An unknown error occurred！".encode("utf-8"))

def updateOnlineList():
    online_usernames = ""
    for sk in OnlineSocketList:
        online_usernames += SocketToUser[sk] + "#!"
    # Send username in online list to all online users
    for socket in OnlineSocketList:
        # Send user's information to distinguish information from online user list
        socket.sendall(("#!onlines#!" + online_usernames).encode("utf-8"))

def sendOnline_notice(new_socket):
    welcome_str = "@@@@@@@@@@ Welcome " + SocketToUser[new_socket] + " come to MyChat! @@@@@@@@@@"
    # Send notifications when user's just been online to all online users
    for socket in OnlineSocketList:
        socket.sendall(("#!notices#!" + welcome_str).encode("utf-8"))

def sendOffline_notice(offline_socket):
    left_str = "__________ "+ SocketToUser[offline_socket] + " has left __________"
    for socket in OnlineSocketList:
        socket.sendall(("#!notices#!" + left_str).encode("utf-8"))

def LoginHandler(new_socket):
    username_psw = new_socket.recv(1024).decode("utf-8")
    ret = re.match(r"(.+)#!#!(.+)", username_psw)
    username = ret.group(1)
    password = ret.group(2)
    encrypted_psw = encrypt_psw(password)
    check_result = checkUser(username, encrypted_psw)
    new_socket.sendall(check_result.encode("utf-8"))  # Send login result to user

    # After successful login, do the following
    if check_result == "Login successfully！":
        SocketToUser[new_socket] = username
        OnlineSocketList.append(new_socket)
        print(OnlineSocketList)
        updateOnlineList()
        time.sleep(8)
        sendOnline_notice(new_socket)

def RegisterHandler(new_socket):
    username_psw = new_socket.recv(1024).decode("utf-8")
    ret = re.match(r"(.+)#!#!(.+)", username_psw)
    username = ret.group(1)
    password = ret.group(2)
    encrypted_psw = encrypt_psw(password)
    addUser(new_socket, username, encrypted_psw)


def MessageHandler(new_socket):
    content = new_socket.recv(1024).decode("utf-8")
    for socket in OnlineSocketList:
        socket.sendall(("#!message#!" + SocketToUser[new_socket] + "#!" +content).encode("utf-8"))

def sendFile(new_socket):
    file_path = new_socket.recv(1024).decode("utf-8")
    print("Uploading file from the server...")
    file = open(file_path, 'r')
    encode = file.read()
    data = ""
    for i in encode:
        data = data + chr(ord(i) + 13)
    new_socket.sendall(data.encode("utf-8"))
    print(data)
    print("Finish upload file from server")
    file.close()
    
    

def receivedFile(new_socket):
    filename = new_socket.recv(1024).decode("utf-8")
    print("receiving file")
    finalfilename = os.path.basename(filename)
    print(finalfilename + "\n")
    file = open(finalfilename, "w")
    data = new_socket.recv(1024).decode("utf-8")
    file.write(data)
    #print(data)
    file.close()
    """ 
    filenameRecev, filesize = received.split(SEPARATOR)
    # remove absolute path if there is
    filename = os.path.basename(filenameRecev)
    with open(filename, "wb") as f:
        while True:
            # read 1024 bytes from the socket (receive)
            bytes_read = new_socket.recv(BUFFER_SIZE)
            if not bytes_read:
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
    """
    print("file received")

def MainHandler(new_socket, addr):
    try:
        while True:
            req_type = new_socket.recv(1).decode("utf-8")  
            print("Request type " + req_type)
            if req_type:  # If it is not true, the client is disconnected
                if req_type == "1":  # Login request
                    print("Handle Login Request")
                    LoginHandler(new_socket)
                elif req_type == "2":  # Register request
                    print("Handle Register Request")
                    RegisterHandler(new_socket)
                elif req_type == "3":  # Message request
                    print("Handle Message Request")
                    MessageHandler(new_socket)
                elif req_type == "4":  # Message request
                    print("Receive File request")
                    receivedFile(new_socket)
                elif req_type == "5": #Message request
                    print("Download File request")
                    sendFile(new_socket)
            else:
                break     
    except Exception as ret:
        print(str(addr) + "Abnormal connection , ready to disconnect: " + str(ret))
    finally:
        try:
            # After client is disconnected, do this follow 
            new_socket.close()
            OnlineSocketList.remove(new_socket)
            sendOffline_notice(new_socket)
            SocketToUser.pop(new_socket)
            time.sleep(4)
            updateOnlineList()
        except Exception as ret:
            print(str(addr) + "Connection closed abnormally")

# Driver program 
if __name__ == "__main__":
    try:
        main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        main_socket.bind(('127.0.0.1', PORT))  
        main_socket.listen(128) 
        print("Server is running on port " + str(PORT))
        while True:
            new_socket, addr = main_socket.accept()
            Thread(target=MainHandler, args=(new_socket, addr)).start()
    except Exception as ret:
        print("Server error: " + str(ret))