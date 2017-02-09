#!/usr/bin/env python
# vim: sw=4 ai ts=4 expandtab
import sys, traceback, copy
from socket import socket, AF_INET, SOCK_STREAM
from OpenSSL.SSL import Context, Connection, TLSv1_METHOD
from OpenSSL.crypto import FILETYPE_PEM, dump_certificate

ret=dict(
        failed=False,
        changed=True,
        )

def main():
    def err_exit(ret, msg):
        ret['failed']=True
        ret['msg']=msg
        module.fail_json(**ret)

    module = AnsibleModule(
        argument_spec=dict(
            host=dict(required=True, type='str'),
            certificates=dict(required=True, type='dict'),
            ),
    )

    host = module.params['host']
    certificates = copy.copy(module.params['certificates'])
    split=host.split(':')
    split.reverse()
    host=split.pop()
    ret['host']=host
    ret['port']=None
    ret['downloaded']=False
    ret['ansible_facts']=dict(certificates=certificates)

    try:
        port=int(split.pop()) if split else 443
        hostport="{}:{}".format(host, port)
        ret['port']=port

        if host in certificates and hostport not in certificates:
            certificates[hostport]=certificates[host]

        if hostport not in certificates or certificates[hostport] is None:
            s = socket(AF_INET, SOCK_STREAM)
            ctx = Context(TLSv1_METHOD )
            con = Connection(ctx, s)
            con.connect((host, port))
            con.do_handshake()
            x509 = con.get_peer_cert_chain()[-1]
            con.shutdown()
            con.close()
            ret['downloaded']=True
            certificates[hostport]=dump_certificate(FILETYPE_PEM, x509)
            if host not in certificates or certificates[host] is None:
                certificates[host]=certificates[hostport]

        module.exit_json(**ret)
    except Exception as e:
        msg_=traceback.format_exc()
        module.fail_json(msg="{}: {}".format(repr(e), msg_))

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
