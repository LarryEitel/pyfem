Pseudo ctrs Operations

NOTES:
TODOs:
QUESTIONS:


# ctrs.py
class Generic
    def __init__(self, me, es = None):
        #: Doc comment for instance attribute me
        self.me = me
        self.es = es
    def post(self, **kwargs):
        session    = kwargs['session'] if 'session' in kwargs else {}
        me         = self.me
        _c         = kwargs['_c']
        model      = getattr(mdls, _c)
        collNam    = model.meta['collection']
        collNamTmp = model.meta['collNam'] + '_tmp'
        coll       = me[collNam]
        collTmp    = me[collNamTmp]

        # QUESTION: How to init an empty schematic model with defaults, etc.
        # if no OID exists, this is a new doc. Will need to generate a temporary doc to work with.
        if not 'OID' in kwargs:
            # create tmpDoc
            # init model for this doc
            m      = model({})
            m.id   = barak.nextId()
            m.slug = barak.slugify()
            tmpOID = str(collTmp.insert(m.to_python(), safe = True))
            # save tmpOID in session
            pass

        # does tmpDoc already exist
        elif 'tmpOID' in session:
            tmpOID = session['tmpOID']

        # if OID exists, need tmpOID
        elif not 'OID' in kwargs:
            pass

ctrs.generic.get 
ctrs.generic.put
ctrs.generic.nextId
