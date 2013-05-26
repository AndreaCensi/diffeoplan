from bootstrapping_olympics.utils import natsorted
from diffeo2dds import get_conftools_discdds
from diffeoplan.programs.ddsgeo.diffeo_system_bounds import DiffeoSystemBounds
from diffeoplan.programs.main import DP
from quickapp.app_utils import iterate_context_names
from quickapp import QuickApp
from reprep import Report


__all__ = ['DPShowFill']

class DPShowFill(DP.get_sub(), QuickApp):
    """ Shows the geometry of a DDS (DiffeoSystemBounds) """

    cmd = 'show-discdds-fill'
    usage = 'show-discdds-fill  -d <distances> -t <testcases>'

    def define_options(self, params):
        params.add_string('discdds', default='*', short='d',
                          help="Comma-separated list of discdds. Can use *.")
        params.add_float('tolerance', default=0.3,
                          help="Normalized tolerance")
        params.add_float('collapse_threshold', default=0,
                          help="Collapse threshold")
        
        params.add_int('num_iterations', short='n', default=100 * 1000,
                          help="Collapse threshold")
        params.add_float('min_visibility', short='v', default=0.5,
                          help="Collapse threshold")

        params.add_float('debug_it', short='v', default=100,
                         help="Debug iterations")

    def define_jobs_context(self, context):
        discdds_library = get_conftools_discdds()
        discdds = discdds_library.expand_names(self.options.discdds)
        discdds = natsorted(discdds)

        for c, id_discdds in iterate_context_names(context, discdds):
            options = self.options
            params = dict(tolerance=options.tolerance,
                     collapse_threshold=options.collapse_threshold,
                     debug_it=options.debug_it,
                     max_it=options.num_iterations,
                     min_visibility=options.min_visibility)
            r = c.comp_config(report_dds_fill, id_discdds, **params)
            c.add_report(r, 'dds_fill', dds=id_discdds, **params)
        
def report_dds_fill(id_discdds, **params):
    dds = get_conftools_discdds().instance(id_discdds)

    r = Report('dds_fill-%s' % id_discdds)
    ds = DiffeoSystemBounds(id_discdds, dds, **params)
    ds.display(r)
    return r


#          
# 
# # @declare_command('show-discdds-fill2',
# #                  'show-discdds-fill2 [<discdds1> <discdds2> ...]')
# def show_discdds_fill2_main(config, parser):
#     """ Displays the intrinsic geometry of a learned DDS """
#     parser.add_option("-o", "--output", help="Output directory",
#                       default='out/dp-show-discdds-fill2/')
#     parser.add_option("-t", "--tolerance", help="Normalized tolerance",
#                       default=0.3, type='float')
#     parser.add_option("--collapse_threshold", help="Collapse threshold",
#                       default=0, type='float')
#     parser.add_option("-n", "--num_iterations", help="Max number of iterations",
#                       default=100000, type='int')
#     parser.add_option("-v", "--min_visibility", help="Minimum visibility",
#                       default=0.5, type='float')
#     parser.add_option("--debug_it", help="Debug iterations",
#                       default=100, type='float')
# 
#     options, which = parser.parse()
#     
#     outdir = options.output 
#   
#     if not which:
#         todo = config.discdds.keys()  
#     else:
#         todo = config.discdds.expand_names(which)
# 
#     for id_dds in todo:
#         dds = config.discdds.instance(id_dds) 
#         report = Report(id_dds)
#         
#         show_ddsfill2(id_dds, dds, report,
#                      tolerance=options.tolerance,
#                      collapse_threshold=options.collapse_threshold,
#                      debug_it=options.debug_it,
#                      max_it=options.num_iterations,
#                      min_visibility=options.min_visibility)    
#         
#         write_report_files(report, basename=os.path.join(outdir, id_dds))    
# 
# 
# def show_ddsfill2(id_dds, dds, report, **args):
#     ds = DiffeoSystemBounds2(id_dds, dds, **args)
#     ds.display(report)
#          

