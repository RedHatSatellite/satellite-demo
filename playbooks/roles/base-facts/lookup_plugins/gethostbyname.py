from ansible.errors import AnsibleError, AnsibleParserError
from ansible.plugins.lookup import LookupBase
from socket import gethostbyname

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class LookupModule(LookupBase):

    def run(self, terms, variables=None, **kwargs):

        ret = []

        for term in terms:
            display.debug("gethostbyname: %s" % term)

            try:
                ret.append(gethostbyname(term))
            except Exception as e:
                raise AnsibleError("Unable to lookup '{}': {}".format(term, e))

        return ret
