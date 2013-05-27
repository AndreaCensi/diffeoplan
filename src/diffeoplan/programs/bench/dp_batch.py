from .bench_jobs import create_bench_jobs
from diffeoplan.programs import DP
from quickapp  import QuickApp
from diffeoplan  import get_conftools_batches, get_dp_config
from quickapp import iterate_context_names


__all__ = ['DPBatch']


class DPBatch(DP.get_sub(), QuickApp):
    """ Runs batch planning experiments from batch configuration files. """

    cmd = 'batch'
    usage = 'batch --sets=<sets>'

    def define_options(self, params):
        params.add_string('batches', default='*',
                          help="Comma-separated list of batches.")
        
    def define_jobs_context(self, context):
        batches_library = get_conftools_batches()
        batches = batches_library.expand_names(self.options.batches)
        
        config = get_dp_config()
        for c, id_batch in iterate_context_names(context, batches):
            spec = batches_library[id_batch]
            algos = config.algos.expand_names(spec['algorithms']) 
            testcases = config.testcases.expand_names(spec['testcases']) 
            create_bench_jobs(c, algos=algos, testcases=testcases)
        

