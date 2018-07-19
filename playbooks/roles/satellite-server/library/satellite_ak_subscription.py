#!/usr/bin/python
# vim: sw=4 ai ts=4 expandtab
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['stableinterface'],
                    'supported_by': 'core'}

DOCUMENTATION = '''
---
author: "Billy Holmes (@gonoph)"
module: satellite_ak_subscription
short_description: Coerce multiple subscription and activation key data into dict 
description:
    - This module merges multiple sources of subscription and activation key data.
    - This merged data can be used to update the subscription information for activation keys.
    - This module is intended to work with Satellite 6.3 and above.
options:
    satellite_hammer_views:
        description:
            - the satellite-server role's hammer view data structure
        required: true
        default: null
    api_activation_keys:
        description:
            - the json result from the activation_keys API call
        required: true
        default: null
    api_subscriptions:
        description:
            - the json result from the subscription list API call
        required: true
        default: null
    api_activation_keys_subscriptions:
        description:
            - the json result from the activation_keys subscription list API call
        required: true
        default: null
version_added: "2.5"
notes:
    - this is designed to work witih Satellite 6.3 and above
'''

EXAMPLES = '''
# Example of calculating the needed subsriptions for activation keys
- satellite_ak_subscription:
    satellite_hammer_views: "{{ satellite_hammer_views }}"
    api_activation_keys: "{{ call_ak }}"
    api_subscriptions: "{{ call_subs }}"
    api_activation_keys_subscriptions: "{{ call_sub_ak }}"
'''
