.PHONY: all clean create config install capsules clients myip step step0 step1 step2 step3 bulk bulk-demoapp bulk-poweroff bulk-unregister bulk-poweron
ROOT_DIR:=$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))

TAGS?=
LIMIT?=
NETS?=
ANSIBLE?=$(ROOT_DIR)/bin/time ansible-playbook -i $(INVENTORY_FILE) $(if $(TAGS), --tags=$(TAGS)) $(if $(LIMIT), --limit=$(LIMIT)) $(if $(NETS), --extra-vars=ec2_mynetworks='{{ "$(NETS)".split(",") }}')

FLAG_CREATE  :=.flag-create
FLAG_CONFIG  :=.flag-config
FLAG_INSTALL :=.flag-install
FLAG_CAPSULES:=.flag-capsules
FLAG_POST    :=.flag-post
FLAG_CLIENTS :=.flag-clients

PB:=./playbooks
PLAYBOOK_CLEAN   :=$(PB)/clean_ec2.yml
PLAYBOOK_CREATE  :=$(PB)/create_ec2.yml
PLAYBOOK_CONFIG  :=$(PB)/config_ec2.yml
PLAYBOOK_INSTALL :=$(PB)/config_satellite.yml
PLAYBOOK_CAPSULES:=$(PB)/config_capsules.yml
PLAYBOOK_POST    :=$(PB)/config_post.yml
PLAYBOOK_CLIENTS :=$(PB)/config_clients.yml
PLAYBOOK_DEMO    :=$(PB)/run_demo.yml
PLAYBOOK_BULK    :=$(PB)/bulkactions.yml

CREATE_INVENTORY :=playbooks/inventory/sat-demo
INSTALL_INVENTORY:=playbooks/inventory/demo.satellite

PLAYBOOKS:=$(PLAYBOOK_CLEAN) $(PLAYBOOK_CREATE) $(PLAYBOOK_CONFIG) $(PLAYBOOK_INSTALL) \
	$(PLAYBOOK_CAPSULES) $(PLAYBOOK_POST) $(PLAYBOOK_CLIENTS) $(PLAYBOOK_DEMO) $(PLAYBOOK_BULK)
PLAYBOOK_flags:=$(FLAG_CREATE) $(FLAG_CONFIG) $(FLAG_INSTALL) $(FLAG_CAPSULES) $(FLAG_POST) $(FLAG_CLIENTS)

help:
	@echo "Usage: make (help | all | clean | create | config | install | capsules | post | clients | step[123]| bulk-[action])"
	@echo "   help:       this help"
	@echo "   all:        run everything in the proper order"
	@echo "   clean:      clean up environment - delete VMs instances"
	@echo "   create:     create the VMs instances"
	@echo "   config:     configure the VMs instances"
	@echo "   install:    configure the satellite server" 
	@echo "   capsules:   configure satellite capsules"
	@echo "   post:       post configuration steps for demo"
	@echo "   clients:    configure clients"
	@echo "   myip:       helper target to add your current IP to the AWS VPC"
	@echo "   info:       helper target to get URL info"
	@echo "   step:       Demo help"
	@echo "   step0:      Demo step0 - build rpm for performance check"
	@echo "   step1:      Demo step1 - publish performance"
	@echo "   step2:      Demo step2 - HA/LB Capsule"
	@echo "   step3:      Demo step3 - content availability without Satellite master"
	@echo "   bulk-*:     Perform a bulk action:"
	@echo "         demoapp:    install or update demoapp on all the clients"
	@echo "         unregister: unregister all the systems"
	@echo "         poweroff:   stop services and poweroff all the systems"
	@echo "         poesron:    start all the ec2 instances"

all: create config install capsules post clients

clean create myip: INVENTORY_FILE=$(CREATE_INVENTORY)
config install capsules post clients info: INVENTORY_FILE=$(INSTALL_INVENTORY)
step step0 step1 step2 step3: INVENTORY_FILE=$(INSTALL_INVENTORY)
bulk bulk-demoapp bulk-unregister bulk-poweroff: INVENTORY_FILE=$(INSTALL_INVENTORY)
bulk-poweron: INVENTORY_FILE=$(CREATE_INVENTORY)

post: TAGS+=untagged,post

clean: $(PLAYBOOK_CLEAN)
	$(ANSIBLE) $<
	rm -f .flag-* *.retry
create:   $(CREATE_INVENTORY) $(FLAG_CREATE)
config:   create $(INSTALL_INVENTORY) $(FLAG_CONFIG)
install:  config $(INSTALL_INVENTORY) $(FLAG_INSTALL)
capsules: install $(INSTALL_INVENTORY) $(FLAG_CAPSULES)
post:     capsules $(INSTALL_INVENTORY) $(FLAG_POST)
clients:  post $(INSTALL_INVENTORY) $(FLAG_CLIENTS)
myip:
	$(ANSIBLE) $(PLAYBOOK_CREATE) --tags=ec2_network,untagged
step step0 step1 step2 step3:
	$(ANSIBLE) $(PLAYBOOK_DEMO) --extra-vars=step=$@ --tags=$@,untagged
bulk bulk-demoapp bulk-unregister bulk-poweroff bulk-poweron:
	$(ANSIBLE) $(PLAYBOOK_BULK) --extra-vars=bulk=$(patsubst bulk-%,%,$@)
info:
	$(ANSIBLE) $(PLAYBOOK_DEMO) --tags=info

$(FLAG_CREATE):   $(PLAYBOOK_CREATE) $(CREATE_INVENTORY) Makefile
$(FLAG_CONFIG):   $(PLAYBOOK_CONFIG) $(INSTALL_INVENTORY) Makefile
$(FLAG_INSTALL):  $(PLAYBOOK_INSTALL) $(INSTALL_INVENTORY) Makefile
$(FLAG_CAPSULES): $(PLAYBOOK_CAPSULES) $(INSTALL_INVENTORY) Makefile
$(FLAG_POST):     $(PLAYBOOK_POST) $(INSTALL_INVENTORY) Makefile
$(FLAG_CLIENTS):  $(PLAYBOOK_CLIENTS) $(INSTALL_INVENTORY) Makefile

$(INSTALL_INVENTORY): $(PLAYBOOK_CREATE)

$(PLAYBOOK_flags):
	$(ANSIBLE) $<
	touch $@
