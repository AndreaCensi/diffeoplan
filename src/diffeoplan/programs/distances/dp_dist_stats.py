from boot_agents.utils import scale_score
from bootstrapping_olympics.utils import natsorted
from contracts import contract
from diffeo2dds import get_conftools_uncertain_image_distances
from diffeo2dds.model.uncertain_image import UncertainImage
from diffeo2dds_learn import get_conftools_streams
from diffeoplan import logger
from diffeoplan.programs import DP
from geometry.utils import assert_allclose
from itertools import chain, starmap, islice, cycle, ifilterfalse
from quickapp import CompmakeContext, QuickApp
from reprep import Report
from reprep.plot_utils import ieee_spines
from reprep.report_utils import StoreResults
import numpy as np
from diffeoplan.programs.logcases.makelogcases import iterate_testcases

__all__ = ['DPDistStats']

class DPDistStats(DP.get_sub(), QuickApp):
    """ Computes statistics for images distances for different plan steps. """

    cmd = 'dist-stats'
    usage = 'dist-stats  -d <distances> -t <testcases>'

    def define_options(self, params):
        params.add_string('distances', default='*', short='d',
                          help="Comma-separated list of distances. Can use *.")
        params.add_string('streams', default='*', short='t',
                          help="Comma-separated list of streams. Can use *.")
        params.add_int('maxd', default=10,
                          help="Maximum interval")
        
    def define_jobs_context(self, context):
        
        distances_library = get_conftools_uncertain_image_distances()
        distances = distances_library.expand_names(self.options.distances)
        distances = natsorted(distances)
        
        streams_library = get_conftools_streams()
        streams = streams_library.expand_names(self.options.streams)
        streams = natsorted(streams)
        # id_comb = ','.join(streams) + '-' + ','.join(distances)

        create_diststats_jobs(context, distances=distances, streams=streams,
                              maxd=self.options.maxd)
       
       
@contract(context=CompmakeContext, distances='list(str)', streams='list(str)',
          maxd='int,>=1')
def create_diststats_jobs(context, distances, streams, maxd):
    # Compmake storage for results
    store = StoreResults()

    for id_distance in distances:    
        for delta in range(1, maxd):
            for i, id_stream in enumerate(streams):
                key = dict(id_distance=id_distance,
                           delta=delta,
                           stream=id_stream)
                job_id = '%s-log%s-delta%s' % (id_distance, i, delta)
                
                store[key] = context.comp_config(compute_dist_stats, id_distance,
                                  id_stream, delta,
                                  job_id=job_id)
    
    
    for id_distance in distances:
        subset = store.select(id_distance=id_distance)
        stats = context.comp(compute_statistics, subset)
        report = context.comp(report_statistics, id_distance, stats)
        context.add_report(report, 'bydistance', id_distance=id_distance)

    subsets = create_subsets(distances)
    
    job_report(context, subsets, store)

    
def create_subsets(distances):
    subsets = {}
    subsets['all'] = sorted(distances)
    for d in distances:
        subsets[d] = [d]
    
    prefix = lambda s: "".join(ifilterfalse(str.isdigit, s))
    initials = set(prefix(d) for d in distances)
    for initial in initials:
        which = filter(lambda x: prefix(x) == initial, distances)
        subsets[initial] = sorted(which)
    return subsets

@contract(context=CompmakeContext)
def job_report(context, subsets, store):
    for id_subset, which in subsets.items():
        logger.info('%s = %s' % (id_subset, which))
        subset = store.select(lambda x: x['id_distance'] in which)
        logger.info('selected %s' % len(subset))
        substats = context.comp(compute_statistics, subset, job_id='%s-s' % id_subset)
        report = context.comp(report_statistics_all, id_subset, substats)
        context.add_report(report, 'main', subset=id_subset)
            
    
# dp_predstats_fig = dict(figsize=(3.3, 1.5))
dp_predstats_fig = dict(figsize=(6.6, 3))
        
def report_statistics_all(id_sub, stats, perc=10, W=0.2):
    records = stats['records']

    r = Report('statsall-%s' % id_sub)
    r.data('records', records)
    f = r.figure()
    
    id_distances = sorted(set(records['id_distance']))
        
    logger.info('%s: %s %s reo %s' % (id_sub, len(stats), id_distances,
                                      len(records)))

    colors = list(islice(cycle(['r', 'g', 'b', 'k', 'y', 'm']), 50))
    

    with f.plot('distance_order', **dp_predstats_fig) as pylab:
        ax = pylab.subplot(111)
        for i, id_d in enumerate(id_distances):
            which = records['id_distance'] == id_d
            delta = records[which]['delta']
            distance = records[which]['distance']
            order = scale_score(distance)
            order = order / float(order.size)

            
            step = float(i) / (max(len(id_distances) - 1, 1))
            xstep = W * 2 * (step - 0.5) 
            fancy_error_display(ax, delta + xstep, order,
                                colors[i], perc=perc, label=id_d)
            
        ieee_spines(pylab)    
        ticks = sorted(list(set(list(delta))))
        pylab.xlabel('plan length')
        pylab.ylabel('normalized distance')
        pylab.xticks(ticks, ticks)
        pylab.yticks((0, 1), (0, 1))
        pylab.axis((0.5, 0.5 + np.max(delta), -0.024, 1.2))
        legend_put_below(ax)

    with f.plot('distance', **dp_predstats_fig) as pylab:
        ax = pylab.subplot(111)
        for i, id_d in enumerate(id_distances):
            which = records['id_distance'] == id_d
            delta = records[which]['delta']
            distance = records[which]['distance']

            step = float(i) / max(len(id_distances) - 1, 1)
            xstep = W * 2 * (step - 0.5) 
            fancy_error_display(ax, delta + xstep, distance,
                                colors[i], perc=perc, label=id_d)
            
        ieee_spines(pylab)    
        ticks = sorted(list(set(list(delta))))
        pylab.xlabel('plan length')
        pylab.ylabel('distance')
        pylab.xticks(ticks, ticks)
#        pylab.yticks((0, 1), (0, 1))
        a = pylab.axis()
        pylab.axis((0.5, 0.5 + np.max(delta), -0.024, a[3]))
        legend_put_below(ax)

    return r

def report_statistics(id_sub, stats):
    records = stats['records']
    distance = records['distance']
    delta = records['delta']
    order = scale_score(distance)
    order = order / float(order.size)

    r = Report('stats-%s' % id_sub)
    r.data('records', records)
    f = r.figure()
    
    with f.plot('scatter') as pylab:
        pylab.scatter(delta, distance)
        pylab.xlabel('delta')
        pylab.ylabel('distance')
        pylab.axis((-1, np.max(delta) + 1, -0.05, np.max(distance)))
        
    with f.plot('with_stats', **dp_predstats_fig) as pylab:
        fancy_error_display(pylab, delta, distance, 'g')

    with f.plot('distance_order', **dp_predstats_fig) as pylab:
        fancy_error_display(pylab, delta, order, color='k')
        
    f = r.figure(cols=1)        
    bins = np.linspace(0, np.max(distance), 100)
    for i, d in enumerate(set(delta)):
        with f.plot('conditional%d' % i) as pylab:
            which = delta == d
            pylab.hist(distance[which], bins)

    return r

def fancy_error_display(pylab, xs, ys, color, perc=10, label=None):
    pylab.scatter(xs, ys, s=20, c=color, edgecolors='none', alpha=0.03,
                  rasterized=True)  # 0.01

    for i, x in enumerate(set(xs)):
        which = xs == x
        
        # only assign the label to the first one
        if i == 0:
            kwargs = dict(label=label)
        else:
            kwargs = dict()
        p = fancy_errorbar(pylab, x, ys[which], perc, fmt='o', ecolor=color,
                       mfc=color, mec=color, **kwargs)
    return p

def fancy_errorbar(pylab, x, ys, p, *args, **kwargs):
    y_mean = np.mean(ys)
    above = np.percentile(ys, 100 - p) - y_mean
    below = y_mean - np.percentile(ys, p) 
    yerr = np.vstack((-above, -below))
    
    p = pylab.errorbar(x, y_mean, yerr=yerr, *args, **kwargs)
    return p

def legend_put_below(ax, frac=0.1):
#    ax = pylab.gca()
    # Shink current axis's height by 10% on the bottom
    box = ax.get_position()
    ax.set_position([box.x0, box.y0 + box.height * frac,
                 box.width, box.height * (1 - frac)])

    # Put a legend below current axis
    ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1),
              fancybox=True, shadow=True, ncol=5)

#    ax.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)

def compute_statistics(results):
    
    def make_array(key, distances):
        for distance in distances:
            yield np.array(
                           (key['delta'], distance, key['id_distance']),
                           dtype=[('delta', 'int'),
                                  ('distance', 'float'),
                                  ('id_distance', 'S64')])
        

    records = chain.from_iterable(starmap(make_array, results.items()))
    records = np.hstack(list(records))
    stats = {}
    stats['records'] = records
    return stats

def compute_dist_stats(id_distance, id_stream, delta):
    distances_library = get_conftools_uncertain_image_distances()
    distance = distances_library.instance(id_distance)
    stream = get_conftools_streams().instance(id_stream)
    it = stream.read_all()
    results = []
    for logitem in iterate_testcases(it, delta):
        assert_allclose(len(logitem.u), delta)
        y0 = UncertainImage(logitem.y0)
        y1 = UncertainImage(logitem.y1)
        d = distance.distance(y0, y1)
        results.append(d)
        
    logger.info('%s: found %d of %d steps in %s' % 
                (id_distance, len(results), delta, id_stream))
    return results
        
        
        
