Satellite 6 Demo using Ansible
===========================

Group of ansible roles to install Satellite 6 and multiple systems in order to
perform a demo.

INFORMATION
-----------

This whole set of playbooks will take a while to run (between 2.5 and 3 hrs with current inventory is about $1.59)

This was based on two projects. One is by Julio Villarreal Pelegrino, and
another is from me (Billy Holmes).
* [Ansible Satellite 6 Install](https://github.com/juliovp01/ansible-satellite6-install.git)
* [satellite-install](https://github.com/gonoph/satellite-install.git)

Overview
--------

This colletion of playbooks and roles will create a set of systems for a
Satellite 6 Demo that use an example domain (example-dot-com) using a
customized dns server, and an haproxy node to load balance the capsules. It
does the following actions:

1. Creates a bunch of VMs on AWS
   1. dns/haproxy for our fake domains and LB/HA stuff to work.
   2. satellite server VM [based on the install recommendations][1]
   3. two satellite capsule VMs in HA/LB mode [as detailed in the upstream foreman][2]
   4. two client VMs
2. Configures the local install environment
   1. Creates a new inventory file that is AWS/GCE agnostic
   2. updates the local ssh config for easy ssh access
3. Configures the dns node
   1. haproxy, dnsmasq
   2. Adds all the hosts in the demo for dns to work
4. Configures the satellite server
   1. installs all the packages and configures the firewall
   2. runs the satellite installer and starts satellite
   3. copies or downloads the manifest from the Red Hat Portal
   4. enables all the demo repos and sets them for `on-download` for deferred downloads
   5. synchronizes the repos
   6. defines the demo content-views, adds all their repos, and publishes 1st version
   7. defines the demo lifecycle environments
   8. *optional* defines filters for one demo view, publishes, promotes them to environments, with one-month increment filters
   9. sets up the system with sane provisioning values:
      1. activiation keys
      2. hostgroups, subnets
      3. attaching subscriptions
      4. remastering the pxe-less discovery iso for automatic discovery
  10. cleans up the templates by removing ones we don't use
5. Configures the Capsules
   1. registers them to the satellite
   2. generates the certificates
   3. installs the capsule packaegs and configures the firewall
   4. runs the capsule installer and starts the capsule process
   5. assigns the lifecycle environments to the capsules
   6. assigns capsules to default org and loc, sets download polciy to inherit from repo
   7. force content synchronization on capsules that haven't been
6. Post-configuration: configures the demo settings
   1. turns extras repo to immediate download
   2. install rpm-devel on satellite to create `demoapp`
   3. create Demo product:
      1. Create Demo product and repo
      2. Create Demo App Content View
      3. Create Demp Comp Composite View
      4. Add Demo App and RHEL-7Server Content Views to the Demo Comp Compsite View
      5. Publish Demo CV's if needed
      6. Create Activation Key for Demo Product
      7. Assign Demo product to AK
      8. Create the Demo Host Group
      9. Wait for caspules to finish sync'ing the changes if needed
7. Configures the clients
   1. registers them to the satellite or capsule LB/HA endpoint
   2. assigns a HG and gives them subscriptions via the AK

[1]: https://access.redhat.com/documentation/en/red-hat-satellite/6.3/paged/installation-guide/
[2]: https://theforeman.org/2018/05/load-balanced-smart-proxies-with-haproxy.html

Requirements
------------

1. Assign subscriptions for RHEL:
   1. Create an Activation Key in the [Portal][6]
     * By Default, I'm using an activation key of `SATELLITE-DEMO-SATELLITE`, [here's how to create one][5].
   2. Assign your subscriptions to [Cloud Access][3]
     * 6x Red Hat Enterprise Linux Server (will be running version RHEL 7.5)
     * You will effectively "double register" the Satellite server.
2. A Satellite manifest.zip
   * Create a manifest [Obtained from the portal][4]
   * Put in the following subscriptions:
     * at least 2x Subscriptions for RHEL (ex: RH00008)
     * at least 2x Subscriptions for the capsules (ex: MCT3718)
     * for a complete list, look in the [defaults file](./playbooks/roles/satellite-server/defaults/main.yml)
   * download the manifest and place it where this README.md is located.
3. Your AWS and Satellite credentials in an environment file:
   * `AWS_ACCESS_KEY` - your AWS access key
   * `AWS_SECRET_KEY` - your AWS secret key
   * `SUBSCRIPTION_ORG` - your Satellite Org, so the activation key works
4. Source the environment file before running the playbook (or use the boostrap container detailed below).

```bash
$ source ./env_file
```

[3]: https://www.redhat.com/en/technologies/cloud-computing/cloud-access
[4]: https://access.redhat.com/solutions/1217793
[5]: https://access.redhat.com/articles/1378093
[6]: https://access.redhat.com/management/activation_keys

Additionally, you will need Ansible. There are several options:
* Red Hat Ansible Tower
* The [Ansible Website](https://www.ansible.com/)
* Use the [bootstrap image](./bootstrap/README.md)

Layout
--------------

### Playbooks and tasks
I'm using a Makefile to break up the playbooks and save time when different steps are completed if you need to go back and re-run different tasks.

type `make` to get a help:

```text
Usage: make (help | all | clean | create | config | install | capsules | post | clients | step[123]| bulk-[action])
   help:       this help
   all:        run everything in the proper order
   clean:      clean up environment - delete VMs instances
   create:     create the VMs instances
   config:     configure the VMs instances
   install:    configure the satellite server
   capsules:   configure satellite capsules
   post:       post configuration steps for demo
   clients:    configure clients
   myip:       helper target to add your current IP to the AWS VPC
   info:       helper target to get URL info
   step:       Demo help
   step0:      Demo step0 - build rpm for performance check
   step1:      Demo step1 - publish performance
   step2:      Demo step2 - HA/LB Capsule
   step3:      Demo step3 - content availability without Satellite master
   bulk-*:     Perform a bulk action:
         demoapp:    install or update demoapp on all the clients
         unregister: unregister all the systems
         poweroff:   stop services and poweroff all the systems
         poesron:    start all the ec2 instances
```

Inventory File
--------------

### Variable Locations

There are (2) two inventory files:
1. a [static inventory](./playbooks/inventory/sat-demo) file that you can edit.
2. a dynamic inventory that is generated: `./playbooks/inventory/demo.satellite`

The purpose is that after the create task, the playbooks operate on the dynamic
inventory file and thus are unaware of which cloud provide (if any) the VMs are
located.

Misc
------------

### Bulk Actions

You can run certain bulk actions using the bulk make task or the bulk action playbook:

1. demoapp - cycles through the clients and updates the demoapp using yum
2. unregister - cycles through all the VMs in the demo and unregisters them
3. poweroff - cycles through all VMs, shutdowns satellite/capsules and docker, then powers them off
4. poweron - cycles through the static inventory and powers on all the VMs

Once you `poweron` the VMs, you should run `make all` to have them reset their
cloud provider DNS and hostname settings.

### Default Inventory

| Host | AWS type | vCPU | Memory | Purpose |
| ---- | -------- | ---- | ------ | ------- |
| dns1 | t2.small | 1 | 2GiB | dns, haproxy |
| clients1,2 | t2.small | 1 | 2GiB | demoapp, clients |
| capsule1,2 | m5.large | 2 | 8GiB | capsule |
| satellite | m5.xlarge | 4 | 16GiB | satellite |

### Inventory Variables you'll probably need to change 

| Variable | Why change? |
| -------- | ----------- |
| `ec2_ami_image` | You need [Red Hat Cloud Access][Cloud Access] in order to see the supplied image. |
| `ansible_user` | If you change the image above, you'll need to know the login user (ex: ec2-user, cloud-user) |
| `ec2_demo_tag` | If you change this, then you can run multiple of these clusters in AWS at the same time. You'll have to add it to the `ec2` group in the inventory file. |
| `private_ip_start` | If you change the above, then you'll need to change this variable, too, probably. |
| `ec2_instance_type` | If you want beefier VMs. With the current inventory in AWS, it costs me $10.90 per day as of Jul 20th, 2018. |
| `ec2_volume_sizes` | The array of volume sizes, current inventory configures a total of 562 GiB at a cost of about $1.77 a day. The more storage allocated to the Satellite and Capsules means more throughput and IOPS, you can also change the storage type and get more performance while paying more. |

[Cloud Access]: https://www.redhat.com/en/technologies/cloud-computing/cloud-access


License
-------

MIT

Author Information
------------------

Billy Holmes <billy@gonoph.net>

**Based on work by:**

Julio Villarreal Pelegrino <julio@linux.com> more at: http://wwww.juliovillarreal.com

Disclaimer
----------

**DISCLAIMER**: I'm a Red Hat Solutions Architect. It's my job to introduce Red
Hat customers to Red Hat products, and help them gain the most value from these
products. I am not support, nor releasing this as a representative of Red Hat.
Thus, I cannot help you use this playbook in production, enterprise, PoC, or
bake-off situation. I will gladly help you get in contact with someone at Red
Hat that **CAN** help you do these things.

The purpose of this playbook is to build a demo and an experimental environment
for Satellite, some capsules, and some clients.  If you have any questions or
run into issues running these playbooks to achieve that goal, then please
create a GitHub issue so I can address it!

If you have other questions or issues with Satellite in general, I'll gladly
help you reach the correct resource at Red Hat!

