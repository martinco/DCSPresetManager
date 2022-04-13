import copy

from .modules import get_module, get_module_from_dcs_type
from .utils import as_json


class Profile(dict):
    """
    For now, a profile is just a dict of modules
    """

    def __init__(self, name, parent=None, content=None):
        super().__init__()
        self.name = name
        self.parent = parent

        self['modules'] = {}
        self['update_groups'] = True

        if content:

            self['update_groups'] = content.get('update_groups', True)

            for module_name, data in content.get('modules', {}).items():
                module = get_module(module_name)
                if module:
                    self['modules'][module.name] = module(data)

        # Register self if we have a profiles object
        if self.parent is not None:
            self.parent[self.name] = self

    def __getattr__(self, key):
        """
        We use getattr and will transpose the raw data to display data
        """
        try:
            return self.__dict__[key]
        except KeyError:
            pass

        if key in self:
            return self[key]

        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, key))

    def get_module(self, module_class):
        if module_class.name not in self['modules']:
            self['modules'][module_class.name] = module_class()
        return self['modules'][module_class.name]

    def by_dcs_type(self, dcs_type):
        module = get_module_from_dcs_type(dcs_type)
        if not module or module.name not in self['modules']:
            return None
        return self['modules'][module.name]

    def clone(self, name):
        return Profile(name, self.parent, copy.deepcopy(self))

    def as_json(self):
        return as_json(self)
