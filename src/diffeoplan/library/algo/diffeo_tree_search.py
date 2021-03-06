from contracts import contract
from diffeo2dds import DiffeoAction, DiffeoSystem
from diffeo2dds.visualization import guess_state_space
from diffeoplan.library import Memoized
from diffeoplan.library.analysis.structure.plan_reducer import PlanReducer
from diffeoplan.utils import WithInternalLog
from ggs import GenericGraphSearch
import collections
import networkx as nx
import numpy as np


__all__ = ['DiffeoTreeSearch']

class DiffeoTreeSearch(GenericGraphSearch, WithInternalLog, Memoized):
    """
        A search tree whose nodes are plans, edges are actions,
        and that already knows:
        - that some plans are equivalent (modulo canonization by planreducer)
        - (to write)
        
    """
    @contract(id_dds='str', dds=DiffeoSystem,
              plan_reducer=PlanReducer, max_depth='int,>=0', max_iterations='int,>=0')
    def __init__(self, id_dds, dds, plan_reducer, max_depth=1000, max_iterations=1000000):
        self.id_dds = id_dds
        self.dds = dds
        self.plan_reducer = plan_reducer
        self.max_iterations = max_iterations
        self.max_depth = max_depth
        self.min_visibility = 0
        Memoized.__init__(self)
        GenericGraphSearch.__init__(self)
        WithInternalLog.__init__(self)
        
    @contract(min_visibility='>=0')
    def set_min_visibility(self, min_visibility):
        """ Set the minimum allowed visibility for nodes to be expanded. """
        self.info('Minimum visibility set to %s.' % min_visibility)
        self.min_visibility = min_visibility
        
    def __str__(self):
        return 'DiffeoTreeSearch'

    def node_friendly(self, plan):
        return self.dds.plan_friendly_labels(plan)
    
    @contract(node='tuple,seq(int)')    
    def next_node(self, node, action):
        child = node + (action,)
        return tuple(self.plan_reducer.get_canonical(child))
    
    def available_actions(self, node):
        
        if len(node) >= self.max_depth:
            self.log_node_too_deep(node)
            return []
        
        if self.iterations >= self.max_iterations:
            self.log_too_many_iterations(node)
            return []
        
        if self.min_visibility > 0:
            # Check this node has minimum visibility
            if self.visibility(node) < self.min_visibility:
                self.log_too_small_visibility(node)
                return [] 
            
        nactions = len(self.dds.actions)
        return range(nactions)
    
    @Memoized.dec()
    def visibility(self, plan):
        """ Returns a rough measure of preserved visibility. """
        action = self.plan2action(plan)
        d = action.get_diffeo2d_forward()
        v = d.get_visibility()
        return v

    @Memoized.dec()
    @contract(plan='tuple', returns=DiffeoAction)
    def plan2action(self, plan):
        if len(plan) == 0:
            shape = self.dds.actions[0].diffeo.get_shape()
            identity_cmd = np.array([0, 0])
            return DiffeoAction.identity('id', shape, identity_cmd)  # XXX
        
        last = self.dds.actions[plan[-1]]
        if len(plan) == 1:
            return last
        else:
            rest = self.plan2action(plan[:-1])
            return DiffeoAction.compose(last, rest)
          
    # TODO: move away visualization
    def plot_graph_using_guessed_statespace(self, pylab,  # @UnusedVariable
            plan2color=None, plan2label=None, cmap=None, origin=None, show_plan=None):
        ss = guess_state_space(self.id_dds, self.dds) 
        
        def plan2xy(plan):
            commands = self.dds.indices_to_commands(plan)
            state = ss.state_from_commands(commands, start=origin)
            xy = ss.xy_from_state(state)
            return 5 * xy
       
        if show_plan is not None:
            points = []
            for i in range(len(show_plan)):
                partial = show_plan[:i]
                points.append(plan2xy(partial))
            points = np.array(points).T
            pylab.plot(points[0], points[1], 'r-')
       
        if plan2color is None:
            plan2color = lambda plan: [0, 0, 0]  # @UnusedVariable
        if plan2label is None:
            plan2label = lambda plan: ''  # @UnusedVariable
        
        nodes = list(self.G.nodes())
         
        pos = dict((n, plan2xy(n)) for n in nodes)
        all_positions = map(tuple, pos.values())
        node_color = map(plan2color, nodes) 
        labels = dict((n, plan2label(n)) for n in self.G)
        
        if False:
            if len(all_positions) != len(set(all_positions)):
                print('Warning, overlapping nodes')
                y = collections.Counter(all_positions)
                for p, num in y.items():
                    if num > 1:
                        print('- %d for %s' % (num, p))
                        for node, node_pos in pos.items():
                            if tuple(node_pos) == p:
                                print('  - %s ' % str(node))

        nx.draw_networkx(self.G, with_labels=True, pos=pos, labels=labels,
                        node_color=node_color, cmap=cmap)
    
    def log_chosen(self, node):
        self.info('%6d closed %6d open | chosen %s' % 
                  (self.get_num_closed(),
                   self.get_num_open(),
                   self.node_friendly(node)))
    
    def log_actionless_node(self, node):
        self.info('No actions available for %s' % self.node_friendly(node))

    def log_child_discarded(self, node, action, child, matches):  # @UnusedVariable
        self.info('%s->%s but discarded' % (self.node_friendly(node),
                                              self.node_friendly(child)))
        
    def log_child_equivalent_found(self, node, action, child, match):  # @UnusedVariable
        self.info('%s->%s but equivalent found (%s)' % 
                  (self.node_friendly(node),
                   self.node_friendly(child),
                   self.node_friendly(match)))
 
    def log_node_too_deep(self, node):
        self.info('Node %s is too deep. (%s)' % (self.node_friendly(node),
                                                 self.max_depth))

    def log_too_many_iterations(self, node):  # @UnusedVariable
        self.info('Cutting because iterations = %s' % self.iterations)

    def log_too_small_visibility(self, node):
        self.info('Not expanding %s because of visibility %s < %s' % 
                  (self.node_friendly(node), self.visibility(node),
                   self.min_visibility))
        
