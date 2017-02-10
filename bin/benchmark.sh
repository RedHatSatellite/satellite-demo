#!/bin/sh

cat<<EOF
This will take a long time, so please be patient:
If you don't see:

ALL DONE!

Then there was an error, so review the log at:

  /tmp/benchmark.log

EOF

set -e -E # fast fail
> /tmp/benchmark.log
echo "First we clean everything up"
time ansible-playbook -i inventory.prod clean_vms.yml --limit=routers,satellites >> /tmp/benchmark.log

echo
echo "Time the VM creation of the servers"
time ansible-playbook -i inventory.prod create_vms.yml --limit=routers,satellites >> /tmp/benchmark.log

echo
echo "Time the configuration of the router"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=routers >> /tmp/benchmark.log

echo
echo "Time the configuration of the satellite"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --skip-tags=satellite >> /tmp/benchmark.log

echo
echo "Time the installation of Satellite 6"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --tags=satellite --skip-tags=satellite-hammer >> /tmp/benchmark.log

echo
echo "Time the configuration of Satellite 6"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --tags=satellite-hammer -e satellite_hammer_configure_CV_filters=true >> /tmp/benchmark.log

cat << EOF

ALL DONE!!

EOF
