import os
from diffeoplan.programs import DP
from quickapp import QuickApp
from .makelogcases import make_logcases
from diffeo2dds import get_conftools_discdds


__all__ = ['DPLogCases']

class DPLogCases(DP.get_sub(), QuickApp):
    """ Creates planning test cases from log files. """
    cmd = 'logcases'
    usage = 'logcases -s <stream> --dds <id_discdds> -n <number> -d <delay>'

    def define_options(self, params):
        params.add_string('stream', short='s', help='ID stream')
        params.add_string('dds', help='DDS to use -- used for converting commands to plan indices')
        params.add_string('pattern', default=None,
                          help='Pattern for ID of testcases; must contain %d to be given index.')
        params.add_int('n', default=1, help='Number of test cases')
        params.add_int('seed', default=42, help='Seed for randomly choosing images.')
        params.add_int('delay', default=1, help='Delay between data (>=1).')
        
    def define_jobs_context(self, context):
                
        id_stream = self.options.stream
        id_discdds = self.options.dds
        delay = self.options.delay
        
        
        id_tc_pattern = self.options.pattern
        if id_tc_pattern is None:
            id_tc_pattern = 'tc_%s_d%d_' % (id_discdds, delay) + '%03d'    
        self.info('Creating test cases with pattern %r' % id_tc_pattern)
        
        outdir = os.path.join(context.get_output_dir(), id_discdds)
        if not os.path.exists(outdir):
            os.makedirs(outdir)
        
        context.comp_config(make, id_discdds, outdir,
                           seed=self.options.seed, id_stream=id_stream,
                           n=self.options.n, delta=delay,
                           id_discdds=id_discdds, id_tc_pattern=id_tc_pattern)
                           
                           
def make(id_discdds, outdir, **params):
    discdds_library = get_conftools_discdds()
    discdds = discdds_library.instance(id_discdds)
    cases = make_logcases(id_discdds=id_discdds, discdds=discdds, **params)
        
    for tc in cases:
        tc.save(outdir)    

    

    
