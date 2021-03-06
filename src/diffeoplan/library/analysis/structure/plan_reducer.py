from collections import defaultdict, deque
from contracts import contract
from diffeoplan import logger
from diffeoplan.library import dp_memoize_instance
from geometry import formatm
import numpy as np
import warnings
from diffeo2s.utils import iterate_indices
warnings.warn('check it was the same')

# from diffeoplan.utils import memoize_instance as memoize

__all__ = ['PlanReducer']


class PlanReducer(object):
    
    def __init__(self):
        # all actions
        self._all_actions = set()
        self._null = set()  # a
        self._commutes = set()  # (a1,a2)
        self._inverse = set()  # (a1,a2)
        self._inverse_for = defaultdict(set)
        self._same = defaultdict(set) 
        
    def set_null(self, a):
        self._all_actions.add(a)
        self._null.add(a) 
        
    def set_commute(self, a, b):
        self._all_actions.add(a)
        self._all_actions.add(b)
        self._commutes.add((a, b))    
        self._commutes.add((b, a))

    def set_inverse(self, a, b):
        self._all_actions.add(a)
        self._all_actions.add(b)
        self._inverse.add((a, b)) 
        self._inverse_for[a].add(b)   
        self._inverse_for[b].add(a)

    def set_same(self, a, b):
        self._all_actions.add(a)
        self._all_actions.add(b)
        self._same[a].add(b)    
        self._same[b].add(a)

    
    @contract(returns='list(tuple(int,int))')
    def get_inverse_pairs(self):
        """ Returns all pairs of inverses. """
        # XXX: this has several assumptions to be worked out
        seen = set()
        res = []
        for a in self._all_actions:
            if a in seen:
                continue
            inverses = self._inverse_for[a]
            inverse = min(inverses)
            res.append((a, inverse))
            seen.add(a)
            seen.update(inverses)
        return res
        
    def null(self, a):
        return a in self._null

    def commute(self, a, b):
        return (a, b) in self._commutes    

    def inverse(self, a, b):
        return (a, b) in self._inverse
    
    def same(self, a, b):
        return (a, b) in self._inverse
    
    @staticmethod
    @contract(labels='seq[N]')
    def dummy(labels):
        n = len(labels)
        print n, labels
        commute = np.eye(n).astype('bool')
        inverse = np.zeros((n, n)).astype('bool')
        same = np.eye(n).astype('bool')
        return PlanReducer.from_matrices(labels, commute, inverse, same)

    @staticmethod
    @contract(labels='seq[N]',
              commute='array[NxN](bool)',
              inverse='array[NxN](bool)',
              same='array[NxN](bool)')
    def from_matrices(labels, commute, inverse, same):
        logger.info('Creating PlanReducer from matrices:\n' + 
                    formatm('same', same, 'oppo', inverse, 'swap', commute))
        pr = PlanReducer()
        for i, j in iterate_indices(commute.shape):
            li = labels[i]
            lj = labels[j]
            if commute[i, j]:
                assert commute[j, i]
                pr.set_commute(li, lj)
        
            if same[i, j]:
                assert same[j, i]
                pr.set_same(li, lj)

            if inverse[i, j]:
                assert inverse[j, i]
                pr.set_inverse(li, lj)
        return pr
        
    def action_has_inverse(self, action):
        """ Returns true if the action has an inverse """
        return len(self._inverse_for[action]) == 0
    
    def action_get_inverse(self, action):
        return min(list(self._inverse_for[action]))
    
    
    @dp_memoize_instance 
    @contract(plan='tuple', returns='tuple')
    def get_canonical(self, plan):
        def log(s):
            # print(s)
            pass
   
        current = list()
        remaining = deque(plan)
        while remaining:
            log('- %s %s' % (current, remaining))
            # get a new action
            new_action = remaining.popleft()
            # if possible to do something...
            if current:
                prev_action = current[-1]
                # if they cancel each other
                if self.inverse(prev_action, new_action):
                    log('canceling %s %s' % (prev_action, new_action))
                    # remove the current one
                    current.pop()
                    continue
                elif prev_action != new_action and self.commute(prev_action, new_action):
                    log('commuting actions %s %s' % (prev_action, new_action))
                    # would changing the order make the plan shorter?
                    changed_order = tuple(current[:-1]) + (new_action,)
                    if_changed = self.get_canonical(changed_order)
                    log(' changing order %s -> %s ' % (changed_order, if_changed))
                    if len(if_changed) < len(current):
                        log(' if_changed would be shorter')
                        current = list(if_changed)
                        remaining.appendleft(prev_action)
                    else:
                        # if they commute and the length is the same
                        # then we put them in order
                        # So that (1,0,0) -> (0,0,1) assuming 0 and 1 commute
                        if new_action < prev_action:
                            # they are not in the right order
                            # now, of course, we put them both in the stack
                            # because there might be other changes to do
                            current.pop()
                            remaining.appendleft(prev_action)
                            remaining.appendleft(new_action)
                        else:
                            # they are already in order
                            current.append(new_action) 
                else:
                    current.append(new_action)
            else:
                # put it on current
                current.append(new_action)
                
        return tuple(current)
        
 
