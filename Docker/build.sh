#!/bin/sh

if ! which docker 2>&1 > /dev/null ; then
  echo "You must have docker installed to build a docker image!"
  exit 1
fi

DOCKER=$(which docker)

if ! docker ps 2>&1 > /dev/null ; then
  echo "Unable to execute the docker command."
  if ! systemctl status docker | fgrep -q 'Active: active' ; then
    echo "Doesn't look like docker is running!"
    echo $"Please start it:
  $ systemctl start docker
  $ systemctl enable docker
"
    exit 1
  fi
  echo "Trying with sudo, if you're a sudoer, please enter your password if asked."
  if ! sudo docker ps 2>&1 > /dev/null ; then
    echo "Sudo didn't work. I'm not sure how to run docker as this user on your system."
    echo "Sorry."
    exit 1
  fi

  DOCKER="sudo $DOCKER"
fi

IMAGE_USER=ansible
if [ $UID = 0 ] ; then
  echo "The bootstrap container will be running as root. It's not recommended, but sure - let's do THIS"
  IMAGE_USER=root
fi

set -e -E

if [ "x$IMAGE_USER" = "xroot" ] ; then
  echo "Removing references to non-root user"
  sed -e "/123456789/d" -e '/^USER/d' Dockerfile.in > Dockerfile.tmp
else
  echo "Building image to run as user UID($UID)"
  sed -e "s/123456789/$UID/" Dockerfile.in > Dockerfile.tmp
fi

# this seems to be pretty global on *unix
NEW_SUM=$(sum Dockerfile.tmp)
[ -r Dockerfile ] && OLD_SUM=$(sum Dockerfile) || OLD_SUM=X

if [ "$NEW_SUM" != "$OLD_SUM" ] ; then
  mv -f Dockerfile.tmp Dockerfile
else
  echo "No changes to existing Dockerfile..."
  rm -f Dockerfile.tmp
fi

docker build -t ansible:latest .
VERSION=$( docker run --rm -i ansible:latest rpm -q --queryformat="%{VERSION}-%{RELEASE}" ansible )
docker tag -f ansible:latest ansible:$VERSION
