#!/bin/sh

MYSELF=$(realpath $0)
DIRNAME=$(dirname $MYSELF)
DIR=$(realpath $DIRNAME/..)
docker run --rm --name ansible -v $HOME:/home/ansible:Z -v "$DIR":/tmp/ansible:z -it --workdir=/tmp/ansible ansible:latest
