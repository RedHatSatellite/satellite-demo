#!/bin/sh
# vim: sw=2 ts=2 expandtab ai
# check to see if we're timing ourselves
_MAGIC_=dRBf33M6y8Z66rai

if [ "x$1" != "x$_MAGIC_" ] ; then
  time $0 $_MAGIC_ "$@"
  exit 0
fi

shift 1

MAX_STAGE=7
KEEP=0

while test $# -gt 0 ; do
  case $1 in
    -h | --h | --he | --hel | --help)
      echo $"Usage: benchmark.sh [OPTION]... [maxstage]
  -h, --help  this usage message
  -k, --keep  keep the current VMs by not running the clean step
  maxstage    maximum stage [1, 2, 3, 4, 5, 6] for execution

  [STAGES]
  1. Clean up the previous run
  2. Create the (router) and (satellite) VMs
  3. Configure the (router)
  4. Configure the (satellite)
  5. Install the packages for Satellite 6
  6. Setup Satellite 6 just before the CV views
  7. Finish the Satellite 6 installation
"
      exit 0
      ;;
    -k | --k | --ke | --kee | --keep)
      KEEP=1
      shift
      ;;
    [123456])
      MAX_STAGE=$1
      shift
      ;;
    *)
      echo "Please see Usage via --help, unrecognized option: $1"
      exit 1
      ;;
  esac
done

header() {
  echo $"
This will take a long time, so please be patient:
If you don't see:

ALL DONE!

Then there was an error, so review the log at:

  /tmp/benchmark.log

"
}

alldone() {
  [ $MAX_STAGE -ne 7 ] && echo $"
MAX STAGE REACHED == $MAX_STAGE
"
  echo $"

ALL DONE!!

"
  exit 0
}

header

set -e -E # fast fail
> /tmp/benchmark.log

export ANSIBLE_FORCE_COLOR=true

echo "1. First we clean everything up"
[ $KEEP -gt 0 ] && time echo "Not running clean, keeping systems." || \
time ansible-playbook -i inventory.prod clean_vms.yml --limit=routers,satellites >> /tmp/benchmark.log
[ $MAX_STAGE -eq 1 ] && alldone

echo
echo "2. Time the VM creation of the servers"
time ansible-playbook -i inventory.prod create_vms.yml --limit=routers,satellites >> /tmp/benchmark.log
[ $MAX_STAGE -eq 2 ] && alldone

echo
echo "3. Time the configuration of the router"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=routers >> /tmp/benchmark.log
[ $MAX_STAGE -eq 3 ] && alldone

echo
echo "4. Time the configuration of the satellite"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --skip-tags=satellite >> /tmp/benchmark.log
[ $MAX_STAGE -eq 4 ] && alldone

echo
echo "5. Time the installation of Satellite 6"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --tags=satellite --skip-tags=satellite-hammer >> /tmp/benchmark.log
[ $MAX_STAGE -eq 5 ] && alldone

echo
echo "6. Time the manifest, repos, sync, and views"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --tags=satellite-manifest,satellite-repos,satellite-sync,satellite-view >> /tmp/benchmark.log
[ $MAX_STAGE -eq 6 ] && alldone

echo
echo "7. Time the rest of the configuration"
time ansible-playbook -i inventory.prod configure_vms.yml --limit=satellites --tags=satellite-hammer -e satellite_hammer_configure_CV_filters=true >> /tmp/benchmark.log

alldone
