import datetime
from bson import ObjectId
from utils import myyaml
import ctrs
from app import app

def scenario_1():
    to_yaml = ctrs.d.to_yaml
    debug   = app.logger.debug
    Put = ctrs.put.Put()
    Lnk = ctrs.lnk.Lnk()
    Post = ctrs.post.Post()

    Post.cmd('Usr|slug:lwe|uNam:lwe|fNam:Larry|fNam2:Wayne|lNam:Stooge')
    Post.cmd('Cmp|slug:ni|cNam:GSNI|typ:company')
    Post.cmd('Cmp|slug:kirmse|cNam:Kirmse|typ:area')
    Post.cmd('Cmp|slug:unit104|cNam:104|typ:unit')
    Post.cmd('Cmp|slug:troop1031|cNam:1031|typ:troop')
    Post.cmd('Pl|slug:atlanta-ga|city:Atlanta')
    Post.cmd('Cmp|slug:ms|cNam:MS')
    Put.cmd('push|Cmp.ms.tels|text:123 456 7890|typ:work')
    Put.cmd('push|Cmp.ni.tels|text:123 456 7890|typ:work')
    Put.cmd('push|Cmp.ni.emails|address:steve@apple.com|typ:work')
    Put.cmd('set|Cmp|q:slug:ni,emails.address:steve@apple.com,emails.typ:work|emails.$.address:bill@ms.com|emails.$.typ:home')
    Put.cmd('set|Cmp|q:slug:ni|cNam:New Name')
    Lnk.cmd('add|Cmp.kirmse|Cmp.ni|area-company')
    Lnk.cmd('add|Cmp.unit104|Cmp.kirmse|unit-area')
    Lnk.cmd('add|Cmp.troop1031|Cmp.unit104|troop-unit')
    Lnk.cmd('add|Cmp.ni|Pl.atlanta-ga|office')



def go():
    from mdls import Email, Prs

    cnts = myyaml.pyObj(self.tests_data_yaml_dir + 'cnts.yaml')

    for doc_dict in cnts.itervalues():
        doc = Prs(**doc_dict)
        doc.save()
        assert doc.id
        coll = doc._get_collection()
        ret = coll.find_one({'_id': doc.id})
        pass
