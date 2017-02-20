#!/bin/sh

MYSELF=$(realpath $0)
DIRNAME=$(dirname $MYSELF)
DIR=$(realpath $DIRNAME/..)

. $DIRNAME/funcs.sh

assign_docker_command

IMAGE_USER=ansible
if [ $UID = 0 ] ; then
  info "The bootstrap container will be running as root. It's not recommended, but sure - let's do THIS"
  IMAGE_USER=root
fi

set -e -E

if [ "x$IMAGE_USER" = "xroot" ] ; then
  info "Removing references to non-root user"
  sed -e "/::REPLACE_UID::/d" -e '/^USER/d' -e "s/::REPLACE_REPO::/$REPO/" Dockerfile.in > Dockerfile.tmp
else
  info "Building image to run as user UID($UID)"
  sed -e "s/::REPLACE_UID::/$UID/" -e "s/::REPLACE_REPO::/$REPO/" Dockerfile.in > Dockerfile.tmp
fi

# this seems to be pretty global on *unix
NEW_SUM=$(sum Dockerfile.tmp)
[ -r Dockerfile ] && OLD_SUM=$(sum Dockerfile) || OLD_SUM=X

if [ "$NEW_SUM" != "$OLD_SUM" ] ; then
  mv -f Dockerfile.tmp Dockerfile
else
  info "No changes to existing Dockerfile..."
  rm -f Dockerfile.tmp
fi

# Docker 1.12 appears not to have the force flag anymore
docker tag -f 2>&1 | fgrep -q 'unknown shorthand flag' && TAGF="" || TAGF="-f"

$DOCKER build -t ansible:latest .
VERSION=$( $DOCKER run --rm -i ansible:latest rpm -q --queryformat="%{VERSION}-%{RELEASE}" ansible )
$DOCKER tag $TAGF ansible:latest ansible:$VERSION
