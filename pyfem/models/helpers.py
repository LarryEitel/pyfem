import datetime
import models

def recurseValidate(doc, doc_class, key, val, attrPath, doc_errors):
    '''this will be called by recursiveDoc function and be executed on each doc/embedded doc'''
    doc = doc_class(**val)
    errors = doc.validate()
    if errors:
        error = {'attrPath': '.'.join(attrPath), 'fld':key, '_cls': val['_cls'], 'errors': errors}
        if 'eId' in val and val['eId']:
            error['eId'] = val['eId']
        doc_errors.append(error)


def recurseVOnUpSert(doc, doc_class, key, val, attrPath, doc_errors):
    '''this will be called by recursiveDoc function and be executed on each doc/embedded doc'''
    if '_cls' in val:
        if hasattr(doc_class, 'vOnUpSert'):
            resp = doc_class.vOnUpSert(val)
            if resp['errors']:
                error = {'attrPath': '.'.join(attrPath), 'fld':key, '_cls': val['_cls'], 'errors': resp['errors']}
                if 'eId' in val and val['eId']:
                    error['eId'] = val['eId']
                doc_errors.append(error)


def recurseDoc(doc, key, val, recurseFn, attrPath, doc_errors):
    '''Recursively traverse model class fields executing recurseFn function on any docs/embedded docs'''
    keyvals = {}
    if type(val) == dict:
        doc_class = getattr(models, val['_cls']) if '_cls' in val else None
        if doc_class:
            # this enables using same recursive funct to execute something on any docs/embedded docs
            recurseFn(val, doc_class, key, val, attrPath, doc_errors)
        for key in val.keys():
            if key in ['_cls', '_types', '_eIds']:
                keyvals[key] = val[key]
                continue
            val[key] = recurseDoc(val, key, val[key], recurseFn, attrPath + [key], doc_errors)
            x=0
    elif type(val) == list:
        if not len(val) or not '_cls' in val[0]:
            return val

        # Let's make sure members of this list have eId's initialized
        if not '_eIds' in doc:
            doc['_eIds'] = {}

        # do all the list items have eId's? If so, set
        max_eId = 0
        allItemsHave_eId = True
        for item in val: # val is a list here
            if not 'eId' in item:
                allItemsHave_eId = False
                break
            if item['eId'] > max_eId:
                max_eId = item['eId']

        # if all items do not have an eId, reset all to default (incremented from 1)
        if not allItemsHave_eId:
            for i in range(len(val)):
                val[i]['eId'] = i + 1

        # either set next eId for this list to max eId's or count of items + 1
        doc['_eIds'][key] = max_eId + 1 if allItemsHave_eId else len(val) + 1
        theList = doc[key]
        if len(theList) and '_cls' in theList[0]:
            listItem_cls = getattr(models, theList[0]['_cls'])
            if hasattr(listItem_cls, 'validateList'):
                listItem = listItem_cls(**theList[0])
                errors = listItem.validateList(theList)
                if errors:
                    doc_errors.append({'attrPath': '.'.join(attrPath), 'fld':key, 'errors': errors})


        # now go ahead and process each item in the list for possible further recursion
        for i in range(len(val)):
            recurseDoc(val[i], key, val[i], recurseFn, attrPath + [str(val[i]['eId'])], doc_errors)

        return val
    else:
        return val

def recurseValidateAndVOnUpSert(m):
    '''recursively handle validate and execute any doc.vOnUpSert functions'''
    docData = m.validDocData()
    doc = docData

    doc_errors = []

    attrPath = []
    recurseDoc(docData, m._cls, docData, recurseValidate, attrPath, doc_errors)

    if doc_errors:
        return doc_errors

    attrPath = []
    recurseDoc(docData, m._cls, docData, recurseVOnUpSert, attrPath, doc_errors)

    if doc_errors:
        return doc_errors

    for field in m._fields.keys():
        if field in docData:
            setattr(m, field, docData[field])

    return m

def docCleanData(m_data):
    '''Models contains some fields with keys and/or vals == None. Return dict with only value keys that also have value'''
    ks = {}
    for k, v in m_data.iteritems():
        if v and k:
            ks[k] = v

    return ks

#def docCleanData(m_data):
    #ks = {}
    #for k, v in m_data.iteritems():
        #if v and k:
            #ks[k] = v

    #return ks

#def docCloneToTmp(m, tmpClass):
    #m_dict = m._data
    #ks = {}
    #for k, v in m_dict.iteritems():
        #if v and k:
            #ks[k] = v

    #ks['cloned_id'] = m.id
    #del ks['sId']
    #return tmpClass(**ks)

#def docClone(m):
    #m_dict = m._data
    #ks = {}
    #for k, v in m_dict.iteritems():
        #if v and k:
            #ks[k] = v

    #ks['cloned_id'] = m.id
    #del ks['sId']
    #return m.__class__(**ks)
