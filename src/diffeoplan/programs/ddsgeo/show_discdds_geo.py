from reprep import Report
from diffeoplan.library.analysis.structure.diffeo_structure import DiffeoStructure
from diffeoplan.programs.main import DP
from quickapp import QuickApp
from diffeo2dds import get_conftools_discdds
from bootstrapping_olympics.utils.natsorting import natsorted
from quickapp.app_utils.subcontexts import iterate_context_names



__all__ = ['DPShowGeo']

class DPShowGeo(DP.get_sub(), QuickApp):
    """ Shows the intrinsic structure of a DDS (DiffeoStructure) """

    cmd = 'show-discdds-geo'
    usage = 'show-discdds-geo  -d <distances> -t <testcases>'

    def define_options(self, params):
        params.add_string('discdds', default='*', short='d',
                          help="Comma-separated list of discdds. Can use *.")
        params.add_float('tolerance', default=0.3,
                          help="Normalized tolerance")
        
    def define_jobs_context(self, context):
        discdds_library = get_conftools_discdds()
        discdds = discdds_library.expand_names(self.options.discdds)
        discdds = natsorted(discdds)
        
        tolerance = self.options.tolerance
        
        for c, id_discdds in iterate_context_names(context, discdds):
            r = c.comp_config(report_dds_geometry, id_discdds, tolerance=tolerance)
            c.add_report(r, 'dds_geometry', tolerance=tolerance, dds=id_discdds)
        
        
def report_dds_geometry(id_discdds, tolerance):
    dds = get_conftools_discdds().instance(id_discdds)
    r = Report('dds_geometry-%s-%s' % (id_discdds, tolerance))
    ds = DiffeoStructure(dds, tolerance=tolerance)
    with r.subsection('display') as r:
        ds.display(r)
    
    with r.subsection('show_reduction_steps') as r:
        ds.show_reduction_steps(r, max_nsteps=5)
        
    with r.subsection('show_reduction') as r:
        ds.show_reduction(r)
        
    return r

