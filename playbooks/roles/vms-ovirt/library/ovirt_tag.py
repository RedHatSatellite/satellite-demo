#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2016 Red Hat, Inc.
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

try:
    import ovirtsdk4 as sdk
    import ovirtsdk4.types as otypes
except ImportError:
    pass

from ansible.module_utils.ovirt import *


DOCUMENTATION = '''
'''


RETURN = '''
id:
    description: ID of the TAG which is found
    returned: On success if TAG is found.
    type: str
    sample: 7de90f31-222c-436c-a1ca-7e655bd5b60c
tag:
    description: "Dictionary of all the TAG attributes. TAG attributes can be found on your oVirt instance
                  at following url: https://ovirt.example.com/ovirt-engine/api/model#types/tag."
    returned: On success if TAG is found.
'''


class TagModule(BaseModule):

    def build_entity(self):
        return otypes.Tag(
            name=self._module.params['name'],
            description=self._module.params['description']
            )

    def update_check(self, entity):
        return (
            equal(self._module.params.get('name'), entity.name)
        )

    def pre_create(self, entity):
        # If TAG don't exists, and template is not specified, set it to Blank:
        if entity is None:
            if self._module.params.get('description') is None:
                self._module.params['description'] = 'Created by Ansible'

def main():
    argument_spec = ovirt_full_argument_spec(
        state=dict(
            choices=['present', 'absent', 'detached'],
            default='present',
        ),
        name=dict(default=None),
        id=dict(default=None),
        vm_id=dict(default=None),
        vm_name=dict(default=None),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    check_sdk(module)
    check_params(module)

    try:
        state = module.params['state']
        connection = create_connection(module.params.pop('auth'))
        tag_service = connection.system_service().tags_service()
        tag_module = TagModule(
            connection=connection,
            module=module,
            service=tag_service,
        )
        tag = tag_module.search_entity()
        state = module.params.get('state')

        if state == 'absent':
            ret = tag_module.remove()
        else:
            ret = tag_module.create(entity=tag)

        vm_id = module.params.get('vm_id')
        vm_name = module.params.get('vm_name')
        # If VM was passed attach/detach disks to/from the VM:
        if (vm_id is not None or vm_name is not None) and state != 'absent':
            vms_service = connection.system_service().vms_service()

            # If `vm_id` isn't specified, find VM by name:
            vm_id = module.params['vm_id']
            if vm_id is None:
                vm_id = getattr(search_by_name(vms_service, module.params['vm_name']), 'id', None)

            # verify vm_id
            vm_service = vms_service.vm_service(vm_id)
            vm_id = getattr(vm_service.get(), 'id', None)

            if vm_id is None:
                module.fail_json(
                    msg="VM don't exists, please create it first."
                    )

            vm_tags_service = vms_service.vm_service(vm_id).tags_service()
            vm_tags_module = TagModule(
                connection=connection,
                module=module,
                service=vm_tags_service,
                changed=ret['changed'] if ret else False,
                )

            if state == 'present' or state == 'attached':
                ret = vm_tags_module.create()
            elif state == 'detached':
                ret = vm_tags_module.remove()

        module.exit_json(**ret)
    except Exception as e:
        module.fail_json(msg=str(e))
    finally:
        connection.close(logout=False)

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
