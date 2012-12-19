import os.path
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# http://pyyaml.org/wiki/PyYAMLDocumentation

def loadMongoCollection(yamlFilePath):
	pass


def pyObj(yamlFilePath):
    yamlFilePath += '.yaml' if '.yaml' not in yamlFilePath else ''
    "Returns python object from yaml file."
    if not os.path.exists(yamlFilePath):
        raise Exception('File does not exist: %s' % yamlFilePath)

    return load(open(yamlFilePath, 'r'), Loader=Loader)
