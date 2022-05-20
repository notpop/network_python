# cli library
import argparse
import locale
import os
import socket
import shlex
import subprocess
import sys
import textwrap
import threading

def execute(cmd):
    cmd = cmd.strip()
    if not cmd:
        return
    
    if os.name == "nt":
        shell = True
    else:
        shell = False
    
    output = subprocess.check_output(shlex.split(cmd), stderr=subprocess.STDOUT, shell=shell)

    if locale.getdefaultlocale() == ('ja_JP', 'cp932'):
        return output.decode('cp932')
    else:
        return output.decode()

class NetCat:
    def __init__(self, args, buffer=None):
        self.args = args
        self.buffer = buffer
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    def send(self):
        self.socket.connect((self.args.target, self.args.port))
        if self.buffer:
            self.socket.send(self.buffer)

        try:
            while True:
                recv_len = 1
                response = ''
                while recv_len:
                    data = self.socket.recv(4096)
                    recv_len = len(data)
                    response += data.decode()
                    if recv_len < 4096:
                        break
                if response:
                    print(response)
                    buffer = input('> ')
                    buffer += '\n'
                    self.socket.send(buffer.encode())
        except KeyboardInterrupt:
            print('User terminated.')
            self.socket.close()
            sys.exit()
        except EOFError as e:
            print(e)
    
    def run(self):
        if self.args.listen:
            self.listen()
        else:
            self.send()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='BHP Net Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            '''example:
            # launch communicate command shell
            netcat.py -t 192.168.1.108 -p 5555 -l -c
            # upload to file
            netcat.py -t 192.168.1.108 -p 5555 -l -u=mytest.txt
            # execute command
            netcat.py -t 192.168.1.108 -p 5555 -l -e=\"cat /etc/passwd\"
            # send string to port on address
            echo 'ABC' | ./netcat.py -t 192.168.1.108 -p 135
            # connection to server
            netcat.py -t 192.168.1.108 -p 5555
            '''
        )
    )

    parser.add_argument('-c', '--command', action='store_true', help='initialize to communicate shell')
    parser.add_argument('-e', '--execute', help='execute command')
    parser.add_argument('-l', '--listen', action='store_true', help='listen')
    parser.add_argument('-p', '--port', type=int, default=5555, help='select to port')
    parser.add_argument('-t', '--target', default='192.168.1.203', help='select to IP address')
    parser.add_argument('-u', '--upload', help='upload to file')

    args = parser.parse_args()
    if args.listen:
        buffer = ''
    else:
        buffer = sys.stdin.read()
    
    nc = NetCat(args, buffer.encode())
    nc.run()

