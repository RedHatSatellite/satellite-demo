#!/bin/bash

host=$1
port=$2

: ${port:=443}
: ${host:=localhost}

## this command does the following:
# echo - force the webserver to end it's conversation with us
# openssl s_client - start openssl in client mode
# + showcerts - show all the certs in the chain - even the self signed one
# + servername - give the server name in case of SNI (shared SSL)
# + connect - the host and port to connect
# sed - -n means to suppress output
# + 1st - APPEND the edges of BEGIN and END cert pem format into the hold space
# + 2nd - on the ssl "issuer" line, REPLACE the hold space with that line,
# ++ - then swap the hold and pattern space, then delete the pattern space
# + 3rd - on the last line, swap the pattern and hold space, then print it
##### why?
# If the server response with a long list of certs, the last cert will be the
# CA cert. Thus, everytime the server responds with a new cert in the chain, we
# swap the hold space with this new cert, and finally just print the last cert
# in the hold space. Since the last cert is always the CA cert, poof - we get
# the CA cert everytime.
##
echo | openssl s_client -showcerts -servername $host -connect $host:$port | \
sed -n \
-e '/BEGIN CERTIFICATE/,/END CERTIFICATE/{H;}' \
-e '/^   i:/{h;x;d;}' \
-e '${x;p;}' | openssl x509 -text
