FROM docker.io/fedora:25
MAINTAINER Billy Holmes <billy@gonoph.net>
COPY root/ /
RUN	useradd -u 1000 ansible -U \
	&& dnf update -y \
	&& dnf remove -y vim-minimal \
	&& dnf install -y \
	ansible \
	bind-utils \
	@development-tools \
	libcurl-devel \
	libxml2-devel \
	libxslt-devel \
	openssl \
	openssl-devel \
	procps-ng \
	python-devel \
	python-firewall \
	python-pycurl \
	redhat-rpm-config \
	sudo \
	vim \
	vim-minimal \
	&& dnf clean all
RUN	id \
	&& pip install -U pip \
	&& pip install -U beautifulsoup4 \
	&& pip install -U dnspython \
	&& pip install -U netaddr \
	&& pip install -U ovirt-engine-sdk-python \
	&& pip install -U requests
USER ansible
CMD [ "/bin/bash" ]
