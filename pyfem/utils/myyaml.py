import os.path
from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# http://pyyaml.org/wiki/PyYAMLDocumentation

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


def pyObj(yamlFilePath):
    yamlFilePath += '.yaml' if '.yaml' not in yamlFilePath else ''
    "Returns python object from yaml file."
    if not os.path.exists(yamlFilePath):
        raise Exception('File does not exist: %s' % yamlFilePath)

    return load(open(yamlFilePath, 'r'), Loader=Loader)
