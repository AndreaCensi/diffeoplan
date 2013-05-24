from diffeoplan.programs.main import DP
from quickapp.quick_app_base import QuickAppBase
from diffeoplan.configuration.master import get_dp_config

class DPShowConfig(DP.get_sub(), QuickAppBase):
    
    def define_program_options(self, params):
        params.add_flag('verbose')
        params.add_string('type', help="Show only type t objects.",
                          default='*')

    def go(self):
        options = self.get_options()
        allofthem = options.type == '*'
        config = get_dp_config()
        
        if options.type == 'distances' or options.type == True:
            print('Distances:')
            print(config.distances.summary_string_id_desc_patterns())
                 
        if options.type == 'algos' or allofthem:
            print('Algorithms:')
            print(config.algos.summary_string_id_desc_patterns())
        
        if options.type == 'sets' or allofthem:
            print('Batch experiments:')
            print(config.sets.summary_string_id_desc_patterns())
            
        if options.type == 'testcases' or allofthem:
            if options.verbose:
                print('Test cases:')
                print(config.testcases.summary_string_id_desc_patterns())
            else:
                n = len(config.testcases)
                print('There are %d testcases; use -v to show them' % n)
