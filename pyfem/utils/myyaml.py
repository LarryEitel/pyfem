import os.path
import datetime
import time
from bson import ObjectId
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from app import app

# http://pyyaml.org/wiki/PyYAMLDocumentation

class PyYamlDumper(object):
    def dump(self, input, indent=0, allflds=False, onlyflds=[]):
        output = u''
        prefix = (u' '*indent) if indent else ''

        ignoreFldsForSure = [ '_types', '_cls']
        ignoreFlds = ['sId', '_id', 'mOn', 'oOn', 'vFullName', 'pths', 'pars']

        ndxFlds = ['_c', 'cls', '_id', 'slug', 'role', 'vNam', 'cNam', 'prefix', 'fNam', 'fNam2', 'lNam', 'lNam2', 'suffix']
        trueValues = ['true', 'on', '+', 'yes', 'y']
        falseValues = ['false', 'off', '-', 'no', 'n']

        valType = type(input)
        if valType == dict:
            items = {}
            fldPos = 1000
            for key, val in input.iteritems():
                if (val
                    and (not onlyflds and (not key in ignoreFlds or allflds) and not key in ignoreFldsForSure)
                    or (onlyflds and key in onlyflds)):

                    item = u"%s%s:" % (prefix, key)
                    item += self.dump(val, indent + 2)

                    if onlyflds:
                        sortPos = onlyflds.index(key)
                    elif key in ndxFlds:
                        sortPos = ndxFlds.index(key)
                    else:
                        sortPos = fldPos
                        fldPos += 1

                    items[sortPos] = item

            if items:
                output += '%s' % (('\n' + '').join([items[k] for k in sorted(items)]))

        elif valType == list:
            items = []
            for i, val in enumerate(input):
                if val:
                    item = self.dump(val, indent + 2).lstrip()
                    items.append(u"%s%s%s" % (prefix, '- ', item))
            if items:
                s = "%s" % (u"%s%s%s" % ('\n', '', '%s' % ('\n').join(items)))
                output += s

        elif valType == datetime.datetime:
            output += ' ' + input.__str__()
        elif valType == int:
            output += ' ' + input.__str__()
        elif valType == ObjectId:
            output += ' ' + input.__str__()
        elif valType == bool:
            output += ' ' + 'true' if input else 'false'
        else:
            output += ' ' + input

        return output

class PyYaml(object):
    @staticmethod
    def dump(docs, allflds=False, logCollNam='cnts', onlyflds=[]):
        if logCollNam:
            logFName = app.config['HOME_PATH']+'logs/mongo_' + logCollNam + 'log.yaml'
            logFH = open(logFName, 'w')


        yamlDumper = PyYamlDumper()
        yml = '# ' + logCollNam + ': ' + time.ctime()
        for doc in docs:
            yml += '\n' + doc['slug'] + ':' + '\n'
            yml += yamlDumper.dump(doc, 2, allflds, onlyflds)

        if logCollNam:
            logFH.write('\n')
            logFH.write(yml)
            logFH.close()

        return yml

def postToMongo(post, yamlFilePath):
    yamlFilePath += '.yaml' if '.yaml' not in yamlFilePath else ''
    if not os.path.exists(yamlFilePath):
        raise Exception('File does not exist: %s' % yamlFilePath)

    dat = load(open(yamlFilePath, 'r'), Loader=Loader)
    collection_name = dat['meta']['collection_name']
    docs = dat['data']

    response     = {}
    docs_handled = {}
    status       = 200

    post_errors  = []
    total_errors = 0

    added = 0
    for docData in docs.itervalues():
        errors      = {}
        doc_info    = {}
        resp        = post(docData)

        if not resp['status'] == 200:
            error = {'docData': docData, 'errors': resp['errors']}
            post_errors.append(error)
        else:
            _id = resp['response']['docs'].keys()[0]
            doc = resp['response']['docs'][_id]
            docs_handled[_id]   = doc

    response['total_inserted'] = len(docs_handled)

    if post_errors:
        response['total_invalid'] = len(post_errors)
        response['errors']        = post_errors
        status                    = 500
    else:
        response['total_invalid'] = 0

    response['docs'] = docs_handled
    response['yamlData'] = dat

    return {'response': response, 'status': status}

def lTrimCompare(yml, expect):
    '''Convenience funct to compare outputted yaml with inline snippet. Inline snippet is indented in the code. This function left trims the white space.'''
    i = 2
    while expect[i] == ' ': i += 1
    return yml.strip('\n') == expect.replace(u' '*(i-1), '').strip('\n')


def pyObj(yamlFilePath):
    yamlFilePath += '.yaml' if '.yaml' not in yamlFilePath else ''
    "Returns python object from yaml file."
    if not os.path.exists(yamlFilePath):
        raise Exception('File does not exist: %s' % yamlFilePath)

    return load(open(yamlFilePath, 'r'), Loader=Loader)