#!/usr/bin/env python
# vim: sw=4 ai ts=4 expandtab

import sys

from yum import YumBase
from yum.parser import varReplace

# we need this in order to load the subscription_manager stuff
_LIBPATH = "/usr/share/rhsm"
# add to the path if need be
if _LIBPATH not in sys.path:
    sys.path.append(_LIBPATH)

HAVE_SM = True
try:
    # from subscription_manager.i18n import configure_i18n
    # configure_i18n()
    # from subscription_manager import logutil
    # logutil.init_logger()
    from subscription_manager.injectioninit import init_dep_injection
    init_dep_injection()
    import subscription_manager.repolib as repolib
    from subscription_manager.api.repos import enable_yum_repositories, disable_yum_repositories
except:
    HAVE_SM = False

# we need to do this in order to prevent the stdout/stderr output from the yum package
def YumSingleton():
    from StringIO import StringIO
    new_out = StringIO()
    sav_out = (sys.stdout, sys.stderr)      # save old IO
    [ x.flush() for x in sav_out ]          # flush output
    sys.stdout = sys.stderr = new_out
    ex = None
    try:
        yb = YumBase()
        yb.conf
        return yb
    except Exception as x:
        ex = x                              # save exception
    finally:
        new_out.flush()                     # grab the output
        (sys.stdout, sys.stderr) = sav_out  # restore it
    # if we got here, then we had an error
    sys.stderr.write(str(new_out))
    raise ex if ex else Exception('Error creating yum.YumBase()')

yum = YumSingleton()                        # use the same instance
del YumSingleton                            # prevent anyone else from creating it

class Logger(object):
    def __init__(self, ansible):
        self.logger = ansible

    def log(self, v, fmt, *kwargs):
        if v <= self.logger._verbosity:
            s = str(fmt) if not kwargs else fmt.format(*kwargs)
            self.logger.log(s)

# Class to filter out repos that are enabled
class SMRepoFilter(object):
    def __init__(self, logger, cache_only=True):
        self.logger = logger
        self.enabled = HAVE_SM
        # this is the SM invoker that does most of the work
        self.invoker = repolib.RepoActionInvoker(cache_only=cache_only) if HAVE_SM else None
        self.update = False
        self._repos = ()

    # returns: dictionary of all SM repos, plus updates the repo file if needed
    def getRepos(self):
        if not self.enabled or self._repos:
            return self._repos

        self._repos = dict(self._generator_repos())
        if self.update:
            self.invoker.update()

        return self._repos

    def _generator_repos(self):
        # get and filter repos from yum, so we can compare it against what SM knows about
        yum_repos = dict((rr[0], rr[1].enabled) for rr in yum.repos.repos.items())
        # get repos from SM
        for x in self.invoker.get_repos():
            enabled = True if x['enabled'] == '1' else False

            # if the SM reppo id is not in the yum repo list, or it's enabled flag doesn't match
            # then we mark the repo file as dirty
            if x.id not in yum_repos or yum_repos[x.id] != enabled:
                self.update = True

            # replace the $vars with the yumvar settings
            x['baseurl']=varReplace(x['baseurl'], yum.conf.yumvar)
            x['enabled']=enabled

            # generate the dictionary
            yield (x.id, x)

    # returns: list of enabled repo ids
    def getEnabled(self):
        return () if not self.enabled else tuple(x for x in self.getRepos() if self.getRepos()[x]['enabled'])

    # returns: list of disabled repo ids
    def getDisabled(self):
        return () if not self.enabled else tuple(x for x in self.getRepos() if not self.getRepos()[x]['enabled'])

class SubscriptionManagerRepos:
    def __init__(self, assign, logger, cache_only=True):
        self.assign = tuple(set(assign))
        self.logger = logger
        self.repo_filter = SMRepoFilter(logger, cache_only=cache_only)
        self._repos=None
        self.enabled = self.repo_filter.enabled
        self._not_found = set()

    def getRepos(self):
        if self._repos:
            return self._repos
        self._repos = (
                self.repo_filter.getEnabled(),
                self.repo_filter.getDisabled(),
                )
        return self._repos

    def getNotFound(self):
        return tuple(self._not_found)

    def _disabled_generator(self):
        # iter over enabled repos
        for r in self.getRepos()[0]:
            self.logger.log(4, '_disabled_generator: {}', r)
            # if it's not in the list of what we want enabled, then disable it
            if r not in self.assign:
                self.logger.log(3, '_disabled_generator: yielding as [{}] is not in [{}].', r, self.assign)
                yield r

    def _enabled_generator(self):
        # iter over what we want
        for r in self.assign:
            self.logger.log(4, '_enabled_generator: {}', r)
            # if it's not in the enabled list, then enable it
            if r not in self.getRepos()[0]:
                # if it's not in the disabled list either, then we can't find it
                if r not in self.getRepos()[1]:
                    self.logger.log(1, '_enabled_generator: not_found {}', r)
                    self._not_found.add(r)
                else:
                    self.logger.log(2, '_enabled_generator: yielding as [{}] is not in [{}].', r, self.getRepos()[0])
                    yield r

    def get_enable_disable(self):
        to_enable = tuple(self._enabled_generator())
        to_disable = tuple(self._disabled_generator())
        return (to_enable, to_disable)

    def fix_msg(self, ret):
        ret['msg']='. '.join(ret['msg'])
        return ret

    def apply(self, check_mode=False):
        (to_enable, to_disable) = self.get_enable_disable()
        ret = dict(
                assign=self.assign,
                repo_updated=self.repo_filter.update,
                previous_repos=self.getRepos()[0],
                to_apply=dict(
                    enable=to_enable,
                    disable=to_disable
                    ),
                summary=dict(
                    wanted=dict(
                        enable=len(to_enable),
                        disable=len(to_disable),
                        ),
                    applied=dict(
                        enable=0,
                        disable=0,
                        ),
                    ),
                not_found=self.getNotFound(),
                changed=True if to_enable or to_disable else False,
                failed=True if self.getNotFound() else False,
                msg=set(''),
                )

        if check_mode:
            self.logger.log(1, 'check_mode is enabled')
            ret['check_mode'] = True

        if self.repo_filter.update:
            ret['msg'].add('SM Repofile was updated')
            ret['changed'] = True

        # don't do anything if nothing to do, or if a repo isn't found
        # or if check_mode is enabled
        if not (to_enable or to_disable) or self.getNotFound() or check_mode:
            if self.getNotFound():
                self.logger.log(1, 'apply: some repos were not found {}', ret)
                ret['msg'].add('Some repos were not found. Maybe a typo in the repo id, or your entitlements have changed')
            else:
                self.logger.log(3, 'changes: {}', ret)

            return self.fix_msg(ret)

        num_enabled, num_disabled = 0, 0

        if to_enable:
            num_enabled += enable_yum_repositories(*to_enable)

        if to_disable:
            num_disabled += disable_yum_repositories(*to_disable)

        ret['summary']['applied']['enable']=num_enabled
        ret['summary']['applied']['disable']=num_disabled

        if num_enabled != len(to_enable) or num_disabled != len(to_disable):
            ret['msg'].add('Not all repos were enabled/disabled')
            ret['failed']=True
        else:
            ret['msg'].add('Some repos were enabled/disabled')
            ret['changed']=True

        self.logger.log(1, 'apply: changed or error: {}', ret)
        return self.fix_msg(ret)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            repos=dict(type='list', required=True),
            cache_only=dict(type='bool', required=False, default=True),
            ),
        supports_check_mode=True,
    )

    if not HAVE_SM:
        module.fail_json(msg='Subscription Manager required for this module')

    sm_repos = SubscriptionManagerRepos(assign=module.params['repos'], logger=Logger(module), cache_only=module.params['cache_only'])
    try:
        ret = sm_repos.apply(module.check_mode)
        module.exit_json(**ret)

    except Exception, e:
        module.fail_json(msg=str(e))

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
