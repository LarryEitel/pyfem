import ctrs
#from . import lnk, put, post


def doit(app, cmd):
    debug = app.g['logger'].debug
    fldClss = dict(emails='Email')

    debug(u'\n' + (u'_'*50) + u'\n' + cmd + u'\n' + (u'_'*50))
    params = cmd.split('|')
    fn = params.pop(0)

    if fn == 'putPush':
        # example: 'putPush|Prs.lwe.emails|address:steve@apple.com|typ:work'
        uri = params.pop(0).split('.')
        _cls = uri[0]
        slug = uri[1]
        fld = uri[2]
        data = dict(_cls=_cls, query=dict(slug=slug))
        fldCls = fldClss[fld]

        # get flds to set
        flds = dict([(v.split(':')[0], v.split(':')[1]) for v in params])
        flds['_cls'] = fldCls
        flds['_types'] = [fldCls]

        data['update'] = dict(actions={'$push': dict(flds={fld: [flds]})})
        print data
        data = {'query': {'slug': 'lwe'}, '_cls': 'Prs', 'update': {'actions': {'$push': {'flds': {'emails': [{'_types': ['Email'], 'typ': 'work', '_cls': 'Email', 'address': 'timothy@ms.com'}]}}}}}

        return app.put(**data)


    if fn == 'lnkAdd':
        # example: 'lnkAdd|Cmp.kirmse|Cmp.ni|area-company'
        chld_ = params[0].split('.')
        par_ = params[1].split('.')
        role_ = params[2]
        return app.lnkAdd(**dict(
            chld_=
                dict(
                    _cls=chld_[0],
                    slug=chld_[1]),
            par_=
                dict(
                    _cls=par_[0],
                    slug=par_[1]),
            role_=role_))
