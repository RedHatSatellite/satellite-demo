Satellite 6 Demo using Ansible
===========================

Group of ansible roles to install Satellite 6 and multiple systems in order to
perform a demo.

INFORMATION
-----------

This playbook will take a while to run.

This was based on two projects. One is by Julio Villarreal Pelegrino, and
another is from me (Billy Holmes).
* [Ansible Satellite 6 Install](https://github.com/juliovp01/ansible-satellite6-install.git)
* [satellite-install](https://github.com/gonoph/satellite-install.git)

Overview
--------

This colletions of roles will create a collection of systems for a Satellite 6
Demo that exist behind a jump box using internal non-public networks. It does
the following actions:

1. Creates a bunch of VMs via oVirt (or AWS when working)
  1. router server VM for proxy
  2. (proxied) satellite server VM
  3. (proxied) optional number of satellite capsule VMs
  4. (proxied) optional number of client VMs
2. Adds and configures any extra
  1. extra network interfaces are added and renamed to sane values
  2. extra disks are added to new or existing LVMs and existing content is rsync'd (for example for `/var`)
3. Properly configures the storage requirements for
  1. [Sat6 based on the install]
  2. based on [recommendations for mongodb]
4. Configures the router
  1. haproxy, dnsmasq
  2. Adds all the hosts in the demo for dns to work behind the proxy.
5. Configures the satellite server
  1. installs all the packages and configures the firewall
  2. runs the satellite installer and starts satellite
  3. copies or downloads the manifest from the Red Hat Portal
  4. enables all the demo repos and sets them for `on-download` for deferred downloads
  5. synchronizes the repos
  6. defines the demo content-views, adds all their repos, and publishes 1st version
  7. defines the demo lifecycle environments
  8. defines filters for one demo view, publishes, promotes them to environments, with one-month increment filters
  9. sets up the system with sane values, activiation keys, hostgroups, subnets, attaching subscriptions, and remastering the pxe-less discovery iso for automatic discovery

[Sat6 based on the install]: https://access.redhat.com/documentation/en/red-hat-satellite/6.2/paged/installation-guide/
[recommendations for mongodb]: https://docs.mongodb.com/manual/administration/production-notes/

There will be more later, but this is as far as I've gotten.

Requirements
------------

You will need a Red Hat Subscription for the following products:
* Red Hat Enterprise Linux Server Version 7
* Satellite 6

Additionally you will need the following:
* A [Red Hat Portal account](https://access.redhat.com/solutions/16762) login info / or a [Satellite 6 manifest file](https://access.redhat.com/solutions/118573)
* (AWS demo isn't working yet)
* Admin access to oVirt or RHV virtualization environment with at least 2 networks (VLANs are ok), one isolated

You will also need Ansible. There are several options:
* Red Hat Ansible Tower
* The [Ansible Website](https://www.ansible.com/)
* Via a Docker image from the included Dockerfile

You will need some RHEL templates with cloud-init installed.
* Build a RHEL image yourself and enable [cloud-init](https://access.redhat.com/solutions/1215553)
* Download and install the [KVM image](https://access.redhat.com/downloads/) on the Red Hat Portal for RHEL 7.3
* *When working* For AWS enable [Cloud Access](https://access.redhat.com/articles/migrating-to-red-hat-cloud-access) and access the RHEL 7.3 image from the market place
* Also via Cloud Access, you can bring your own image (BYOI)

You can obtain this from either the
Red Hat Portal or the AWS (*when working*) market place if you enabled Cloud Access

Layout
--------------

### Playbooks
The project has the following parent playbooks:
* `site.yml` - this is the main playbook that joins the VM creation and configuration plays
* `create_vms.yml` - this creates virtual machines from the `demo-vms` group
* `configure_vms.yml` - this configures the `direct` and `proxied` VMs
* `clean_vms.yml` - this cleans up everything, and will even unregister the RHEL systems

### Groups
The project has a number of groups:
* `demo-vms` - all the VMs for the demo
* `ovirt-hosts` - all the VMs that should be on RHV or oVirt
* `aws-hosts` - all the AWS hosts **doesn't work yet**
* `direct` - all the directly accessable hosts. *move them into aws-hosts or ovirt-hosts*
* `proxied` - all the non-directly accessable hosts. *move them into aws-hosts or ovirt-hosts*
* `routers` - `direct` router that allows access to the `proxied` hosts
* `satellites` - `proxied` satellite server for the demo
* `capsules` - `proxied` capsule servers **doesn't work yet**
* `clients` - `proxied` a bunch of clients for the demo **configures and builds, but not complete**

### Roles
The project defines several roles that performs a lot of the magic:
* `vms-ovirt` - the role that is used to create the oVirt VMs
* `vms-aws` - **TODO** will be the role that is used to create the AWS VMs
* `rhel` - the role that configures a RHEL server
* `router` - `rhel` based role that configures the router server
* `satellite` - `rhel` based role that configures the satellite server
* `satellite-capsule` - **TODO** will be the role that configures satellite capsules
* `satellite-client` - **TODO** will be the role that configures satellite clients

Variables
--------------

### Variable Locations
All role variables are stored as defaults in the `roles/:role:/defaults/main.yml`. This allows them to
be easily overriden via
* `group_vars` - varibles that are defined for the specific groups above
* `inventory vars` - variables that are defined for a specific host in the inventory file
* `commandline` - variables that override verything

### Customization of Group Vars
There's a few variables that you will want to customize and their typical location.

There's a lot to customize, so only the most important are listed.

**Variable file:** `group_vars/all/customize.yml`

This holds all the variables that are global and can be public:
* `ovirt_url` - the URL for the oVirt/RHV management interface
* `ovirt_user` - the username for the oVirt/RHV management interface
* `vm_template` - define your basic RHEL template here for all systems except the router
* `routers_vm_template` - this is like the `vm_template` above, except it should be RHEL Atomic Host for the router(s)
* `routers_storage_domain` - this is the storage domain from where to allocate the extra disk for the routers
* `satellite_storage_domain` - like above, but this is for the satellite server
* `capsule_storage_domain` - like above, but this is for the capsules
* `subscription_ak` - the default activation key
* `satellites_subscription_ak` - the activation key for the satellite server
* `add_certificates` - a list of servers:port to automatically download their CA and add to configured VMs
* `docker_haproxy` - This will override the docker image/location for the haproxy (*if you have a local registry*)
* `docker_ovirt_agent` - same as the `docker_haproxy` above
* `satellite_rhsm_user` - the username for RHSM (only used for satellite configuration if you don't have a manifest file)
* `satellite_rhsm_pass` - the password for RHSM (only used for satellite configuration if you don't have a manifest file)
* `satellite_manifest_file` - the manifest file on the local file system to copy and then upload to the satellite server
* `pulp_mirror` - a local pulp mirror to configure [pulp alternative content sources](https://docs.pulpproject.org/user-guide/content-sources.html)
* `authorized_ssh_keys` - you can leave it blank and a task will automatically put `~/.ssh/id_rsa.pub` on all VMs
* `subscription_mirror` - a list of repos that mirror the RHEL repos (**it can be another satellite pulp mirror**)
* `satellite_subscription_mirror` - like above, except for the satellite server

**Variable file:** `group_vars/all/secret.yml`
* This holds all the variables that aren't public, but you need. There's a secret.yml.example file for hints:
* `subscription_org` - the subscription organization to pair with the activation key. You can obtain this by running `subscription-manager identity` on any registered RHEL system.
* `ovirt_pass` - the login for the `ovirt_user` above
* `satellite_rhsm_pass` - the password that goes with the `satellite_rhsm_user` variable

**Variable file:** `group_vars/demo-vms.yml`
* `user_password` - by default we make a random password, and expect ssh-keys to work

###Special Variables

There are some varibles through the group files that are common in their function.
* `satellite_rhsm_user` - (`satellite` role) used to login into the Red Hat Portal
  - if this and the password are defined then the role will access the portal, and attempt to find and download the `manifest.zip` that matches the name of the current default Organization for the Satellite.
  - if they aren't defined, and the `satellite_manifest_file` is, then the role will copy the `manifest.zip` from the local ansible host, and then upload it into the satellite server.
* `subscription_mirror` - (`rhel` role) will create `mirror.repo` in `/etc/yum.repos.d/` from the contents of the dictionary
  - it will also install plugins from `subscription_plugins` from the repos in `subscription_repos_mirror`
* `satellite_subscription_contract`
  - if not defined, when we look for a subscription to attach to the activation key sorted by highest Quantity
  - if defined, then we will select the first subscription with that contract number
* `authorized_ssh_keys` - (`rhel` role) if blank will pull in ~/id_rsa.pub
  - otherwise will use the contents of the variable
* `nic` dictionary - (global) is auto populated from inventory vars
  - useful for playbooks that don't call a `setup` such as the vm creation tasks
  - or when you don't know the ip address of the host yet
  - or can not connect to it to obtain it, but still need it for a task
* `ansible_ssh_common_args` - (global) defined for the `proxied` hosts in order to use the router as the jump host
* `vm_extra_disks` - (`vms-ovirt` role and later aws) will automatically add those disks to the VM
  - `storage_domain` - (above) the pre-existing storage domain for the added disks. (big/cheap/fast)
* `lv` - (`rhel` role) this small variable has big consequences if defined.
  - it will add the extra disks
  - add/configure to existing or new VG/LV
  - rsync any existing files if asked
  - and defined a read-head value to meet the mongodb requirements and add that rule to udev 

Dependencies
------------

Obviously you need Ansible, but if you don't use the existing `Docker` image, then you also need the following.

Via the pip module or installed:
* (via yum) bind-utils
* beautifulsoup4
* dnspython
* netaddr
* ovirt-engine-sdk-python
* requests

If you use pip, some of those above will need to be compiled, and you'll need (for fedora at least):
* @development-tools - to compile anything
* libcurl-devel
* libxml2-devel
* libxslt-devel
* openssl-devel
* python-devel
* python-firewall
* python-pycurl
* redhat-rpm-config

Host File
----------

The host file for this role is inventory.prod. There's some special logic in it:

```ini
[test]
test-server ip=rhevm:eth0:192.168.26.63/24,int0:eth1:192.168.30.2/24,int1:eth2:192.168.31.2/24 gw=10
```

The above defines a `test-server` in the `test` group with three network interfaces and a gateway.
When expanded out by logic in the playbooks and templates, it will look like this.

- interface 1
  - `rhevm` oVirt interface (VM)
  - `eth0` OS interface
  - `192.168.26.63/24` is host/mask of the interface
- interface 2
  - `int0` oVirt interface (VM)
  - `eth1` OS interface
  - `192.168.30.2/24` is host/mask of the interface
- interface 3
  - `int1` oVirt interface (VM)
  - `eth2` OS interface
  - `192.168.31.2/24` is host/mask of the interface
- gateway
  - assumes 1st interface, 10 ip addresses into the CIDR of the network `192.168.26.0/24`

How to run the playbook
------------------------

**You will need the following beforehand:**
* Create and/or download a Satellite manfest (explained below).
* Download/install or create a **RHEL 7** Template wth `cloud-init` enabled
* Download/install or create a **RHEL 7 Atomic Host** Template with `cloud-init` enabled
* Edit `inventory.prod` with your ip networks and dns
* Edit `group_vars/all/customize.yml` with your settings
* Optionally copy `group_vars/all/customize.yml` to `group_vars/all/secret.yml` and edit with your full settings. The project's `.gitignore` is set to ignore the secret.yml file

**How to create or download the manifest for Satellite 6**

Go to rhn.redhat.com. 
- Click "Satellite"" 
- Click "Register a Satellite"
- Set a Name, select a version and Click "Register"
After this we are going to  attach a subscription. 
- Click "Attach Subscription" and select the subscription to attach and click "Attach Selected"
After this we will download the manifest. 
- Click "Download manifest"
After this copy the download file inside the /files directory on the role and name it satellite_manifest.zip 

Then edit the variable file on `group_vars/all/customize.yml` to set it to your environment.

**Run the playbook**

```bash
ansible-playbook -i inventory.prod site.yml
```

Skipping or only running certain sections
------------------------------------------

You can add `--tags=` to the playbook to limit the run to only certain tags.

The following tags are defined for different roles:

* vms-ovirt: ovirt - on all tasks below
  - login - only run the login sequence
  - create - only run the initial VM creation part
  - disks - only run the extra attachment of disks
  - tags - only tag the VMs as demo VMs
* rhel: configure - on all tasks below
  - certificates - only get CA certs and add them to the system
  - subscriptions - only register and attach subscriptions
  - mirrors - only run the section that adds the repo mirrors
  - disks - only run the disks plays that adds and rsyncs new disks
* routers: configure - since it depends on the `rhel` role, this also has a configure tag
  - networks - configures the networks and the extra interfaces for routing/MASQ
  - docker - for starting the haproxy and rhev agent docker containers
* satellites: satellite - only satellite tasks
  - satellite-packages - only install the packages to the system
  - satellite-networks - only configure the firewall and network
  - satellite-install - run the installer
  - satellite-hammer - run all the tasks that need hammer
  - satellite-manifest - only run the manifest tasks
  - satellite-repos - only run the repository tasks
  - satellite-sync - only synch the repositories
  - satellite-view - only create the content-views
  - satellite-environments - only create the lifecylce environments
  - satellite-cv-filter - only create/remove the sequence of creating rules for a demo view using 4 months of filters
  - satellite-provision - only run the provisioning sanity steps

License
-------

MIT

Author Information
------------------

Billy Holmes <billy@gonoph.net>

**Based on work by:**

Julio Villarreal Pelegrino <julio@linux.com> more at: http://wwww.juliovillarreal.com
