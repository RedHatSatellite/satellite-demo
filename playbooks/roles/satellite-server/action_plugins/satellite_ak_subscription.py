# vim: sw=4 ai ts=4 expandtab

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.errors import AnsibleAction, AnsibleActionFail
from ansible.module_utils._text import to_text

def readAKS(json):
    aks = dict()
    results = json.get('results', None)
    if results is None:
        raise AnsibleActionFail("Activation Key API data doesn't have results array!")

    for item in results:
        aks[item['name']] = dict(id=item['id'], subscriptions=[], to_add=[])
    return aks

def readSubs(json):
    subs = dict()
    results = json.get('results', None)
    if results is None:
        raise AnsibleActionFail("Subscription API data doesn't have results array!")

    for item in results:
        pid=item['product_id']
        dd=dict(id=item['id'], available=item['available'])
        if pid in subs:
            if subs[pid]['available'] < dd['available']:
                subs[pid]=dd
        else:
            subs[pid]=dd
    return subs

def readAKSubs(json):
    akSubs = dict()
    results = json.get('results', None)
    if results is None:
        raise AnsibleActionFail("Activation Key Subscription  API data doesn't have results array!")

    for item in results:
        dd=[]
        results2 = item.get('json', dict(json={})).get('results', None)
        if results2 is None:
            raise AnsibleActionFail("Activation Key Subscription  API data doesn't have results array!")

        for sub in results2:
            dd.append(sub['product_id'])
        akSubs[item['item']['name']] = list(set(dd))
    return akSubs

def hammerViewToAKSubs(satellite_hammer_views):
    dd=filter(lambda x: x['ak'], satellite_hammer_views)
    dd=map(lambda x: [x['ak'], x['ak_product_ids']], dd)
    return dict(dd)

def findSub(sublist, subs):
    if not sublist:
        return None

    if sublist[0] in subs:
        return subs[sublist[0]]

    return findSub(sublist[1:], subs)

def findNewActivationKeySubscriptions(satellite_hammer_views, api_ak, api_subs, api_ak_subs):
    hv=hammerViewToAKSubs(satellite_hammer_views)
    aks=readAKS(api_ak)
    subs=readSubs(api_subs)
    ak_subs=readAKSubs(api_ak_subs)

    # merge existing subscriptions with activation keys
    for ak in aks:
        aks[ak]['subscriptions']=ak_subs[ak]

    # find missing subscriptions for activation keys
    for ak in hv:
        if not hv[ak]:
            continue
        if not set(hv[ak]).intersection(aks[ak]['subscriptions']):
            new_sub = findSub(hv[ak], subs)
            if new_sub:
                aks[ak]['to_add'].append(new_sub['id'])

    is_changed = reduce(lambda x,y: x+y, map(lambda x: len(aks[x]['to_add']), aks)) > 0

    return dict(ansible_facts=dict(satellite_ak_subscription=aks), changed=is_changed)

class ActionModule(ActionBase):

    TRANSFERS_FILES = False

    def run(self, tmp=None, task_vars=None):

        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)
        satellite_hammer_views=self._task.args.get('satellite_hammer_views', None)
        api_activation_keys=self._task.args.get('api_activation_keys', None)
        api_subscriptions=self._task.args.get('api_subscriptions', None)
        api_activation_keys_subscriptions=self._task.args.get('api_activation_keys_subscriptions', None)

        try:
            if satellite_hammer_views is None and type(satellite_hammer_views) == list:
                raise AnsibleActionFail('satellite_hammer_views must be defined and be a list!')
            if api_activation_keys is None or api_activation_keys.get('json', None) is None:
                raise AnsibleActionFail('api_activation_keys must be defined and have json response!')
            if api_subscriptions is None or api_subscriptions.get('json', None) is None:
                raise AnsibleActionFail('api_subscriptions must be defined and have json response!')
            if api_activation_keys_subscriptions is None or api_activation_keys_subscriptions.get('results', None) is None:
                raise AnsibleActionFail('api_activation_keys_subscriptions must be defined and have results array!')

            chk = map(lambda x: 1 if x.get('json', None) is None else 0, api_activation_keys_subscriptions['results'])
            chk = reduce(lambda x,y: x + y, chk)
            if chk > 0:
                raise AnsibleActionFail('api_activation_keys_subscriptions.results[] must have items with json defined!')

            chk = map(lambda x: 1 if x['json'].get('results', None) is None else 0, api_activation_keys_subscriptions['results'])
            chk = reduce(lambda x,y: x + y, chk)
            if chk > 0:
                raise AnsibleActionFail('api_activation_keys_subscriptions.results[].json must have results array!')

            try:

                result.update(findNewActivationKeySubscriptions(
                        satellite_hammer_views,
                        api_activation_keys['json'],
                        api_subscriptions['json'],
                        api_activation_keys_subscriptions
                        ))

            except Exception as e:
                # raise AnsibleActionFail("%s: %s" % (type(e).__name__, to_text(e)))
                raise

        except AnsibleAction as e:
            result.update(e.result)

        return result
