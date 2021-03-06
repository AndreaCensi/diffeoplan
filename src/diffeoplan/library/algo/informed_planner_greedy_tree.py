from .diffeo_tree_search_image_greedy_tree import (
    DiffeoTreeSearchImageGreedyTree)
from .informed_planner import InformedPlanner
from diffeo2dds import get_conftools_uncertain_image_distances

__all__ = ['InformedPlannerGreedyTree']


class InformedPlannerGreedyTree(InformedPlanner):

    def __init__(self, metric_attractor, **kwargs):
        distances = get_conftools_uncertain_image_distances()
        self.metric_attractor = distances.instance(metric_attractor)
        super(InformedPlannerGreedyTree, self).__init__(**kwargs)
        
    def plan_init(self, y0, y1):
        super(InformedPlannerGreedyTree, self).plan_init(y0, y1)
        self.start_tree.set_other_tree(self.goal_tree)
        self.goal_tree.set_other_tree(self.start_tree)

    def init_start_tree(self, y0):
        dts = DiffeoTreeSearchImageGreedyTree(metric_attractor=self.metric_attractor,
                                          image=y0,
                                          id_dds=self.id_dds,
                        dds=self.get_dds(), plan_reducer=self.get_plan_reducer(),
                        max_depth=self.max_depth, max_iterations=self.max_iterations,
                        metric_collapse=self.metric_collapse,
                        metric_collapse_threshold=self.metric_collapse_threshold)
        return dts
    
    def init_goal_tree(self, y1):
        dds = self.get_dds().inverse()  # <-- note inverse()
        if self.bidirectional:
            max_depth = self.max_depth
            max_iterations = self.max_iterations
        else:
            max_depth = 0  # do not expand anything
            max_iterations = 0  # do not expand anything
        dts = DiffeoTreeSearchImageGreedyTree(metric_attractor=self.metric_attractor,
                                          image=y1, id_dds=self.id_dds,
                        dds=dds, plan_reducer=self.get_plan_reducer(),
                        max_depth=max_depth, max_iterations=max_iterations,
                        metric_collapse=self.metric_collapse,
                        metric_collapse_threshold=self.metric_collapse_threshold)
        return dts
    
