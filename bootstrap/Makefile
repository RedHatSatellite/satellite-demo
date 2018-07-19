.PHONY: all build clean run
MAKEFILE_DIR:=$(dir $(realpath $(lastword $(MAKEFILE_LIST))))

DOCKERFILE?=Dockerfile
DOCKER_LABEL?=localhost/demo-ansible:latest
CONTAINER_NAME?=demo-ansible

MOTD=files/etc/motd

all: build

TEST_NEEDS_SUDO:=$(shell docker ps > /dev/null 2>&1 && echo no || echo yes)

ifeq ($(TEST_NEEDS_SUDO),yes)
SUDO:=sudo
else
SUDO:=
endif

build: $(DOCKERFILE)
	$(SUDO) docker build -t $(DOCKER_LABEL) -f $(DOCKERFILE) .

GID=$(shell id -g)
UID=$(shell id -u)
USER=$(shell id -u -n)

$(MOTD): Makefile
	sed -n '/^### Playbooks/,/^Variables/p' ../README.md  | head -n -1 > files/etc/motd

$(DOCKERFILE): $(DOCKERFILE).template $(MOTD) Makefile
	sed -e "s,%%GID%%,$(GID)," -e "s,%%UID%%,$(UID)," -e "s,%%USER%%,$(USER)," $(DOCKERFILE).template > $(DOCKERFILE)

clean: $(DOCKERFILE).template
	rm -fv $(DOCKERFILE) files/etc/motd

.ONESHELL:
run: $(DOCKERFILE)
	@T=`mktemp -d`
	trap 'rm -rfv $$T' EXIT
	cp -a ~/.ssh $$T
	err() { echo "$$@" >&2; exit 1; }
	V="-v $(MAKEFILE_DIR)/..:/tmp/install:Z"
	test -r $(MAKEFILE_DIR)/aws && cp $(MAKEFILE_DIR)/aws $$T && V+=" -v $$T/aws:/etc/profile.d/aws.sh:Z"
	D_HOME=`$(SUDO) docker run --rm -i $(DOCKER_LABEL) /bin/sh -c 'echo $$HOME'`
	test -z "$$D_HOME" && err 'Unable to determine docker container HOME directory'
	V+=" -v $$T/.ssh:$$D_HOME/.ssh:Z"
	$(SUDO) docker run --name=$(CONTAINER_NAME) --rm -it $$V $(DOCKER_LABEL)
