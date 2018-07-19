FROM fedora:28
MAINTAINER Billy Holmes <billy@gonoph.net>

ENV	PS1='\[\033[01;30m\](\[\033[01;32m\]container\[\033[01;30m\])\[\033[0m\] [\u@\h \[\033[01;34m\]\W\[\033[0m\]]$ ' \
	BUILD_USER=%%USER%% \
	BUILD_UID=%%UID%% \
	BUILD_GID=%%GID%%

# Metrics install needs these to create the passwords
# - python2-passlib
# - httpd-tools
# - java-1.8.0 
# for the EC2 playbooks:
# - python2-netaddr
# - python2-boto3
# For testing and the post playobok:
# - jq
# - origin-clients

RUN    	sed -i 's/^enabled=1/enabled=0/' /etc/yum.repos.d/fedora-updates-testing.repo \
	&& yum update -y \
	&& yum install -y \
	atomic \
	ansible \
	git \
	make \
	jq \
	procps-ng \
	# python2-pip \
	python2-boto \
	python2-boto3 \
	python2-docker-py \
	python2-netaddr \
	python2-passlib \
	python3.x86_64 \
	python3-boto \
	python3-boto3 \
	python3-netaddr \
	python3-passlib \
	# python3-pip \
	sudo \
        vim \
        && rm -rf /var/cache/yum

# Setup container to have same UID/GID as the build user on the host
RUN	groupadd -fg $BUILD_GID $BUILD_USER \
        && useradd -ou $BUILD_UID -g $BUILD_GID ansible \
	&& usermod -a -G wheel,$BUILD_GID ansible \
        && echo "ansible  ALL=(ALL)       NOPASSWD: ALL" > /etc/sudoers.d/ansible_conf

WORKDIR	/tmp/install
COPY	files /
USER    ansible
CMD [ "/usr/bin/bash" ]
