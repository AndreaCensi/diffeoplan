from diffeo2dds import get_conftools_uncertain_image_distances
from diffeoplan import get_conftools_testcases
from diffeoplan.programs import DP
from quickapp import iterate_context_names, QuickApp
import warnings
from diffeoplan.utils.in_a_while import InAWhile

__all__ = ['DPDistFPS']


class DPDistFPS(DP.get_sub(), QuickApp):
    cmd = 'dist-fps'
    usage = 'dist-fps  -d <distances> -t <testcases>'

    def define_options(self, params):
        params.add_string('distances', default='*', short='d',
                          help="Comma-separated list of distances. Can use *.")
        params.add_string('testcases', default='*', short='t',
                          help="Comma-separated list of testcases. Can use *.")
        params.add_int('repeat', default=1,
                          help="Repeat many times")
        
    def define_jobs_context(self, context):
        
        library = get_conftools_uncertain_image_distances()
        distances = library.expand_names(self.options.distances)
        
        library = get_conftools_testcases()
        testcases = library.expand_names(self.options.testcases)
    
        self.info('Using distances: %s' % distances)
        self.info('Using testcases: %s' % testcases)
       
        for c, id_distance in iterate_context_names(context, distances):
            c.comp_config(benchmark_distance, id_distance, testcases,
                          repeat=self.options.repeat)
       

def benchmark_distance(id_distance, testcases, repeat):

    library_testcases = get_conftools_testcases()
    testcases = map(library_testcases.instance, testcases)
    d = get_conftools_uncertain_image_distances().instance(id_distance)
        
    fps = InAWhile()
    for _ in range(repeat):
        for tc in testcases: 
            fps.its_time()
            result = d.distance(tc.y0, tc.y1)
            print('%s / %s: %s (%s)' % (id_distance, tc.id_tc, result, tc.true_plan))
    print('%s: frames per second: %s' % (id_distance, fps.fps()))
 
