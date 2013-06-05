from .bench_jobs import create_bench_jobs
from diffeoplan.programs import DP
from quickapp  import QuickApp
from diffeoplan  import get_conftools_batches
from quickapp import iterate_context_names


__all__ = ['DPBatch']


class DPBatch(DP.get_sub(), QuickApp):
    """ Runs batch planning experiments from batch configuration files. """

    cmd = 'batch'
    usage = 'batch --sets=<sets>'

    def define_options(self, params):
        params.add_string('batches', default='*',
                          help="Comma-separated list of batches.")
        params.add_string_list('alltestcases', default=[],
                          help="List of all available tescases")
        
    def define_jobs_context(self, context):
        batches_library = get_conftools_batches()
        batches = batches_library.expand_names(self.options.batches)
        
        for c, id_batch in iterate_context_names(context, batches):
            c.extra_report_keys['batch'] = id_batch
            batch = batches_library.instance(id_batch)
            create_bench_jobs(c, batch, alltestcases=self.options.alltestcases)
        

