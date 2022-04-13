from ..module import Module

MODULES_BY_NAME = {}
MODULES_BY_DCS_TYPE = {}

for module in Module.__subclasses__():
    MODULES_BY_NAME[module.name] = module
    MODULES_BY_DCS_TYPE.update(dict((x, module) for x in module.dcs_types))


def get_module_from_dcs_type(dcs_type):
    if dcs_type in MODULES_BY_DCS_TYPE:
        return MODULES_BY_DCS_TYPE[dcs_type]
    return None


def get_module(module_class):
    if module_class in MODULES_BY_NAME:
        return MODULES_BY_NAME[module_class]
    return None
