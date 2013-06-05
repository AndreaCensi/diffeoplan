from conf_tools import GlobalConfig
from diffeo2dds_learn import DDSLLearn
from diffeoplan import DPDistStats, DPPredStats, DPShowGeo
from quickapp import QuickApp
from diffeoplan.programs.ddsgeo.show_discdds_fill import DPShowFill
from diffeoplan.programs.logcases.dp_logcases import DPLogCases
from diffeoplan.programs.bench.dp_batch import DPBatch

__all__ = ['DPTR1']

class DPTR1(QuickApp):
    """ Reproduces planning experiments """
    
    def define_options(self, params):
        pass
    
    def define_jobs_context(self, context):
        
        # Load defaults for everybody
        GlobalConfig.global_load_dir('default')
        # Load our specific config
        from pkg_resources import resource_filename  # @UnresolvedImport
        config_dir = resource_filename("dptr1", "configs")
        GlobalConfig.global_load_dir(config_dir)
        
        # So we can load objects we create
        GlobalConfig.global_load_dir(context.get_output_dir())
        
        # get_diffeo2ddslearn_config().load('default')
        
        # First, learn the diffeomorphisms
        stream = "orbit-pt256-80"
        estimator = 'test_ddsest_unc_refine2'  # "n35s"
        max_displ = 0.35
        
        learned = context.subtask(DDSLLearn, estimator=estimator, stream=stream,
                        max_displ=max_displ)
        rm = context.get_resource_manager()
        rm.set_resource(learned, 'discdds', id_discdds='test_ddsest_unc_refine2_orbit-pt256-80')
                
        # dp plearn -s $stream -l n35s -c "clean *summarize*; parmake "
        # dp plearn -s $stream -l n35o -c "clean *summarize*; parmake "        

        distances = "L1,L2,L1w,L2w,cL2,cL1,cD10,D10,cD20,D20,cD30,D30,N10,N20,N30,cN10,cN20,cN30"     
        
        
        # dp dist-stats -o $out/dp-dist-stats -d $distances -s $stream  -c "clean report*; parmake"
        context.subtask(DPDistStats, streams=stream, distances=distances)
        dds_orbit = "%s-%s" % (estimator, stream)
        
        # dp pred-stats -o $out/dp-pred-stats -d $distances -s $stream --dds $stream-n35s -c "clean report*; parmake"
        # dp pred-stats -o $out/dp-pred-stats -d $distances -s $stream --dds $stream-n35o -c "clean report*; parmake"
        context.subtask(DPPredStats,
                        distances=distances, streams=stream, dds=dds_orbit)
        
         
        #  dp1 show-discdds-geo -o $out/dp-show-discdds-geo -t 0.04  dcl4r80
        dds_cl = 'sym-dcl4r-80'
        context.subtask(DPShowGeo, discdds=dds_cl, tolerance=0.4)
        
        #  dp1 show-discdds-geo -o $out/dp-show-discdds-geo h1orbit-pt256-80-n35s 
        context.subtask(DPShowGeo, discdds=dds_orbit, tolerance=0.3)
 
        
        # dp1 show-discdds-fill -o $out/dp-show-discdds-fill -v 0.5 h1orbit-pt256-80-n35s
        context.subtask(DPShowFill, min_visibility=0.5, discdds=dds_orbit)
        # dp1 show-discdds-fill -o $out/dp-show-discdds-fill -v 0.5 dpx1
        context.subtask(DPShowFill, min_visibility=0.5, discdds='sym-dpx1-80')
        # dp1 show-discdds-fill -o $out/dp-show-discdds-fill --collapse_threshold 0.5 -v 0.5 dtx1
        context.subtask(DPShowFill, min_visibility=0.5, discdds='sym-dtx1-80', collapse_threshold=0.5) 
        # dp1 show-discdds-fill -o $out/dp-show-discdds-fill -v 0.5 dcl4r80
        context.subtask(DPShowFill, min_visibility=0.5, discdds=dds_cl, collapse_threshold=0.5)
        
        context.subtask(DPShowFill, min_visibility=0.5, discdds='sym-dpx3-80')
        context.subtask(DPShowFill, min_visibility=0.5, discdds='sym-dptcam3-80')
        
        c_planning = context.child('planning')

        alltestcases = []
        for delay in range(1, 13):
            # XXX: I didn't want to change the name in the configuration
            pattern = 'tc_h1orbit-pt256-80-n35s_d%d' % (delay) + '_%03d'
            tcs = c_planning.subtask(DPLogCases, stream=stream, pattern=pattern,
                               dds=dds_orbit, delay=delay)
            alltestcases.extend(tcs)
            
#             for id_tc in id_tc2job:
#                 testcases = get_conftools_testcases()
#                 testcases.add_spec(id_tc, 'generated', ['', {}])
                
        c_planning.checkpoint('testcases')
        
#         nice -n 10 dp batch -o out.tr1/dp-batch tr1_orbit_r80 -c "parmake n=6"
#         nice -n 10 dp batch -o out.tr1/dp-batch tr1_park_r80    -c "parmake n=4"
#         nice -n 10 dp batch -o out.tr1/dp-batch tr1_park_r128    -c "parmake n=4"
        batches = ['tr1_orbit_r80', 'tr1_park_r80', 'tr1_park_r128']
        c_planning.subtask(DPBatch, batches=",".join(batches), alltestcases=alltestcases)


