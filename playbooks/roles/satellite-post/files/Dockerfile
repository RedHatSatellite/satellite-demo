FROM docker.io/fedora:28
# Old User should be default
USER root

ARG	HTTP_USER=admin
ARG	HTTP_PASS=redhat123
ARG	HTTP_UID=500
ARG	HTTP_GID=500

ENV	HTTPD_MAIN_CONF_PATH=/etc/httpd/conf \
	HTTPD_MAIN_CONF_D_PATH=/etc/httpd/conf.d

RUN     yum install -y \
	httpd mod_ssl git \
        && rm -rf /var/cache/yum/x86_64 \
	&& groupadd -g $HTTP_GID -f $HTTP_USER \
	&& useradd -u $HTTP_UID -g $HTTP_GID -c $HTTP_USER -d /git -M $HTTP_USER \
	&& mkdir /git \
	&& chown $HTTP_USER:$HTTP_USER /git \
	&& chmod 755 /git \
	&& chmod 777 /run/httpd \
	&& sed -i -e 's/^Listen 80/Listen 0.0.0.0:8888/' ${HTTPD_MAIN_CONF_PATH}/httpd.conf \
	&& sed -i -e 's%AllowOverride None%AllowOverride All%' ${HTTPD_MAIN_CONF_PATH}/httpd.conf \
	&& sed -i -e 's/^Listen 443/Listen 0.0.0.0:8443/' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf \
	&& sed -i -e 's/_default_:443/_default_:8443/' ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf \
	&& sed -ri " s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;" ${HTTPD_MAIN_CONF_PATH}/httpd.conf \
	&& sed -ri " s!^(\s*CustomLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*TransferLog)\s+\S+!\1 |/usr/bin/cat!g; s!^(\s*ErrorLog)\s+\S+!\1 |/usr/bin/cat!g;" ${HTTPD_MAIN_CONF_D_PATH}/ssl.conf \
	&& mv $HTTPD_MAIN_CONF_D_PATH/ssl.conf $HTTPD_MAIN_CONF_D_PATH/ssl.conf.bak \
	&& mkdir /etc/git \
	&& touch /etc/git/htpasswd \
	&& htpasswd -i /etc/git/htpasswd $HTTP_USER <<< "$HTTP_PASS"
COPY	git.conf /etc/httpd/conf.d/git.conf
COPY	run-gitserver /usr/bin/run-gitserver
USER	$HTTP_USER
VOLUME	/git
EXPOSE	8888 8443
ENTRYPOINT [ "/usr/bin/run-gitserver" ]
CMD	[ "/usr/sbin/apachectl", "-DFOREGROUND" ]
