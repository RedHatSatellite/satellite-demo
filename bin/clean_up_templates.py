#!/bin/env python
#vim: sw=2 ai expandtab

from json import loads
from subprocess import check_output, call

OK_LIST=(
  'Discovery Red Hat kexec',
  'idm_register',
  'Kickstart default iPXE',
  'Kickstart default PXELinux',
  'kickstart_networking_setup',
  'puppet.conf',
  'remote_execution_ssh_keys',
  'saltstack_minion',
  'Satellite Atomic Kickstart Default',
  'Satellite Kickstart Default',
  'Satellite Kickstart Default Finish',
  'Satellite Kickstart Default User Data',
  'subscription_manager_registration'
)

print "Getting Organzation Id"
ORG = loads(check_output('/usr/bin/hammer --output=json organization list --search=name=Demo62', shell=True))[0]['Id']
print "Getting Location Id"
LOC = loads(check_output('/usr/bin/hammer --output=json location list --search=name=LocalNet', shell=True))[0]['Id']
print "ORG=%s\nLOC=%s" % (ORG, LOC)

print "Reading all templates that belong to Organzation"
j =  loads(check_output(['/usr/bin/hammer', '--output=json', 'template', 'list', '--organization-id', str(ORG)]))
print "Reading all templates that belong to Location"
j += loads(check_output(['/usr/bin/hammer', '--output=json', 'template', 'list', '--location-id', str(LOC)] ))
print "Merging lists"
j = dict(list(map(lambda x: (x['Id'], x['Name']), j)))
print "Templates: %d" % len(j)

print "Filtering out items that are in the OK_LIST"
ids = dict(list(filter(lambda x: x[1] not in OK_LIST, j.items())))
print "Filtered: %d" % len(ids)
print "Items to remove:"
for i in ids:
  print "%d - %s" % (i, ids[i])

def ret(rc):
  return 'success' if rc==0 else 'failed'

with open('/dev/null','rw') as devnull:
  for i in ids:
    rc = call(['/usr/bin/hammer', 'location', 'remove-config-template', '--config-template-id', str(i), '--id', str(LOC)], stdout=None, stderr=None)
    print "Removed Location: %d %s - %s" % (i, ids[i], ret(rc))
    rc = call(['/usr/bin/hammer', 'organization', 'remove-config-template', '--config-template-id', str(i), '--id', str(ORG)], stdout=None, stderr=None)
    print "Removed Organization: %d %s - %s" % (i, ids[i], ret(rc))
