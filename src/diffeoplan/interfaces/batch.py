from contracts import contract
from conf_tools.utils.wildcards import expand_string


__all__ = ['DiffeoplanBatch']

class DiffeoplanBatch(object):
    """ """
    
    @contract(algorithms='list', testcases='list', discdds='str')
    def __init__(self, algorithms, testcases, discdds):
        self.algorithms = algorithms
        self.testcases = testcases
        self.discdds = discdds
    
    @contract(returns='dict(str:list(str))')
    def get_id_discdds2testcases(self, alltestcases):
        x = {}
        from diffeoplan import get_dp_config
        config = get_dp_config()
        if not alltestcases:
            testcases = config.testcases.expand_names(self.testcases)          
        else:
            testcases = expand_string(self.testcases, alltestcases)

        x[self.discdds] = testcases
        return x
        
