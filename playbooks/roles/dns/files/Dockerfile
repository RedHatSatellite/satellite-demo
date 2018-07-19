# vim: sw=16 ts=16 expandtab
FROM            fedora:28
MAINTAINER      Billy Holmes <billy@gonoph.net>
COPY            certserv.py /container-entrypoint
COPY            ca.crt /data/ca.crt
ENV             PYTHONUNBUFFERED=TRUE
ENTRYPOINT      [ "/usr/bin/python3", "/container-entrypoint" ]
CMD             [ "/data/ca.crt", "8080" ]
