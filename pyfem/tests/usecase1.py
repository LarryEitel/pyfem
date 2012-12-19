from utils import myyaml
import models

class UseCase1():
    '''Convenient tools for automatically loading sample data from yaml files'''
    def __init__(self, yaml_path):
        self.yaml_path = yaml_path

    def load(self, uc_file):
        fname = self.yaml_path + uc_file + '.yaml'
        try:
            self.dat = myyaml.pyObj(fname)
        except:
            raise Exception('Failed to load yaml: ' + fname)

        self.cmds = self.dat['cmds']
        self.data = self.dat['data']


    def run_all(self):
        # loop through all commands for a usecase
        cmds = []
        for cmd in self.cmds:
            for _cls, params in cmd.iteritems():
                cmds.append(self.run(_cls, params))

        return cmds


    def run(self, _cls, params):
        model_class = getattr(models, _cls)
        slug = params['slug']

        # get data for this item
        docData = self.dat['data'][slug]

        # if a count value, use it to repeat else 1
        doc = model_class(**docData)
        doc.save()
        assert doc.id
        return doc