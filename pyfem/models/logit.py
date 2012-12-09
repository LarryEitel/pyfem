import datetime

def logit(usr, baseDocDict, targetDocDict, method=''):
    now = datetime.datetime.utcnow()
    resp = {}
    status = 200
    updtFlds = {}

    if not 'cOn' in targetDocDict or not 'cBy' in baseDocDict:
        updtFlds['cBy'] = targetDocDict['cBy'] = usr['OID']
        updtFlds['cOn'] = targetDocDict['cOn'] = now
        if usr['at']:
            updtFlds['cAt'] = targetDocDict['cAt'] = usr['at']


    if not 'oOn' in baseDocDict or not 'oBy' in baseDocDict:
        updtFlds['oBy'] = targetDocDict['oBy'] = usr['OID']
        updtFlds['oOn'] = targetDocDict['oOn'] = now
        if usr['at']:
            updtFlds['oAt'] = targetDocDict['oAt'] = usr['at'] # lattitude, longitude (x,y)


    updtFlds['mBy'] = targetDocDict['mBy'] = usr['OID']
    updtFlds['mOn'] = targetDocDict['mOn'] = now
    if usr['at']:
        updtFlds['mAt'] = targetDocDict['mAt'] = usr['at']


    resp['doc'] = targetDocDict
    resp['updtFlds'] = updtFlds

    return {'response': resp, 'status': status}

