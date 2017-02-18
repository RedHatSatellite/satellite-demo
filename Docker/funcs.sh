#!/bin/sh

info() {
  echo "[INFO]" "$@" 1>&2
}

warn() {
  echo "[WARN]" "$@" 1>&2
}

err() {
  echo "[ERROR]" "$@" 1>&2
  exit 1
}

assign_docker_command() {
  which docker > /dev/null 2>&1 || err "You must have docker installed to build a docker image!"

  DOCKER=$(which docker)

  if ! docker ps > /dev/null 2>&1 ; then
    warn "Unable to execute the docker command."
    if ! systemctl status docker 2>&1 | fgrep -q 'Active: active' ; then
      warn "Doesn't look like docker is running!"
      err $"Please start it:
    $ systemctl start docker
    $ systemctl enable docker
"
    fi
    warn "Trying with sudo."
    warn "If you're a sudoer, please enter your password if asked."
    if ! sudo docker ps > /dev/null 2>&1 ; then
      warn "Sudo didn't work. I'm not sure how to run docker as this user on your system."
      err "Sorry."
    fi

    DOCKER="sudo $DOCKER"
  fi
}
