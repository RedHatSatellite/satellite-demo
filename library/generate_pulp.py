#!/usr/bin/env python
# vim: sw=4 ai ts=4 expandtab
import sys
from ansible.module_utils.urls import fetch_url

from yum import YumBase
from yum.parser import varReplace

_verbosity_override = 4

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
        raise                               # raise the exception with stack
    finally:
        new_out.flush()                     # grab the output
        (sys.stdout, sys.stderr) = sav_out  # restore it
        if ex:                              # if there was an error, then print it out
            sys.stderr.write(str(new_out))

yum = YumSingleton()                        # use the same instance
del YumSingleton                            # prevent anyone else from creating it

class Logger(object):
    def __init__(self, ansible):
        self.logger = ansible

    def log(self, v, fmt, *kwargs):
        if v <= self.logger._verbosity:
            s = str(fmt) if not kwargs else fmt.format(*kwargs)
            self.logger.log(s)

class PulpMirror(object):
    @staticmethod
    def addSlash(url):
        return url if url[-1] == '/' else url + '/'

    @staticmethod
    def stripSlash(url):
        return url if url[-1] != '/' else url[:-1]

    def contentType(self, resp):
        _ct = resp[1]['content-type'] if 'content-type' in resp[1] else 'text/plain'
        ct=[ x.strip() for x in _ct.split(';') ]
        self.logger.log(4, [resp[1]['status'], ct])
        return ct

    def __init__(self,
            url,
            module,
            repo_name=None,
            base_url='https://cdn.redhat.com/content/'):
        if not url:
            raise ValueError('URL can not be blank!')
        self.url = PulpMirror.stripSlash(url)
        self.repo_name = repo_name
        self.base_url = PulpMirror.addSlash(base_url)
        self.module = module
        self.logger = Logger(module)

    def grabRepo(self, url, path, repos):
        self.logger.log(2, 'grabRepo looking at: {}', url)
        # repos have a repomd.xml file
        resp = fetch_url(self.module, url + '/repodata/repomd.xml')
        content_type=self.contentType(resp)
        self.logger.log(4, 'recurseRepos resp: {}', resp)

        # it must be an xml file
        if resp[1]['status'] == 200 and 'text/xml' in content_type:
            r=dict(label='-'.join(path), url=url)
            self.logger.log(1, 'found repo: {}', r)
            return repos + [r]

        return repos

    def recurseRepos(self, url, path=['pulp'], repos=[]):
        # properly formed Red Hat pulp repos have a listing file
        self.logger.log(4, 'recurseRepos looking at: {}', url)
        resp = fetch_url(self.module, url + '/listing')

        content_type=self.contentType(resp)

        # it needs to be a text file or plain
        if resp[1]['status'] == 200 and 'text/plain' not in content_type:
            return repos

        # some malformed pulp mirrors might have a listing in the repodir
        # so check anyways
        if resp[1]['status'] == 404 or resp[1]['status'] == 200:
            # might be a repo
            repos = self.grabRepo(url, path, repos)

        # can't see anything listings
        if resp[1]['status'] != 200:
            return repos

        content=resp[0].read()

        # ignore blank listings
        if not content:
            return repos

        # check the subdirs
        children=content.split('\n')
        for child in children:
            repos=self.recurseRepos(url+'/'+child, path+[child], repos)

        return repos

    def findRepos(self):
        if not self.url:
            return {}
        repos = self.recurseRepos(self.url)
        return dict([ (x['label']+'-rpms', x['url']) for x in repos ])

    def getYumRepos(self):
        return dict( [ ( x[0], x[1].baseurl ) for x in  yum.repos.repos.items() if x[1].enabled ] )

def main():
    module = AnsibleModule(
        argument_spec=dict(
            url=dict(type='str', required=True),
            base_url=dict(type='str', required=False, default='https://cdn.redhat.com/content/'),
            ),
        supports_check_mode=True,
    )

    if _verbosity_override > 0:
        module._verbosity = _verbosity_override

    pulp = PulpMirror(url=module.params['url'], base_url=module.params['base_url'], module=module)
    try:
        ret = pulp.findRepos()
        # ret = pulp.getYumRepos()
        module.exit_json(**ret)

    except Exception, e:
        module.fail_json(msg=str(e))

from ansible.module_utils.basic import *
if __name__ == "__main__":
    main()
