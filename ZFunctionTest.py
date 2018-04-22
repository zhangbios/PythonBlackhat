import socket
import paramiko
import subprocess
import sys
import os


def main():
    localhost = 'localhost'
    port = 9000
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((localhost, port))
    server_socket.listen()
    while True:
        client,addr = server_socket.accept()
        print("{}:{} connected".format(addr[0],addr[1]))
        # print(client)
        output = client.recv(4096)
        print(output)


def GenerateNewPrivateKey():
    paramiko.RSAKey.generate(512)


def execute_command(command):
    output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    return output


def SizeOf():
    a = 'ba'
    print(sys.getsizeof(a))


def DirectoryTest():
    print(os.getcwd())
    os.chdir('D:\\')
    print(os.getcwd())
    for r,d,f in os.walk("."):
        print("{}/{}".format(r,f))


def KongHng():
    print("123456")
    print("999999")


a = 456
def ExecFun():
    a = 123
    exec('print(a)', {'a': 789}, None)
    exec('print(a)', None, {'a': 345})
    exec('print(a)', None, None)
    exec('print(a)', None, {})
    exec('print(a)', {}, None)
    exec('print(a)', {}, {})


def run(**args):
    print("[*] In dirlister module.")
    files = os.listdir(".")
    return str(files)


def run_enviroment(**args):
    print("[*] In enviroment module.")
    return str(os.environ)


if __name__ == '__main__':
    buffer = run_enviroment()
    print(buffer)