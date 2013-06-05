from conf_tools import ConfigMaster, ObjectSpec
from contracts import contract

__all__ = ['get_dp_config',
           'get_conftools_planning_algos',
           'get_conftools_testcases',
           'get_conftools_batches']

class DiffeoplanConfigMaster(ConfigMaster):
    def __init__(self):
        ConfigMaster.__init__(self, 'dp')
        
        from diffeoplan import DiffeoPlanningAlgo
        from diffeoplan import TestCase
        from diffeoplan import DiffeoplanBatch
  
        self.algos = \
            self.add_class_generic('algos', '*.algos.yaml',
                                   DiffeoPlanningAlgo)
        self.testcases = \
            self.add_class_generic('testcases', '*.tc.yaml', TestCase)
        
        self.batches = \
            self.add_class_generic('batches', '*.batch.yaml', DiffeoplanBatch)
        
  
    def get_default_dir(self):
        from pkg_resources import resource_filename  # @UnresolvedImport
        return resource_filename("diffeoplan", "configs")

 
get_dp_config = DiffeoplanConfigMaster.get_singleton

 
@contract(returns=ObjectSpec)
def get_conftools_planning_algos():
    """ Returns the object responsible for instancing UncertainImages. """
    return get_dp_config().algos

@contract(returns=ObjectSpec)
def get_conftools_testcases():
    """ Returns the object responsible for instancing UncertainImages. """
    return get_dp_config().testcases

@contract(returns=ObjectSpec)
def get_conftools_batches():
    return get_dp_config().batches


