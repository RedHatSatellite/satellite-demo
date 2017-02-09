#!/usr/bin/env python

if __name__ == '__main__':
    import getca
    raise SystemExit(getca.main())

from socket import socket, AF_INET, SOCK_STREAM
from OpenSSL.SSL import Context, Connection, TLSv1_METHOD
from OpenSSL.crypto import FILETYPE_PEM, dump_certificate
import sys,os,datetime

def xjoin(list_of_lists):
    return ",".join(map(lambda x: "=".join(x), list_of_lists))

def datestr(dt):
    try:
        return str(datetime.datetime.strptime(dt, "%Y%m%d%H%M%SZ"))
    except:
        return str(dt)

FMT="""i: {}
s: {}
Valid
    Not Before: {}
    Not After : {}"""

def walkchain(cert_chain):
    chain = cert_chain
    x509 = None
    for cert in chain:
        x509 = cert
        print FMT.format(
        xjoin(x509.get_issuer().get_components()),
        xjoin(x509.get_subject().get_components()),
        datestr(x509.get_notBefore()),
        datestr(x509.get_notAfter()))
    return x509

def printcert(host, port, hostname):
    con = Connection(Context(TLSv1_METHOD), socket(AF_INET, SOCK_STREAM))
    con.connect((host, port))
    con.set_tlsext_host_name(hostname if hostname else host)
    con.do_handshake()
    con.shutdown()
    con.close()
    print dump_certificate(FILETYPE_PEM, walkchain(con.get_peer_cert_chain()))

def main():
    args = sys.argv
    args.reverse()
    prog = args.pop()

    if len(args) < 1:
        print "Usage {} host[:port]" \
            " [hostname if different from host]".format(os.path.basename(prog))
        sys.exit(1)

    split = args.pop().split(':')[::-1]
    host = split.pop()
    port = int(split.pop()) if split else 443
    hostname = args.pop() if args else None

    printcert(host, port, hostname)
