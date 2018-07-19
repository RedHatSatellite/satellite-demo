#!/usr/bin/env python
# vim: sw=4 ts=4 ai expandtab
from __future__ import print_function
"""
Certserv in python
"""

HELP="""

Usage::
    ./certserv.py /path/to/cafile.crt [<port>]

Send a GET request::
    curl http://localhost

"""

try:
    # for python2
    from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
except ModuleNotFoundError:
    # for python3
    from http.server import BaseHTTPRequestHandler, HTTPServer

from sys import stderr, stdout
from signal import signal, SIGTERM, SIGINT
from subprocess import PIPE, Popen
from hashlib import sha256
import re

def handler(signum, frame):
    print("Caught signal %d, Exiting now..." % signum, file=stderr)
    exit(signum)

class CertData(object):
    def __init__(self):
        self.started = False
        self.data = ''

class CertReadException(IOError):
    pass

def encode(s):
    return s.encode('latin1')

def toint(s):
    try:
        return int(s)
    except ValueError:
        return -1

def tohash(s):
    return sha256(encode(s)).hexdigest()

class CertServ(BaseHTTPRequestHandler):
    def _set_idx_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.send_header('Content-length', len(INDEX))
        self.end_headers()

    def _set_cert_headers(self, idhash):
        if idhash not in CERT_DATA:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', len(encode(ERROR404)))
            self.end_headers()
            return None

        cert = CERT_DATA[idhash]
        self.send_response(200)
        self.send_header('Content-type', 'application/x-x509-ca-cert')
        self.send_header('Content-length', len(encode(cert)))
        self.end_headers()
        return cert

    def do_GET(self):
        path = re.sub('^/ca/', '/', self.path)

        if '/' == path:
            self._set_idx_headers()
            self.wfile.write(encode(INDEX))
        else:
            idhash = path[1:]
            cert = self._set_cert_headers(idhash)
            if cert is None:
                self.wfile.write(encode(ERROR404))
            else:
                self.wfile.write(encode(cert))

    def do_HEAD(self):
        path = re.sub('^/ca/', '/', self.path)

        if '/' == path:
            self._set_idx_headers()
        else:
            idhash = path[1:]
            cert = self._set_cert_headers(idhash)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Content-type', 'httpd/unix-directory')
        self.send_header('Content-length', 0)
        self.send_header('Allow', 'GET,OPTIONS,HEAD')
        self.end_headers()
        
def run(server_class=HTTPServer, handler_class=CertServ, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print('Starting certserv on port %d...' % port, file=stderr)
    httpd.serve_forever()

CERT_DATA=dict()
INDEX=''
ERROR404='Unable to find certifiate\n'

if __name__ == "__main__":
    from sys import argv

    if len(argv) < 2:
        print(HELP, file=stderr)
        exit(1)

    with open(argv[1], 'r') as f:
        cert=None
        for line in f:
            if cert is None:
                cert = CertData()
            if cert.started:
                cert.data += line
                if '-----END CERTIFICATE-----' == line.strip():
                    p = Popen([ 'openssl', 'x509', '-issuer', '-subject', '-noout' ],
                            stdout=PIPE,
                            stdin=PIPE,
                            stderr=PIPE)
                    out, err = p.communicate(encode(cert.data))
                    err = err.decode()
                    out = out.decode()

                    if len(err):
                        raise CertReadException(err)

                    CERT_DATA[out] = out + cert.data
                    cert=None
            else:
                if '-----BEGIN CERTIFICATE-----' == line.strip():
                    cert.data += line
                    cert.started = True

    signal(SIGTERM, handler)
    signal(SIGINT, handler)

    print("Read in {} certificates.".format(len(CERT_DATA)), file=stderr)

    INDEX="""<!DOCTYPE html>
<html><head><title>CertServ</title></head><body>
<h1>List of Certs</h1>
<table>
"""

    HASHED_CERT_DATA=dict()
    HASHED_CERT_DATA.update(CERT_DATA)
    for k in CERT_DATA:
        h = tohash(k)
        INDEX+='<tr><td><a href="{}">X</a></td><td><a href="{}"><pre>{}</pre></a></td></tr>\n'.format(h, h, k)
        HASHED_CERT_DATA[h] = CERT_DATA[k]

    INDEX+="</table></body></html>\n"

    CERT_DATA = HASHED_CERT_DATA

    if len(argv) > 2:
        run(port=int(argv[2]))
    else:
        run()
