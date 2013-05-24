from .checks import check_valid_set
from conf_tools import (ConfigMaster, GenericCall, check_generic_code_desc,
    ObjectSpec)
from contracts import contract

__all__ = ['get_dp_config',
           'get_conftools_planning_algos',
           'get_conftools_testcases']

class DiffeoplanConfigMaster(ConfigMaster):
    def __init__(self):
        ConfigMaster.__init__(self, 'dp')
        
        from diffeoplan import TestCase
        from diffeoplan import DiffeoPlanningAlgo
  
        self.algos = \
            self.add_class_generic('algos', '*.algos.yaml',
                                   DiffeoPlanningAlgo)
 
        self.testcases = \
            self.add_class_generic('testcases', '*.tc.yaml', TestCase)
        
        self.sets = self.add_class('sets', '*.batch.yaml', check_valid_set)
  
  
    def get_default_dir(self):
        from pkg_resources import resource_filename  # @UnresolvedImport
        return resource_filename("diffeoplan", "configs")

 
get_dp_config = DiffeoplanConfigMaster.get_singleton

 
@contract(returns=ObjectSpec)
def get_conftools_planning_algos():
    """ Returns the object responsible for instancing UncertainImages. """
    return get_dp_config().algos

contract(returns=ObjectSpec)
def get_conftools_testcases():
    """ Returns the object responsible for instancing UncertainImages. """
    return get_dp_config().testcases
