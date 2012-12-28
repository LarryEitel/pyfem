import os.path
import datetime
from bson import ObjectId
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from app import app

# http://pyyaml.org/wiki/PyYAMLDocumentation

class PyYamlInline(object):
    @staticmethod
    def dump(val):
        trueValues = ['true', 'on', '+', 'yes', 'y']
        falseValues = ['false', 'off', '-', 'no', 'n']

        if type(val) == list:
            inlinedumplist = PyYamlInline.dumpList(val)
            #app.logger.debug('inlinedumplist: ' + inlinedumplist)
            return inlinedumplist
        elif type(val) == dict:
            inlinedumpdict = PyYamlInline.dumpDict(val)
            #app.logger.debug('inlinedumpdict: ' + inlinedumpdict)
            return inlinedumpdict
        elif type(val) == datetime.datetime:
            return val.__str__()
        elif type(val) == int:
            return val
        elif type(val) == ObjectId:
            return val.__str__()
        else:
            return val

    @staticmethod
    def dumpDict(doc):
        yamlDumper = PyYamlDumper()
        dumperdump = yamlDumper.dump(doc)
        #app.logger.debug('dumpDict:dumperdump: ' + dumperdump)
        return dumperdump

    @staticmethod
    def dumpList(vals):
        output = []
        for val in vals:
            yamlDumper = PyYamlDumper()
            dumperdump = yamlDumper.dump(val)
            #app.logger.debug('dumpList:dumperdump: ' + dumperdump)
            output.append(dumperdump)

            #inlinedump = PyYamlInline.dump(val)
            #app.logger.debug('inlinedump:' + inlinedump)
            #output.append(inlinedump)
        return u'[%s]' % ', '.join(output)



class PyYamlDumper(object):
    def dump(self, input, indent=0):
        output = u''
        prefix = (u' '*indent) if indent else ''

        ignoreFlds = ['_types', '_cls', '_id', 'mOn', 'oOn']
        ndxFlds = ['_c', 'slug', 'sId', 'cNam', 'prefix', 'fNam', 'fNam2', 'lNam', 'lNam2', 'suffix']
        trueValues = ['true', 'on', '+', 'yes', 'y']
        falseValues = ['false', 'off', '-', 'no', 'n']

        valType = type(input)
        if valType == dict:
            items = {}
            fldPos = 1000
            for key, val in input.iteritems():
                if val and not key in ignoreFlds:
                    item = u"%s%s:" % (prefix, key)
                    item += self.dump(val, indent + 2)

                    if key in ndxFlds:
                        sortPos = ndxFlds.index(key)
                    else:
                        sortPos = fldPos
                        fldPos += 1

                    items[sortPos] = item

            if items:
                output += '%s' % (('\n' + '').join([v for v in items.itervalues()]))

        elif valType == list:
            items = []
            for i, val in enumerate(input):
                if val:
                    item = ''
                    item += self.dump(val, indent + 2)
                    item = item.lstrip()

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
        else:
            output += ' ' + input

        return output

class PyYaml(object):
    @staticmethod
    def dump(doc, indent=0):
        yamlDumper = PyYamlDumper()
        app.logger.debug(doc['slug'] + ':')
        yml = yamlDumper.dump(doc, 2)
        app.logger.debug(yml)
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