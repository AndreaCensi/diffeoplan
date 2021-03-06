from contracts import contract
from diffeo2dds import DiffeoSystem, UncertainImage
from diffeoplan import DiffeoPlanningAlgo, PlanningResult, get_dp_config, logger
import numpy as np
import time

__all__ = ['SamplePlanner']


class SamplePlanner(DiffeoPlanningAlgo):
    """ A sample based planner. """
    
    def __init__(self, plan_time, plan_max_length, metric_goal):
        logger.info('initiating sampleplanner')
        print('pr: initiating sampleplanner')
        DiffeoPlanningAlgo.__init__(self)
        config = get_dp_config()
        
        self.metric_goal = config.distances.instance(metric_goal)
        self.plan_time = plan_time
        self.max_length = plan_max_length
        logger.info('done')
        print('pr: done')
        
    @contract(dds=DiffeoSystem)
    def init(self, id_dds, dds):
        """ Might be redefined to add precomputation. """
        self.info('Initialized with dds %r' % id_dds) 
        self._dds = dds
        self.id_dds = id_dds
        print('Starting to compute ComposedGraphs')
        self.composed_dds = ComposeGraph(id_dds, self.max_length)
    

    @contract(y0=UncertainImage, y1=UncertainImage,
              returns=PlanningResult)
    def plan(self, y0, y1, precision=None, min_visibility=None):
        """ 
            This must return an instance of PlanningResult.
        """
        time0 = time.time()
        num = len(self.composed_dds.composed_actions)
        unevaled = range(num)
        evaled = []
        min_dist = self.metric_goal.distance(y0, y1)
        best_action = None
        while(time.time() - time0 < self.plan_time):
            if len(unevaled) == 0:
                logger.info('Search done after %g evaluations' % len(evaled))
                break
            
            i = unevaled[np.random.randint(len(unevaled))]
            ypi = self.composed_dds.composed_actions[i].predict(y0)
            di = self.metric_goal.distance(ypi, y1)
            
            if min_dist > di:
                
                min_dist = di
                best_action = i
            
            unevaled.remove(i)
            evaled.append(i)
        if best_action is None:
            plan = ()
        else:
            plan = self.composed_dds.plan_reduced[best_action]
        logger.info('Plan output: ' + str(plan))
        logger.info('predicted distance for plan: ' + str(min_dist))
        
        return PlanningResult(success=True, plan=plan,
                              status=(str(len(evaled)) + 'of' + str(num) + 
                                      ' evaluated'))


