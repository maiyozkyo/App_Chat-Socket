from tkinter import *
from tkinter import messagebox
from tkinter import  filedialog
from threading import Thread
import socket
import time
import re
import os
import tqdm
import pickle

SEPARATOR = "<SEPARATOR>"
BUFFER_SIZE = 1024

class Panel:
    def __init__(self):
        self.username = None
        self.password = None

    def setPanelPosition(self, width, height):
        screenWidth = self.Frame.winfo_screenwidth()
        screenHeight = self.Frame.winfo_screenheight()
        self.width = width
        self.height = height
        gm_str = "%dx%d+%d+%d" % (width, height, (screenWidth - width) / 2, (screenHeight - 1.2 * height) / 2)
        self.Frame.geometry(gm_str)

    def configRegPanel(self,name):
        self.name = name
        self.Frame.configure(background="#9999FF")
        self.Frame.resizable(width=False, height=False)
        self.Frame.title(name)

    def setTitle(self, title):
        self.title = title
        titleLabel = Label(self.Frame, text=title, font=("Microsoft Yahei", 16), fg="black", bg="pink")
        titleLabel.pack(ipady=10, fill=X)
    
    def setForm(self):
        pass

    def setBtn(self, func1, func2):
        self.func1 = func1
        self.func2 = func2
        btnFrame = Frame(self.Frame, bg="#9999FF")
        btnReg = Button(btnFrame, text="Register", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.func1)
        btnReg.pack(side=LEFT, ipady=3)

        btnLogin = Button(btnFrame, text="Login", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.func2)
        btnLogin.pack(side=RIGHT, ipady=3)
        btnFrame.pack(fill=X, padx=20, pady=20)
    

    def show(self):
        self.setPanelPosition()
        self.configRegPanel()
        self.setTitle()
        self.setForm()
        self.setBtn()
        self.Frame.mainloop()

    def close(self):
        if self.Frame == None:
            print("No interface displayed")
        else:
            self.Frame.destroy()

    def getInput(self):
        pass
    
class Client:
    def __init__(self):
        print("Initialize multi-person chat room client")
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect(('127.0.0.1', 7890))

    def sendLoginInfo(self, username, password):

        self.clientSocket.sendall("1".encode("utf-8"))

        username_psw = username + "#!#!" + password
        self.clientSocket.sendall(username_psw.encode("utf-8"))

        checkResult = self.clientSocket.recv(1024).decode("utf-8")
        return checkResult

    def sendRegisterInfo(self, username, password, confirm):

        if not password == confirm:
            return "Password is incorrect, please try again！"

        self.clientSocket.sendall("2".encode("utf-8"))

        username_psw = username + "#!#!" + password
        self.clientSocket.sendall(username_psw.encode("utf-8"))

        checkResult = self.clientSocket.recv(1024).decode("utf-8")
        return checkResult

    def sendMessage(self, content):
        self.clientSocket.sendall("3".encode("utf-8"))
        self.clientSocket.sendall(content.encode("utf-8"))

    def recv_data(self, size=1024):
        return self.clientSocket.recv(size).decode("utf-8")

    def receiveFile(self, file_path):
        self.clientSocket.sendall("5".encode("utf-8"))
        self.clientSocket.send(str(file_path).encode("utf-8"))
        decode = ""
        decode = self.clientSocket.recv(1024).decode("utf-8")
        data = ""
        for i in decode:
            data = data + chr(ord(i) - 13)
        file_path = filedialog.asksaveasfilename()
        if not file_path:
            return 
        file = open(file_path, "w")
        print("Downloading...")
        print(data)
        file.write(data)
        file.close()
        print("Successfully")


    def sendfile(self, file_path):
        self.clientSocket.sendall("4".encode("utf-8"))
        print("Sending file: ")

        """ 
        self.clientSocket.send(f"{file_path}{SEPARATOR}{filesize}".encode())
        with open(file_path, "rb") as f:
            while True:
                # read the bytes from the file
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    # file transmitting is done
                    break
                # we use sendall to assure transimission in
                # busy networks
                self.clientSocket.sendall(bytes_read)
        """

        # open & reading file
        filename = open(file_path,"r")
        data = filename.read()
        # send filename
        self.clientSocket.send(file_path.encode("utf-8"))
        # send data
        self.clientSocket.send(data.encode("utf-8"))
        print(data)
        filename.close()

        print("Finish upload")
        

    def close(self):
        self.clientSocket.close()


class LoginPanel(Panel):
    def __init__(self):
        self.Frame =  Tk()
        super().__init__

    def setPanelPosition(self):
        super().setPanelPosition(400,300)

    def configRegPanel(self):
        super().configRegPanel("Login")

    def setTitle(self):
        super().setTitle("Chat with me - Login")

    def setForm(self):
        formFrame = Frame(self.Frame, bg="#9999FF")
        formFrame.pack(fill=X, padx=20, pady=10)

        Label(formFrame, text="Username：", font=("Microsoft Yahei", 12), bg="#9999FF", fg="black").grid(row=0, column=3, pady=20)
        Label(formFrame, text="Password：", font=("Microsoft Yahei", 12), bg="#9999FF", fg="black").grid(row=1, column=3, pady=20)

        self.username = StringVar()
        self.password = StringVar()
        Entry(formFrame, textvariable=self.username, bg="#e3e3e3", width=30).grid(row=0, column=4, ipady=1)
        Entry(formFrame, textvariable=self.password, show="*", bg="#e3e3e3", width=30).grid(row=1, column=4, ipady=1)

    def setBtn(self):
        btnFrame = Frame(self.Frame, bg="#9999FF")
        btnReg = Button(btnFrame, text="Register", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.regFunc)
        btnReg.pack(side=LEFT, ipady=3)

        btnLogin = Button(btnFrame, text="Login", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.loginFunc)
        btnLogin.pack(side=RIGHT, ipady=3)
        btnFrame.pack(fill=X, padx=20, pady=20)

    def show(self):
        super().show()

    def close(self):
        super().close()

    def getInput(self):
        return self.username.get(), self.password.get()

    def loginFunc(self):
        username, password = self.getInput()
        client = Client()
        checkResult = client.sendLoginInfo(username, password)
        if checkResult == "Login successfully！":
            messagebox.showinfo(title="Success", message="Login successfully！")
            self.close()
            mainPanel = MainPanel(username, client)
            Thread(target=mainPanel.handleMessage).start()
            mainPanel.show()
        elif checkResult == "Password is incorrect, please try again！":
            messagebox.showerror(title="Error", message="Password is incorrect, please try again！")
        elif checkResult == "The user does not exist, please register first！":
            messagebox.showerror(title="Error", message="The user does not exist, please register first！")

    def regFunc(self):
        self.close()
        regPanel = RegPanel()
        regPanel.show()


class RegPanel(Panel):
    def __init__(self):
        self.Frame =  Tk()
        super().__init__
        self.confirm = None

    def setPanelPosition(self):
        super().setPanelPosition(400,360)

    def configRegPanel(self):
        self.Frame.protocol("WM_DELETE_WINDOW", self.closeCallback)
        super().configRegPanel("Register")

    def setTitle(self):
        super().setTitle("Chat with me - Register")

    def setForm(self):
        formFrame = Frame(self.Frame, bg="#9999FF")
        formFrame.pack(fill=X, padx=20, pady=10)

        Label(formFrame, text="Username：", font=("Microsoft Yahei", 12), bg="#9999FF", fg="black").grid(row=0, column=1, pady=20)
        Label(formFrame, text="Password：", font=("Microsoft Yahei", 12), bg="#9999FF", fg="black").grid(row=1, column=1, pady=20)
        Label(formFrame, text=" Confirm：", font=("Microsoft", 12), bg="#9999FF", fg="black").grid(row=2, column=1, pady=20)

        self.username = StringVar()
        self.password = StringVar()
        self.confirm = StringVar()

        Entry(formFrame, textvariable=self.username, bg="#e3e3e3", width=30).grid(row=0, column=2, ipady=1)
        Entry(formFrame, textvariable=self.password, show="*", bg="#e3e3e3", width=30).grid(row=1, column=2, ipady=1)
        Entry(formFrame, textvariable=self.confirm, show="*", bg="#e3e3e3", width=30).grid(row=2, column=2, ipady=1)

    def setBtn(self):
        btnFrame = Frame(self.Frame, bg="#9999FF")
        btn_quit = Button(btnFrame, text="Cancel", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.quit_func)
        btn_quit.pack(side=LEFT, ipady=3)

        btnReg = Button(btnFrame, text="Register", bg="pink", fg="black", width=15, font=('Microsoft Yahei', 12), command=self.regFunc)
        btnReg.pack(side=RIGHT, ipady=3)
        btnFrame.pack(fill=X, padx=20, pady=20)

    def show(self):
        super().show()

    def close(self):
        super().close()

    def getInput(self):
        return self.username.get(), self.password.get(), self.confirm.get()

    def quit_func(self):
        self.close()
        loginPanel = LoginPanel()
        loginPanel.show()

    def regFunc(self):
        username, password, confirm = self.getInput()
        client = Client()
        ret = client.sendRegisterInfo(username, password, confirm)
        print(ret)
        if ret == "Password is incorrect, please try again！":
            messagebox.showerror(title="Error", message="Password is incorrect, please try again！")
        else:
            if ret == "Sorry, username already exists！":
                messagebox.showerror(title="Error", message="Sorry, username already exists! ")
            elif ret == "Register successfully! ":
                messagebox.showinfo(title="Success", message="Register successfully! ")
                self.close()
                loginPanel = LoginPanel()
                loginPanel.show()
            else:
                messagebox.showerror(title="Error", message="An unknown error occurred！")

    def closeCallback(self):
        self.close()
        loginPanel = LoginPanel()
        loginPanel.show()

class MainPanel:
    def __init__(self, username, client):
        print("Initialize the main interface")
        self.mainFrame = Tk()
        self.client = client
        self.username = username
        self.onlineListBox = None
        self.messageBox = None
        self.inputBox = None

    def setPanelPosition(self):
        width = 800
        height = 500
        screenWidth = self.mainFrame.winfo_screenwidth()
        screenHeight = self.mainFrame.winfo_screenheight()
        gm_str = "%dx%d+%d+%d" % (width, height, (screenWidth - width) / 2, (screenHeight - 1.2 * height) / 2)
        self.mainFrame.geometry(gm_str)
        self.mainFrame.minsize(width, height) 

    def configMainPanel(self):
        self.mainFrame.title("MyChat")
        self.mainFrame.configure(background="pink")

        self.mainFrame.protocol("WM_DELETE_WINDOW", self.closeCallback)
        self.mainFrame.rowconfigure(1, weight=1)
        self.mainFrame.columnconfigure(1, weight=1)

    def setOnlineList(self):
        online_list_var = StringVar() 
        self.onlineListBox = Listbox(self.mainFrame, selectmode=NO, listvariable=online_list_var, bg="#9999FF", fg="Green", font=("Microsoft Yahei", 14), highlightcolor="white")
        self.onlineListBox.grid(row=1, column=0, rowspan=3, sticky=N + S, padx=10, pady=(0, 5))

        list_sr_bar = Scrollbar(self.mainFrame)
        list_sr_bar.grid(row=1, column=0, sticky=N + S + E, rowspan=3, pady=(0, 5))

        list_sr_bar['command'] = self.onlineListBox.yview
        self.onlineListBox['yscrollcommand'] = list_sr_bar.set

    def SetMessageBox(self):
        msg_sr_bar = Scrollbar(self.mainFrame)
        msg_sr_bar.grid(row=1, column=1, sticky=E + N + S, padx=(0, 10))

        self.messageBox = Text(self.mainFrame, bg="#9999FF", height=1, highlightcolor="white", highlightthickness=1)

        self.messageBox.config(state=DISABLED)
        self.messageBox.tag_configure('greencolor', foreground='green')
        self.messageBox.tag_configure('bluecolor', foreground='blue')
        self.messageBox.grid(row=1, column=1, sticky=W + E + N + S, padx=(10, 30))

        msg_sr_bar["command"] = self.messageBox.yview
        self.messageBox["yscrollcommand"] = msg_sr_bar.set

    def setInputBox(self):
        send_sr_bar = Scrollbar(self.mainFrame)
        send_sr_bar.grid(row=2, column=1, sticky=E + N + S, padx=(0, 10), pady=10)

        self.inputBox = Text(self.mainFrame, bg="#9999FF", height=5, highlightcolor="white", highlightbackground="#fff", highlightthickness=3)
        self.inputBox.see(END)
        self.inputBox.grid(row=2, column=1, sticky=W + E + N + S, padx=(10, 30), pady=10)

        send_sr_bar["command"] = self.inputBox.yview
        self.inputBox["yscrollcommand"] = send_sr_bar.set

    def setBtn(self):
        Button(self.mainFrame, text="Send", bg="green", font=("Microsoft Yahei", 14), fg="black", command=self.sendFunc).grid(row=3, column=1, pady=5, padx=10, sticky=W, ipady=3, ipadx=10)
        Button(self.mainFrame, text="Clear", bg="red", font=("Microsoft Yahei", 14), fg="black", command=self.clearInputBox).grid(row=3, column=1, pady=5, sticky=W, padx=(110, 0), ipady=3, ipadx=10)
        Button(self.mainFrame, text="Log out", bg="#B8E238", font=("Microsoft Yahei", 14), fg="black", command=self.Logout).grid(row=3, column=1, pady=5, sticky=W, padx=(400, 0), ipady=3, ipadx=10)
        Button(self.mainFrame, text="Upload", bg="blue", font=("Microsoft Yahei", 14), fg="black", command=self.upload).grid(row=3, column=1, pady=5, padx=(210,0), sticky=W, ipady=3, ipadx=10)
        Button(self.mainFrame, text="Download", bg="blue", font=("Microsoft Yahei", 14), fg="black", command=self.download).grid(row=4, column=1, pady=5, padx=(210,0), sticky=W, ipady=3, ipadx=10)


    def show(self):
        self.setPanelPosition()
        self.configMainPanel()

        Label(self.mainFrame, text="MyChat：" + self.username, font=("Microsoft Yahei", 13), bg="pink", fg="black").grid(row=0, column=0, ipady=10, padx=10, columnspan=2, sticky=W)
        self.setOnlineList()
        self.SetMessageBox()
        self.setInputBox()
        self.setBtn()

        self.mainFrame.mainloop()

    def download(self):
        self.mainFrame.withdraw
        file_path = filedialog.askopenfilename()
        self.client.receiveFile(file_path)

    def upload(self):
        self.mainFrame.withdraw
        file_path = filedialog.askopenfilename()
        self.client.sendfile(file_path)

    def handleMessage(self):
        time.sleep(2)
        while True:
            try:
                recv_data = self.client.recv_data()
                if recv_data:
                    ret = re.match(r"(#![\w]{7}#!)([\s\S]+)", recv_data)
                    option = ret.group(1)
                    print(">>received type: " + option)
                    print(">>received data: " + recv_data)
                    if option == "#!onlines#!":
                        print("--Get online user list data")
                        online_usernames = ret.group(2).split("#!")
                        online_usernames.remove("")  
                        print(online_usernames)
                        self.updateOnlineList(online_usernames)
                        print(online_usernames)
                    elif option == "#!message#!":  
                        print("--Get new message\n")
                        username_content = ret.group(2)
                        ret = re.match(r"(.*)#!([\s\S]*)", username_content)
                        username = ret.group(1)
                        content = ret.group(2)
                        self.setMessage_showFormat(username, content)
                    elif option == "#!notices#!":
                        print("--Get online and offline users notifications")
                        notice = ret.group(2)  
                        self.showNotice(notice)

            except Exception as ret:
                print("Error occurred while receiving server message, receiving sub-thread ends " + str(ret))
                break

    def updateOnlineList(self, online_usernames):
        print("Updating user list...")
        self.onlineListBox.delete(0, END)  
        for username in online_usernames:
            self.onlineListBox.insert(0, username)

    def showNotice(self, notice):
        self.messageBox.config(state=NORMAL)  
        self.messageBox.insert(END, notice, "red")
        self.messageBox.insert(END, "\n", "red")
        self.messageBox.config(state=DISABLED)  
        self.messageBox.see(END) 

    def setMessage_showFormat(self, username, content):
        self.messageBox.config(state=NORMAL)
        title = username + " " + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n"
        if username == self.username:
            self.messageBox.insert(END, title, "blue")
        else:
            self.messageBox.insert(END, title, "black")
        self.messageBox.insert(END, content + "\n")
        self.messageBox.config(state=DISABLED)
        self.messageBox.see(END)

    def clearInputBox(self):
        self.inputBox.delete('0.0', END)

    def getInputContent(self):
        return self.inputBox.get('0.0', END)

    def sendFunc(self):
        content = self.getInputContent()
        self.client.sendMessage(content)
        self.clearInputBox()

    def Logout(self):
        print("Logged out")
        self.closeCallback()
        loginPanel = LoginPanel()
        loginPanel.show()

    def close(self):
        if self.mainFrame == None:
            print("No interface displayed! ")
        else:
            self.mainFrame.destroy()

    def closeCallback(self):
        self.client.close()
        self.close()

# Driver program 
if __name__ == "__main__":
    loginPanel = LoginPanel()
    loginPanel.show()

