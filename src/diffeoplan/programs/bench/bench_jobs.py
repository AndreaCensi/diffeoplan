from .bench import run_planning, run_planning_stats
from .tables import results2stats_dict, jobs_tables
from .visualization import visualize_result
from collections import defaultdict
from compmake import comp_stage_job_id
from contracts import contract
from diffeo2dds import get_conftools_discdds, get_conftools_uncertain_images
from diffeoplan import (get_conftools_testcases, get_conftools_planning_algos,
    get_dp_config)
from reprep import Report
from reprep.report_utils import StoreResults
import warnings


def create_bench_jobs(context, algos, testcases):
    # dict(id_algo, id_tc, id_discdds, plan_length) => PlanningResults
    allplanning = StoreResults()
    # dict(id_algo, id_tc, id_discdds, plan_length) => resultstats
    allruns = StoreResults() 
    # dict(id_algo, id_tc) => DiffeoPlanningAlgorithm
    algoinit = StoreResults()
    
    config = get_dp_config()
    
    # Let's instantiate all test cases and sort them by discdds
    # so that we do only one initialization per algorithms
    id_discdds2testcases = defaultdict(lambda: {}) 
    alltc = {}  # id -> Promise TestCase
    for id_tc in testcases:
        alltc[id_tc] = context.comp(instantiate_testcase, id_tc)
        # Do it once, now, to get its dds
        tc1 = config.testcases.instance(id_tc) 
        id_discdds2testcases[tc1.id_discdds][id_tc] = tc1
    
    # Load discdds before, they might be automatically generated
    # as well so we want the generation to happen only once.
    discdds = {}  # id -> Promise DiffeoSystem
    for id_discdds in id_discdds2testcases: 
        discdds[id_discdds] = context.comp(instantiate_discdds, id_discdds)
        
    # for each algorithm
    for id_algo in algos:
        config.algos[id_algo]  # check it is in the configuration
            
        # for each dynamics
        for id_discdds, dds in discdds.items():
            job_id = 'init-%s-%s' % (id_algo, id_discdds)
            
            # initialize the algorithm for that dynamics
            algo = context.comp(init_algorithm, id_algo, id_discdds, discdds[id_discdds], job_id=job_id)
            algoinit[dict(id_algo=id_algo, id_discdds=id_discdds)] = algo
            
            # for each test case in that dynamics
            for id_tc, tc in id_discdds2testcases[id_discdds].items():
                
                # run the planning
                job_id = 'plan-%s-%s' % (id_algo, id_tc)
                result = context.comp(run_planning, id_algo,
                              id_tc, alltc[id_tc], algo, job_id=job_id)
                
                # compute statistics
                result_stats = context.comp(run_planning_stats, result,
                                    dds, alltc[id_tc],
                                    job_id=job_id + '-stats') 
    
                attrs = dict(id_algo=id_algo, id_tc=id_tc,
                             id_discdds=tc.id_discdds,
                             true_plan_length=len(tc.true_plan))
                allruns[attrs] = result_stats
                allplanning[attrs] = result
    
    jobs_report_algo_init(context, algoinit)
    jobs_report_tc(context, testcases, alltc)
    jobs_report_dds(context, discdds)

    allstats = StoreResults()
    for key, run in allruns.items():
        allstats[key] = context.comp(results2stats_dict, run,
                             job_id=comp_stage_job_id(run, 'statsdict'))

    jobs_tables(context, allstats)
    jobs_visualization(context, allruns)
    
    

def instantiate_discdds(id_discdds):
    warnings.warn('make sure it it called with comp_config')
    return get_conftools_discdds().instance(id_discdds)

def instantiate_testcase(id_tc):
    warnings.warn('make sure it it called with comp_config')
    return get_conftools_testcases().instance(id_tc)

def jobs_report_tc(context, testcases, alltc):
    for id_tc in testcases:
        tc = get_conftools_testcases().instance(id_tc)
        report = context.comp_config(report_tc, id_tc, alltc[id_tc],
                      job_id='report_tc-%s' % id_tc)
        report_attrs = dict(true_plan_length=len(tc.true_plan),
                            id_tc=id_tc, id_discdds=tc.id_discdds)
        context.add_report(report, 'tc', **report_attrs)

def jobs_report_dds(context, discdds):
    for id_discdds, dds in discdds.items():
        report = context.comp(report_dds, id_discdds, dds,
                      job_id='report_dds-%s' % id_discdds)
        context.add_report(report, 'dds', id_discdds=id_discdds)
        
def jobs_report_algo_init(context, algoinit):  # @UnusedVariable
    """ add the initialization report for each algorithm """
    for k, algo in algoinit.items():
        id_algo = k['id_algo'] 
        id_discdds = k['id_discdds']
        job_id = 'init-%s-%s-report' % (id_algo, id_discdds)
        report = context.comp(report_init_algorithm, id_algo, id_discdds, algo,
                      job_id=job_id)
        report_attrs = dict(id_algo=id_algo, id_discdds=id_discdds)
        context.add_report(report, 'init', **report_attrs)
        

def jobs_visualization(context, allruns):
    for run in allruns:
        id_tc = run['id_tc']
        id_algo = run['id_algo']
        result = allruns[run]
        job_id = 'plan-%s-%s-visualize' % (id_algo, id_tc)
        report = context.comp_config(visualize_result, id_tc, id_algo,
                      result, job_id=job_id)
        report_attrs = run
        context.add(report, 'visualization', **report_attrs)


def init_algorithm(id_algo, id_discdds, discdds):
    """ Returns the instanced DiffeoPlanninAlgorithm """
    warnings.warn('make sure it it called with comp_config')
    algo = get_conftools_planning_algos().instance(id_algo)    
    # initialize the algorithm with the dynamics
    # TODO: add computation time
    # t0 = time.clock()
    algo.set_name_for_log(id_algo)
    algo.init(id_discdds, discdds) 
    # init_time = time.clock() - t0
    return algo


@contract(returns=Report)
def report_init_algorithm(id_algo, id_discdds, algo):
    """ Creates a report for the initialization phase of the algorithm """
    r = Report('init-%s-%s' % (id_algo, id_discdds)) 
    algo.init_report(r)
    return r

    
@contract(returns=Report)
def report_tc(id_tc, tc):
    warnings.warn('make sure it it called with comp_config')
    r = Report('tc-%s' % (id_tc))
    tc.display(r)
    return r


@contract(returns=Report)
def report_dds(id_discdds, discdds, image='lena'):
    warnings.warn('make sure it it called with comp_config')
    r = Report('dds-%s' % (id_discdds))
    y0 = get_conftools_uncertain_images().instance(image)
    discdds.display(r, y0)
    return r


