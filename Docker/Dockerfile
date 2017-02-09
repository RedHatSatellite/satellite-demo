FROM docker.io/centos:7
MAINTAINER Billy Holmes <billy@gonoph.net>
COPY root/ /
RUN	useradd -u 1000 ansible -U \
	&& yum update -y \
	&& yum remove -y vim-minimal \
	&& yum install -y epel-release \
	&& yum install -y \
	ansible \
	bind-utils \
	@development \
	libcurl-devel \
	libxml2-devel \
	libxslt-devel \
	openssl \
	openssl-devel \
	procps-ng \
	python-devel \
	python-firewall \
	python2-pip \
	python-pycurl \
	redhat-rpm-config \
	sudo \
	vim \
	vim-minimal \
	&& yum clean all
RUN	id \
	&& PYCURL_SSL_LIBRARY=nss pip install -U pycurl \
	&& pip install -U pip \
	&& pip install -U beautifulsoup4 \
	&& pip install -U dnspython \
	&& pip install -U netaddr \
	&& pip install -U ovirt-engine-sdk-python \
	&& pip install -U pyOpenSSL \
	&& pip install -U requests
USER ansible
CMD [ "/bin/bash" ]
