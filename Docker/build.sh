#!/bin/sh

set -e -E

docker build -t ansible:latest .
VERSION=$( docker run --rm -i ansible:latest rpm -q --queryformat="%{VERSION}-%{RELEASE}" ansible )
docker tag -f ansible:latest ansible:$VERSION
