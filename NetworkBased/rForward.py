"""
    transport.reqest_port_forward
    SSH 隧道
"""
import optparse
import getpass
import paramiko
import socket
import sys
import select
import threading

g_verbose = True
DEFAULT_PORT = 4000

def get_host_port(spec, default_port):
    args = (spec.split(":", 1) + [default_port])[:2]
    host = args[0]
    port = int(args[1])
    return host,port

def verbose(s):
    if g_verbose:
        print(s)

def parse_options():
    Usage = "usage: %prog [options]<server>[:<server-port>]"
    Ver = "%prog 1.0"
    Help = "Usage: rForward.py 192.168.0.123 -p 8080 --user justin --password -r 10.10.10.251:80"
    parser = optparse.OptionParser(Usage, version=Ver, description=Help)
    parser.add_option('-q', '--quiet', action='store_false', dest='verbose', default=True,
                      help='squelch all informational output')
    parser.add_option('-p', '--remote-port', action='store', type='int', dest='port',
                      default=DEFAULT_PORT, help='port on server to forward (default: %d)')
    parser.add_option('-u', '--user', action='store', type='string', dest='user',
                      default=getpass.getuser(), help='username for SSH authentication (default: %s)' % getpass.getuser())
    parser.add_option('-K', '--key', action='store', type='string', dest='keyfile',
                      default=None, help='private key file to use for SSH authentication')
    parser.add_option('', '--no-key', action='store_false', dest='look_for_keys', default=True,
                      help='don\'t look for or use a private key file')
    parser.add_option('-P', '--password', action='store_true', dest='readpass', default=False,
                      help='read password (for key or password auth) from stdin')
    parser.add_option('-r', '--remote', action='store', type='string', dest='remote',
                      default=None, metavar='host:port', help='remote host and port to forward to')

    options, args = parser.parse_args()

    server_host,server_port = get_host_port(args[0], 22)
    remote_host,remote_port = get_host_port(options.remote, 22)
    g_verbose = options.verbose
    return options, (server_host, server_port), (remote_host, remote_port)

def reverse_forward_tunnel(server_port, remote_host, remote_port, transport):
    transport.request_port_forward("", server_port)
    while True:
        chan = transport.accept(100)
        if chan is None:
            continue
        thr = threading.Thread(target=handler, args=(chan, remote_host, remote_port))
        thr.setDaemon(True)
        thr.start()

def handler(chan, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host,port))
    except Exception as e:
        verbose("Forwarding request to {}:{} failed{}".format(host, port, e))
        return

    verbose("Connected! tunnel open {} -> {} -> {}".format(chan.origin_addr,
                                                           chan.getpeername(), (host,port)))
    while True:
        r,w,x = select.select([sock, chan], [], [])
        if sock in r:
            data = sock.recv(1024)
            if len(data) == 0:
                break
            sock.send(data)
        if chan in r:
            data = chan.recv(1024)
            if len(data) == 0:
                break
            chan.send(data)
    chan.close()
    sock.close()
    verbose("tunnel closed from {}!".format(chan.origin_addr,))

def main():
    option, server, remote = parse_options()

    password = None
    if option.readpass:
        password = getpass.getpass("Enter SSH password:")

    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    verbose("Connecting to ssh host {}:{}...".format(server[0],server[1]))
    try:
        client.connect(hostname=server[0], port=server[1], username=option.user, key_filename=option.keyfile,
                       look_for_keys=option.look_for_keys, password=password)
    except Exception as  e:
        print("**** Failed to connect to {}:{} {} !".format(server[0], server[1], e))
        sys.exit(1)

    verbose("Now forwarding remote port {} to {}:{}!".format(option.port, remote[0], remote[1]))

    try:
        reverse_forward_tunnel(option.port, remote[0], remote[1], client.get_transport())
    except KeyboardInterrupt:
        print("port forwarding stopped!")
        sys.exit(0)


if __name__ == '__main__':
    main()