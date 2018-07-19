.PHONY: all install clean dist uninstall

DESTDIR?=/usr/local
BINDEST?=usr/bin
LIBDEST?=lib
VERSION?=unset
DIST_DEST?=/tmp/demoapp-latest.tar.gz

APP:=demoapp
SERVICE:=$(APP).service

INSTALL_APP:=$(DESTDIR)/$(BINDEST)/$(APP)
INSTALL_SERVICE:=$(DESTDIR)/$(LIBDEST)/systemd/system/$(SERVICE)

TO_INSTALL:=$(INSTALL_APP) $(INSTALL_SERVICE)

SOURCES:=COPYING demoapp demoapp.service demoapp.spec Makefile README

.ONESHELL:
all:
	@echo "Fake build"

$(TO_INSTALL): Makefile $(APP) $(SERVICE)
	
install: $(TO_INSTALL)
	@echo installing to $(DESTDIR)
	install -v -D -m 755 -T $(APP) $(INSTALL_APP)
	install -v -D -m 644 -T $(SERVICE) $(INSTALL_SERVICE)
	sed -i -e "s,%%%UPDATE_VERSION_HERE%%%,$(VERSION)," -e "s,%%%BUILD_INFO_HERE%%%,$$(hostname) $$(date)," $(INSTALL_APP)

clean:
	@rm -fv $(DIST_DEST)

uninstall:
	@rm -fv $(TO_INSTALL)

dist: $(DIST_DEST)

$(DIST_DEST): $(SOURCES)
	tar -czf $(DIST_DEST) $(SOURCES)

dist-build: dist
	rpmbuild -tb $(DIST_DEST)
