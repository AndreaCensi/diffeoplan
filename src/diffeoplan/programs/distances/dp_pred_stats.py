from boot_agents.utils import scale_score
from contracts import contract
from diffeo2dds import (UncertainImage, get_conftools_discdds,
    get_conftools_uncertain_image_distances)
from diffeo2dds_learn import get_conftools_streams
from diffeoplan.programs.distances.dp_dist_stats import (dp_predstats_fig,
    create_subsets, fancy_error_display, legend_put_below)
from diffeoplan.programs.main import DP
from geometry.utils import assert_allclose
from itertools import chain, starmap, islice, cycle
from quickapp import CompmakeContext, iterate_context_names
from quickapp.quick_app import QuickApp
from reprep import Report
from reprep.plot_utils import ieee_spines
from reprep.report_utils import StoreResults
import numpy as np
import warnings
from diffeoplan.programs.logcases.makelogcases import iterate_testcases
warnings.warn('dependency on boot_agents')


__all__ = ['DPPredStats']


class DPPredStats(DP.get_sub(), QuickApp):
    """ Computes prediction performances for different DDS. """

    cmd = 'pred-stats'
    usage = 'pred-stats -d <distances> -s <streams> --dds discdds'

    def define_options(self, params):
        params.add_string('distances', default='*', short='d',
                          help="Comma-separated list of distances.")
        params.add_string('dds', short='S',
                          help="Comma-separated list of diffeosystems.")
        params.add_string('streams', default='*', short='s',
                          help="Comma-separated list of streams. Can use *.")
        
    def define_jobs_context(self, context):
        distances_library = get_conftools_uncertain_image_distances()
        distances = distances_library.expand_names(self.options.distances)
        
        streams_library = get_conftools_streams()
        streams = streams_library.expand_names(self.options.streams)
       
        discdds_library = get_conftools_discdds()
        discdds = discdds_library.expand_names(self.options.dds)
       
        for c, id_discdds in iterate_context_names(context, discdds):
            create_predstats_jobs(context=c, distances=distances,
                              id_discdds=id_discdds,
                              streams=streams, maxd=10)
        
        
@contract(context=CompmakeContext, distances='list(str)',
          streams='list(str)', id_discdds='str', maxd='int,>=1')
def create_predstats_jobs(context, distances, streams, id_discdds, maxd):
    # Compmake storage for results
    store = StoreResults()
    
    # Try to instance it 
    # dds = config.discdds.instance(id_discdds) 
    
    for delta in range(1, maxd):
        for i, id_stream in enumerate(streams):
            key = dict(delta=delta, id_stream=id_stream, id_discdds=id_discdds)
            job_id = 'pred-%s-log%s-delta%s' % (id_discdds, i, delta)
            
            store[key] = context.comp_config(compute_predstats,
                                            id_discdds,
                                            id_stream, delta, distances,
                                            job_id=job_id)
     
    subsets = create_subsets(distances)
    job_report_one(context, subsets, id_discdds, store)
    

def job_report_one(context, subsets, id_discdds, store):
    records = context.comp(make_records, store)
    for id_subset, distances in subsets.items():
        job_id = 'report_predstats-%s-%s' % (id_discdds, id_subset)    
        report = context.comp_config(report_predstats,
                                     id_discdds, id_subset, distances, records,
                                     job_id=job_id)
        context.add_report(report, 'predstats', id_discdds=id_discdds, subset=id_subset)
            
            
            
def make_records(results):
     
    def make_array(key, distances):
        dtype = [('delta', 'int'),
                 ('id_stream', 'S64')]
        dtype += list(distances[0].dtype.descr)
        dtype = np.dtype(dtype)
        for distance in distances:
            fields = [key['delta'], key['id_stream']]
            fields += map(lambda x: float(distance[x]), distance.dtype.fields)
            
            yield np.array(tuple(fields), dtype=dtype)

    records = chain.from_iterable(starmap(make_array, results.items()))
    records = list(records)
    records = np.hstack(records)
    return records


def report_predstats(id_discdds, id_subset, id_distances, records):
    r = Report('predistats-%s-%s' % (id_discdds, id_subset))
    
    r.data('records', records)
    f = r.figure()
    
    colors = list(islice(cycle(['r', 'g', 'b', 'k', 'y', 'm']), 50))
    delta = records['delta']
    W = 0.2

    # Save the raw values
    for i, id_d in enumerate(id_distances):
        r.data(id_d, records[id_d])
    
    with f.plot('values_order', **dp_predstats_fig) as pylab:
        ax = pylab.subplot(111)

        for i, id_d in enumerate(id_distances):
            distance = records[id_d]
            distance_order = scale_score(distance) / (float(distance.size) - 1)
            
            step = float(i) / max(len(id_distances) - 1, 1)
            xstep = W * 2 * (step - 0.5) 
            fancy_error_display(ax, delta + xstep, distance_order,
                                colors[i], perc=10, label=id_d)
            
        ieee_spines(pylab)    
        ticks = sorted(list(set(list(delta))))
        pylab.xlabel('interval length')
        pylab.ylabel('normalized distance')
        pylab.xticks(ticks, ticks)
        pylab.yticks((0, 1), (0, 1))
        pylab.axis((0.5, 0.5 + np.max(delta), -0.024, 1.2))
        legend_put_below(ax)

    with f.plot('values', **dp_predstats_fig) as pylab:
        ax = pylab.subplot(111)

        for i, id_d in enumerate(id_distances):
            distance = records[id_d]
            
            step = float(i) / max(len(id_distances) - 1, 1)
            xstep = W * 2 * (step - 0.5) 
            fancy_error_display(ax, delta + xstep, distance,
                                colors[i], perc=10, label=id_d)
            
        ieee_spines(pylab)    
        ticks = sorted(list(set(list(delta))))
        pylab.xlabel('interval length')
        pylab.ylabel('distance')
        pylab.xticks(ticks, ticks)
#        pylab.yticks((0, 1), (0, 1))
        a = pylab.axis()
        pylab.axis((0.5, 0.5 + np.max(delta), -0.024, a[3]))
        legend_put_below(ax)

    return r
     
def compute_predstats(id_discdds, id_stream, delta, id_distances):
    dds = get_conftools_discdds().instance(id_discdds)
    stream = get_conftools_streams().instance(id_stream)
    distances_library = get_conftools_uncertain_image_distances()
    distances = dict(map(lambda x: (x, distances_library.instance(x)), id_distances))
    dtype = [(x, 'float32') for x in id_distances]
    
    results = []
    for logitem in iterate_testcases(stream.read_all(), delta):
        assert_allclose(len(logitem.u), delta)
        y0 = UncertainImage(logitem.y0)
        y1 = UncertainImage(logitem.y1)
        py0 = dds.predict(y0, dds.commands_to_indices(logitem.u))
        ds = []
        for name in id_distances:
            d = distances[name].distance(y1, py0)
            #  d0 = distances[name].distance(y1, y0)
            ds.append(d)
        
        a = np.array(tuple(ds), dtype=dtype)
        results.append(a)
        
    return results


        
